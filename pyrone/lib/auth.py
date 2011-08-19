"""
Authentication and authorization functions
"""
import logging

#import pyramid.threadlocal as threadlocal
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implements
#from pylons.controllers.util import abort, redirect
from decorator import decorator

from pyrone.models.user import anonymous as anonymous_user

log = logging.getLogger(__name__)

def principals_finder(user, request):
    principals = user.get_permissions()
    return principals

def get_user(request):
    if 'user' in request.session:
        return request.session['user']
    else:
        return anonymous_user
    
def has_permission(request, p):
    get_user(request).has_permission(p)
    
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
        user = request.session.get(self.user_key)
        if user is not None and user.id == userid:
            return user.get_permissions()
        
    def __init__(self):
        self.user_key = 'user'
        #self.logout_token_key = 'user.logout_token'

    def remember(self, request, userid, **kw):
        """ Ignore userid and user kw argument ``user`` """
        request.session[self.user_key] = kw['user']
        #request.session[self.logout_token_key] = str(uuid.uuid4())
        request.session.save()
        return []
    
    def forget(self, request):
        """ Remove user from the session """
        if self.user_key in request.session:
            del request.session[self.user_key]
            #del request.session[self.logout_token_key]
            request.session.save()
        return []

    def unauthenticated_userid(self, request):
        user = request.session.get(self.user_key)
        if user is not None:
            return user.id
    