from pyrone.models import DBSession
from pyramid.view import view_config

#@view_config(route_name='blog_latest', renderer='/blog/list_articles.mako')
@view_config(route_name='blog_latest', renderer='/blog/test.mako')
def latest(request):
    return dict(project='pyrone')