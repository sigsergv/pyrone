from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyrone.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.scan()
    config.add_static_view('static', 'pyrone:static')
    config.add_route('blog_latest', '/')
    config.add_subscriber('pyrone.subscribers.add_renderer_globals', 'pyramid.events.BeforeRender')
    
    #config.add_view('pyrone.views.latest',
    #                route_name='latest',
    #                renderer='templates/mytemplate.pt')
    return config.make_wsgi_app()