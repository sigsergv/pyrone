import pyramid.threadlocal as threadlocal

from pyrone.lib import helpers

def add_renderer_globals(event):
    #renderer_globals = event
    #renderer_globals['h'] = helpers
    event['h'] = helpers