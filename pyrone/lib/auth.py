"""
Authentication and authorization functions
"""
import logging
import hashlib

#import pyramid.threadlocal as threadlocal
from pyramid.security import unauthenticated_userid
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implementer
#from pylons.controllers.util import abort, redirect

from pyrone.models.user import anonymous as anonymous_user, get_user as get_user_by_id

log = logging.getLogger(__name__)

SESSION_USER_KEY = 'user'


def md5(s):
    return hashlib.md5(s).hexdigest()


def sha1(s):
    return hashlib.sha1(s).hexdigest()


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


def get_logout_token(request):
    s = request.session
    logout_token = ''
    if 'user.logout_token' in s:
        logout_token = s['user.logout_token']

    return logout_token


@implementer(IAuthenticationPolicy)
class PyroneSessionAuthenticationPolicy(CallbackAuthenticationPolicy):

    def callback(self, userid, request):
        user = request.session.get(SESSION_USER_KEY)
        if user is not None and user.id == userid:
            roles = ['role:{0}'.format(x) for x in user.get_roles()]
            return roles

    def remember(self, request, userid, user=None, **kw):
        request.session[SESSION_USER_KEY] = user
        request.session.save()
        return []

    def forget(self, request):
        """ Remove user from the session """
        if SESSION_USER_KEY in request.session:
            del request.session[SESSION_USER_KEY]
            request.session.save()
        return []

    def unauthenticated_userid(self, request):
        user = request.session.get(SESSION_USER_KEY)
        if user is not None:
            return user.id
