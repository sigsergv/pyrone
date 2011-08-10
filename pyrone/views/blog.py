## -*- coding: utf-8 -*-
import logging

from pyramid.view import view_config
from pyrone.models import DBSession
from pyrone.models import config

log = logging.getLogger(__name__)

#@view_config(route_name='blog_latest', renderer='/blog/list_articles.mako')
@view_config(route_name='blog_latest', renderer='/blog/test.mako')
def latest(request):
    v = config.get('site_title')
    log.debug(v)
    
    config.set('aaabbb', u'фывфыв')
    
    log.debug(request.session)
    return dict(project='pyrone')