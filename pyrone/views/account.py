## -*- coding: utf-8 -*-
import logging
import transaction

from hashlib import md5

from sqlalchemy.orm import eagerload
from pyramid.i18n import TranslationString as _
from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound

from pyrone.models import DBSession
from pyrone.models import User
from pyrone.models.user import find_local_user
from pyrone.lib import helpers as h, auth

log = logging.getLogger(__name__)

@view_config(route_name='account_login_form', renderer='/blog/local_login.mako')
def login_form(request):
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
