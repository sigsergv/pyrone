## -*- coding: utf-8 -*-
import logging

from pyramid.i18n import TranslationString as _

from pyramid.security import remember
from pyramid.security import forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url

from pyrone.models import DBSession
from pyrone.models import config
from pyrone.models.user import find_local_user
from pyrone.lib import helpers as h

log = logging.getLogger(__name__)

@view_config(route_name='blog_login_form', renderer='/blog/local_login.mako')
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
            
    elif request.method == 'GET':
        log.debug(request.session)
        
    return c

@view_config(route_name='blog_logout')    
def logout(request):
    # "forget" method is also doesn't return any headers 
    headers = forget(request)
    return HTTPFound(location=route_url('blog_latest', request), headers=headers)
    