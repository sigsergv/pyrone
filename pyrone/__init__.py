from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config

# from pyrone.lib.auth import PyroneSessionAuthenticationPolicy, get_user
from pyrone.models.file import init_storage_from_settings
from pyrone.lib.notifications import init_notifications_from_settings
from pyrone.lib.lang import locale_negotiator
#from pyrone.resources import RootFactory


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('.security')
    config.include('.routes')
    config.include('.models')
    config.include('pyramid_mako')

    return config.make_wsgi_app()
    '''
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    session_factory = session_factory_from_settings(settings)
    init_storage_from_settings(settings)
    init_notifications_from_settings(settings)
    authentication_policy = PyroneSessionAuthenticationPolicy()
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, session_factory=session_factory,
        root_factory='pyrone.resources.RootFactory',
        authentication_policy=authentication_policy,
        authorization_policy=authorization_policy,
        locale_negotiator=locale_negotiator)
    config.add_translation_dirs('pyrone:locale/')
    config.add_request_method(get_user, 'user', reify=True)  # reify=True means that result is cached per request
    config.scan()

    config.add_subscriber('pyrone.subscribers.add_renderer_globals', 'pyramid.events.BeforeRender')
    config.add_subscriber('pyrone.subscribers.add_localizer', 'pyramid.events.NewRequest')

    return config.make_wsgi_app()
    '''
