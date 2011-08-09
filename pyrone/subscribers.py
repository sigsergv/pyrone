import pyramid.threadlocal as threadlocal

from pyrone.lib import helpers

def add_renderer_globals(event):
    renderer_globals = event
    renderer_globals['h'] = helpers
    
    request = event.get('request') or threadlocal.get_current_request()
    if not request:
        return
    tmpl_context = request.tmpl_context
    renderer_globals['c'] = tmpl_context
    renderer_globals['tmpl_context'] = tmpl_context
    