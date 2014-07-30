import logging

from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.url import route_url

from pyrone.lib import helpers

log = logging.getLogger(__name__)

class url_generator():
    def __init__(self, request):
        self.request = request

    def __call__(self, route_name, **kwargs):
        return route_url(route_name, self.request, **kwargs)


def add_renderer_globals(event):
    #renderer_globals = event
    #renderer_globals['h'] = helpers
    event['h'] = helpers
    request = event.get('request')  # or threadlocal.get_current_request()
    if not request:
        return

    event['_'] = request.translate
    event['url'] = url_generator(request)
    event['user'] = request.user

tsf = TranslationStringFactory('pyrone')


def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(string):
        return localizer.translate(tsf(string))

    request.translate = auto_translate
