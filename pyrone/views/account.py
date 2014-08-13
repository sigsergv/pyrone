import logging
import transaction
import hashlib
import random
import urllib

from twitter import Twitter, OAuth
from twitter.api import TwitterHTTPError
from sqlalchemy.orm import joinedload
from pyramid.i18n import TranslationString as _
from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPServerError

from pyrone.models import DBSession
from pyrone.models import User
from pyrone.models.user import find_local_user, find_twitter_user,\
    normalize_email, VerifiedEmail
from pyrone.models.config import get as get_config
from pyrone.lib.jsonhttpresponse import JSONResponse
from pyrone.lib import httpcode

log = logging.getLogger(__name__)


def md5(s):
    return hashlib.md5(s).hexdigest()


def sha1(s):
    return hashlib.sha1(s).hexdigest()


@view_config(route_name='account_login', renderer='/blog/local_login.mako')
def login_local(request):
    c = {'error': ''}

    if request.method == 'POST':
        # process login
        login = request.POST['login']
        password = request.POST['password']
        user = find_local_user(login, password)
        if user is None:
            c['error'] = _('Incorrect login or password')
        else:
            # this method doesn't return any headers actually
            user.detach()
            headers = remember(request, user.id, user=user)
            return HTTPFound(location=route_url('blog_latest', request), headers=headers)

    elif request.method == 'GET':
        log.debug(request.session)

    return c


@view_config(route_name='account_logout', request_method='POST')
def logout(request):
    # "forget" method is also doesn't return any headers
    headers = forget(request)
    # return to referer if possible
    referer = request.headers.get('Referer')
    if referer is None:
        referer = route_url('blog_latest', request)

    return HTTPFound(location=referer, headers=headers)


@view_config(route_name='account_my_profile', renderer='/blog/my_profile.mako', permission='authenticated')
def my_profile(request):
    c = {}

    return c


@view_config(route_name='account_save_my_profile_ajax', renderer='json', permission='authenticated', request_method='POST')
def my_profile_save_ajax(request):
    c = {}
    user_id = request.user.id

    is_changed = False

    dbsession = DBSession()
    user = dbsession.query(User).options(joinedload('roles')).get(user_id)

    if user is None:
        return JSONResponse(httpcode.BadRequest, c)

    if 'email' in request.POST:
        user.email = request.POST['email']
        is_changed = True

    if user.kind == 'local':
        if 'display_name' in request.POST:
            user.display_name = request.POST['display_name']
            is_changed = True
        if 'login' in request.POST:
            user.login = request.POST['login']
            is_changed = True

        if 'new_password' in request.POST and request.POST['new_password'] != '':
            # construct new password
            sample = '0123456789abcdef'
            salt = ''.join([random.choice(sample) for x in range(8)])

            user.password = salt + sha1(salt + sha1(request.POST['new_password']))
            is_changed = True

    if is_changed:
        dbsession.flush()
        user.detach()
        user.get_roles()
        # also update Beaker session object
        remember(request, None, user=user)
    else:
        return JSONResponse(httpcode.BadRequest, c)

    return c


@view_config(route_name='account_twitter_init', renderer='json')
def login_twitter_init(request):
    """
    Start twitter authentication: create OAuth request to twitter and pass url back to
    caller javascript
    """
    c = {'authorize_url': False}

    consumer_key = str(get_config('tw_consumer_key'))
    consumer_secret = str(get_config('tw_consumer_secret'))

    page_url = request.POST['page_url']
    callback_url = route_url('account_twitter_finish', request, _query=[('pyrone_url', page_url)])
    twitter = Twitter(auth=OAuth('', '', consumer_key, consumer_secret), format='', api_version=None)

    try:
        oauth_resp = twitter.oauth.request_token(oauth_callback=callback_url)
    except TwitterHTTPError as e:
        log.error('Invalid "request_token" request: {0}'.format(str(e)))
        return HTTPNotFound()

    oauth_resp_data = dict(urllib.parse.parse_qsl(oauth_resp))

    oauth_token = oauth_resp_data['oauth_token']
    oauth_token_secret = oauth_resp_data['oauth_token_secret']

    request.session['twitter_request_token'] = (oauth_token, oauth_token_secret)
    auth_url = 'https://twitter.com/oauth/authorize?{0}'.format(urllib.parse.urlencode({
        'oauth_token': oauth_token
        }))
    c['authorize_url'] = auth_url

    return c


@view_config(route_name='account_twitter_finish', renderer='json')
def login_twitter_finish(request):
    """
    Finish twitter authentication
    """
    consumer_key = str(get_config('tw_consumer_key'))
    consumer_secret = str(get_config('tw_consumer_secret'))
    token = request.session.get('twitter_request_token')
    twitter = Twitter(auth=OAuth(token[0], token[1], consumer_key, consumer_secret), format='', api_version=None)

    verifier = request.GET.get('oauth_verifier')
    try:
        oauth_resp = twitter.oauth.access_token(oauth_verifier=verifier)
    except TwitterHTTPError as e:
        log.error('Invalid "access_token" request: {0}'.format(str(e)))
        return HTTPNotFound()

    oauth_resp_data = dict(urllib.parse.parse_qsl(oauth_resp))
    # typical response:
    # {'user_id': '128607225', 'oauth_token_secret': 'NaGQrWyNRtHHHbvm3tNI0tcr2KTBUEY0J3ng8d7KFXg', 'screen_name': 'otmenych', 'oauth_token': '128607225-NWzT8YL1Wt6qNzMLzmaCEWOxqFtrEI1pjlA8c5FK'}
    tw_username = oauth_resp_data['screen_name']
    user = find_twitter_user(tw_username)

    if user is None:
        dbsession = DBSession()
        # create user
        user = User()
        user.kind = 'twitter'
        user.login = tw_username
        dbsession.add(user)

        # re-request again to correctly read roles
        user = find_twitter_user(tw_username)
        if user is None:
            log.error('Unable to create twitter user')
            return HTTPServerError()

    # save user to the session
    user.detach()
    remember(request, None, user=user)

    return HTTPFound(location=request.GET['pyrone_url'])


@view_config(route_name='account_verify_email', renderer='/blog/verify_email.mako')
def verify_email(request):
    c = {}

    fail = False
    try:
        email = normalize_email(request.GET['email'])
        verification_code = request.GET['token']
        dbsession = DBSession()
        vf = dbsession.query(VerifiedEmail).filter(VerifiedEmail.email == email).first()
        if vf is None or vf.verification_code != verification_code or vf.is_verified:
            fail = True
        else:
            vf.is_verified = True
    except KeyError:
        fail = True

    if fail:
        c['result'] = _('Verification failed: email not found.')
        return JSONResponse(httpcode.BadRequest, c)
    else:
        c['result'] = _('Email `{0}` has been confirmed.').format(email)

    return c


@view_config(context='pyramid.httpexceptions.HTTPNotFound', renderer='/404.mako')
def handler_404_not_found(request):
    return {}

@view_config(context='pyramid.httpexceptions.HTTPForbidden', renderer='/403.mako')
def handler_403_not_found(request):
    return {}
