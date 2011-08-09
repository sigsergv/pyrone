from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyrone.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'pyrone:static')
    config.add_route('home', '/')
    config.add_view('pyrone.views.my_view',
                    route_name='home',
                    renderer='templates/mytemplate.pt')
    return config.make_wsgi_app()

