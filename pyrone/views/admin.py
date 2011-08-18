## -*- coding: utf-8 -*-
import logging
import transaction

from pyramid.i18n import TranslationString as _
from pyramid.view import view_config
from pyramid.url import route_url

from pyrone.lib import helpers as h, auth, markup
from pyrone.models import config, DBSession, Article, Comment, Tag

log = logging.getLogger(__name__)



@view_config(route_name='admin_settings', renderer='/admin/settings.mako', permission='admin', request_method='GET')
def view_settings(request):
    """
    Display blog settings
    """
    c = dict(settings=dict(), errors=dict())
    for p in config.get_all():
        c['settings'][p.id] = p.value
    
    return c

@view_config(route_name='admin_settings_save_ajax', renderer='json', permission='admin', request_method='POST')
def save_settings_ajax(request):
    """
    Save settings
    """
    c = dict()
    errors = dict()
    
    epp = request.POST['elements_on_page']

    try:
        epp = int(epp)
    except ValueError:
        errors['elements_on_page'] = _('Invalid value, must be positive numeric value')

    preview_width = request.POST['image_preview_width']
    try:
        preview_width = int(preview_width)
    except ValueError:
        errors['image_preview_width'] = _('Invalid value, must be positive numeric value')

    if len(errors):
        c['errors'] = errors
    else:
        dbsession = DBSession()
        transaction.begin()
        
        # save settings
        settings = ('site_title', 'site_base_url', 'site_copyright', 'elements_on_page',
              'admin_notifications_email', 'verification_msg_sibject_tpl',
              'comment_answer_msg_subject_tpl', 'comment_answer_msg_body_tpl',
              'verification_msg_body_tpl', 'image_preview_width',
              'tw_consumer_key', 'tw_consumer_secret')
        for id in settings:
            try:
                v = request.POST[id]
                config.set(id, v)
            except KeyError:
                continue

        bool_settings = ('admin_notify_new_comments', 'admin_notify_new_user')
        for id in bool_settings:
            if id in request.POST:
                v = True
            else:
                v = False
            config.set(id, v, dbsession)

        transaction.commit()
        
        config.clear_cache()
    
    return c