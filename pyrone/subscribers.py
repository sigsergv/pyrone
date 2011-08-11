#import pyramid.threadlocal as threadlocal
#from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.i18n import TranslationString
from pyramid.url import route_url

from pyrone.lib import helpers

class url_generator():
    def __init__(self, request):
        self.request = request
        
    def __call__(self, route_name, **kwargs):
        return route_url(route_name, self.request, **kwargs)

def add_renderer_globals(event):
    #renderer_globals = event
    #renderer_globals['h'] = helpers
    event['h'] = helpers
    request = event.get('request')# or threadlocal.get_current_request()
    if not request:
        return
    
    event['_'] = TranslationString
    event['url'] = url_generator(request)
 
#tsf = TranslationStringFactory('pyrone')

#def add_localizer(event):
#    