## -*- coding: utf-8 -*-
import logging

from pyramid.i18n import TranslationString as _

from pyramid.view import view_config
from pyrone.models import DBSession
from pyrone.models import config
from pyrone.lib import helpers as h

log = logging.getLogger(__name__)

@view_config(route_name='blog_latest', renderer='/blog/list_articles.mako')
def latest(request):
    """
    Display list of articles sorted by publishing date ascending,
    show rendered previews, not complete articles
    """
    c = dict()
    c['title'] = _('Latest articles')
    c['articles'] = list()
    c['next_page'] = None
    c['prev_page'] = None
    
    return c