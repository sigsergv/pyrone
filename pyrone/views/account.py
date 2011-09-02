## -*- coding: utf-8 -*-
import logging
import transaction
import tweepy
import uuid

from hashlib import md5

from sqlalchemy.orm import eagerload
from pyramid.i18n import TranslationString as _
from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound, HTTPServerError

from pyrone.models import DBSession
from pyrone.models import User
from pyrone.models.user import find_local_user, find_twitter_user,\
    normalize_email, VerifiedEmail
from pyrone.models.config import get as get_config
from pyrone.lib import helpers as h, auth

log = logging.getLogger(__name__)

@view_config(route_name='account_login_form', renderer='/blog/local_login.mako')
def login_local(request):
    c = dict()
    c['error'] = ''
    
    if request.method == 'POST':
        # process login
        login = request.POST['login']
        password = request.POST['password']
        user = find_local_user(login, password)
        if user is None:
            c['error'] = _('Incorrect login or password')
        else:
            # this method doesn't return any headers actually
            headers = remember(request, None, user=user) #@UnusedVariable
            # after this method execution "request.session['user']" should contain valid user object
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
    c = dict()
    
    return c

@view_config(route_name='account_save_my_profile_ajax', renderer='json', permission='authenticated', request_method='POST')    
def my_profile_save_ajax(request):
    c = dict()
    user_id = auth.get_user(request).id
    
    is_changed = False;
    
    transaction.begin()
    dbsession = DBSession()
    user = dbsession.query(User).options(eagerload('permissions')).get(user_id)
    
    if user is None:
        return HTTPNotFound()
    
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
            user.password = md5(request.POST['new_password']).hexdigest()
            is_changed = True
            
    if is_changed:
        dbsession.flush()
        dbsession.expunge(user)
        user.get_permissions()
        transaction.commit()
        # also update Beaker session object
        remember(request, None, user=user)
    else:
        transaction.abort()
        
    return c

@view_config(route_name='account_twitter_init', renderer='json')
def login_twitter_init(request):
    """
    Start twitter authentication
    """
    c = dict(authorize_url=False)

    consumer_key = get_config('tw_consumer_key')
    consumer_secret = get_config('tw_consumer_secret')
    #site_base_url = get_config('site_base_url')
    #site_base_url = site_base_url.rstrip().rstrip('/')
    
    # remove all trailing slashes from the url
    
    page_url = request.POST['page_url']
    callback_url = route_url('account_twitter_finish', request, _query=[ ('pyrone_url', page_url) ])
    log.debug('CCCCCCCCCCCCCCCCCCCCCCCCCCC')
    log.debug(callback_url)
    
    oh = tweepy.OAuthHandler(consumer_key, consumer_secret, callback=callback_url, secure=True)
    try:
        auth_url = oh.get_authorization_url(signin_with_twitter=False)
        c['authorize_url'] = auth_url
        # save auth token in the session, it's required for the final auth stage
        request.session['twitter_request_token'] = (oh.request_token.key, oh.request_token.secret) 
        request.session.save()
    except tweepy.TweepError:
        log.error('Invalid "consumer_key" or "consumer_secret"')
        c['error'] = _('Cannot create authorization Twitter URL')
        
    return c
    
@view_config(route_name='account_twitter_finish', renderer='json')
def login_twitter_finish(request):
    """
    Finish twitter authentication
    """
    consumer_key = get_config('tw_consumer_key')
    consumer_secret = get_config('tw_consumer_secret')
    token = request.session.get('twitter_request_token')
    if token is None:
        return HTTPNotFound()

    del request.session['twitter_request_token']
    
    oh = tweepy.OAuthHandler(consumer_key, consumer_secret)
    oh.set_request_token(token[0], token[1])
    
    #request_token = request.GET['oauth_token']
    verifier = request.GET.get('oauth_verifier')
    
    try:
        oh.get_access_token(verifier)
    except tweepy.TweepError:
        log.error('Invalid "oauth_verifier" request argument')
        return HTTPNotFound() 
         
    # looks fine, it's a really twitter user so authenticate it or create account now
    # Do we need to store "oh.access_token.key" and "oh.access_token.secret"?
    # we also have to fetch twitter user name
    tw_username = oh.get_username()
    user = find_twitter_user(tw_username)
    
    if user is None:
        dbsession = DBSession()
        transaction.begin()
        # create user
        user = User()
        user.kind = 'twitter'
        user.login = tw_username
        dbsession.add(user)
        transaction.commit()
        
        # re-request again to correctly read permissions
        user = find_twitter_user(tw_username)    
        if user is None:
            log.error('Unable to create twitter user')
            return HTTPServerError()
        
    # save user to the session
    remember(request, None, user=user)

    return HTTPFound(location=request.GET['pyrone_url'])    
    
@view_config(route_name='account_verify_email', renderer='/blog/verify_email.mako')
def verify_email(request):
    c = dict()
    
    fail = False
    try:
        email = normalize_email(request.GET['email'])
        verification_code = request.GET['token']
        dbsession = DBSession()
        transaction.begin()
        vf = dbsession.query(VerifiedEmail).filter(VerifiedEmail.email==email).first()
        if vf is None or vf.verification_code != verification_code or vf.is_verified:
            fail = True
        else:
            vf.is_verified = True
            transaction.commit()
    except KeyError:
        transaction.abort()
        fail = True
        
    if fail:
        c['result'] = _('Verification failed: email not found.')
    else:
        c['result'] = _('Email `%s` has confirmed.') % 'aaa'
        
    return c