#import pyramid.threadlocal as threadlocal
#from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.i18n import TranslationString

from pyrone.lib import helpers

def add_renderer_globals(event):
    #renderer_globals = event
    #renderer_globals['h'] = helpers
    event['h'] = helpers
    request = event.get('request')# or threadlocal.get_current_request()
    if not request:
        return
    
    event['_'] = TranslationString
 
#tsf = TranslationStringFactory('pyrone')

#def add_localizer(event):
#    