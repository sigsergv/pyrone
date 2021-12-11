from pyramid.authentication import AuthTktCookieHelper
from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.request import RequestLocalCache

from pyrone.models.user import anonymous as anonymous_user, get_user as get_user_by_id


class MySecurityPolicy:
    def __init__(self, secret):
        self.authtkt = AuthTktCookieHelper(secret)
        self.identity_cache = RequestLocalCache(self.load_identity)

    def load_identity(self, request):
        identity = self.authtkt.identify(request)
        if identity is None:
            return None

        userid = identity['userid']
        user = get_user_by_id(request, userid)
        return user

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        user = self.identity(request)
        if user is not None:
            return user.id

    def remember(self, request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.authtkt.forget(request, **kw)


def includeme(config):
    settings = config.get_settings()

    # config.set_csrf_storage_policy(CookieCSRFStoragePolicy())
    # config.set_default_csrf_options(require_csrf=True)
    
    config.set_security_policy(MySecurityPolicy(settings['pyrone.auth_secret']))