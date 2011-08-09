import logging

from pyrone.models import DBSession
from pyramid.view import view_config

log = logging.getLogger(__name__)

#@view_config(route_name='blog_latest', renderer='/blog/list_articles.mako')
@view_config(route_name='blog_latest', renderer='/blog/test.mako')
def latest(request):
    log.debug(request.session)
    return dict(project='pyrone')