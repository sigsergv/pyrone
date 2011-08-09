"""
Authentication and authorization functions
"""
import logging

#from pylons.controllers.util import abort, redirect
from decorator import decorator

log = logging.getLogger(__name__)

def get_user():
    if 'user' in s:
        return s['user']
    else:
        return None
    
def has_permission(p):
    user = get_user()
    if user is None:
        return False
    else:
        return user.has_permission(p)
    
def get_logout_token():
    logout_token = '';
    if 'logout_token' in s:
        logout_token = s['logout_token']

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