"""
Authentication and authorization functions
"""
import logging

#import pyramid.threadlocal as threadlocal
from pyramid.security import unauthenticated_userid
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implements
#from pylons.controllers.util import abort, redirect
from decorator import decorator

from pyrone.models.user import anonymous as anonymous_user, get_user as get_user_by_id

log = logging.getLogger(__name__)

SESSION_USER_KEY = 'user'

def principals_finder(user, request):
    principals = user.get_permissions()
    return principals

def get_user(request):
    '''
    if 'user' in request.session:
        return request.session[SESSION_USER_KEY]
    else:
        return anonymous_user
    '''
    userid = unauthenticated_userid(request)
    if userid is not None:
        user = get_user_by_id(userid)
    else:
        user = anonymous_user

    return user
    
def has_permission(request, p):
    request.user.has_permission(p)
    
def get_logout_token(request):
    s = request.session
    logout_token = '';
    if 'user.logout_token' in s:
        logout_token = s['user.logout_token']

    return logout_token

def permissions_required(permissions):
    @decorator
    def d(g, self, *args, **kwargs):
        if self.user is None:
            abort(403)
        
        #log.debug(self._get_method_args())
        allow = True
        # make sure self.user has corresponding permissions
        for p in permissions:
            allow = allow and self.user.has_permission(p)
            if not allow:
                break
        if allow:
            return g(self, *args, **kwargs)
        else:
            abort(403)
    
    return d

@decorator
def auth_required(f, self, *args, **kwargs):
    if self.user is None:
        abort(403)
        
    return f(self, *args, **kwargs)

class PyroneSessionAuthenticationPolicy(CallbackAuthenticationPolicy):
    implements(IAuthenticationPolicy)
    
    def callback(self, userid, request):
        user = request.session.get(SESSION_USER_KEY)
        if user is not None and user.id == userid:
            return user.get_permissions()
        
    def remember(self, request, userid, user=None, **kw):
        request.session[SESSION_USER_KEY] = user
        #request.session[self.logout_token_key] = str(uuid.uuid4())
        request.session.save()
        return []
    
    def forget(self, request):
        """ Remove user from the session """
        if SESSION_USER_KEY in request.session:
            del request.session[SESSION_USER_KEY]
            #del request.session[self.logout_token_key]
            request.session.save()
        return []

    def unauthenticated_userid(self, request):
        user = request.session.get(SESSION_USER_KEY)
        if user is not None:
            return user.id
    