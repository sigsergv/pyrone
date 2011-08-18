## -*- coding: utf-8 -*-
import logging
import transaction
import shutil
import os.path

from mimetypes import guess_type
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from sqlalchemy.exc import IntegrityError

from pyrone.lib import helpers as h, auth, markup
from pyrone.models import config, DBSession, Article, Comment, Tag, File
from pyrone.models.file import get_storage_dirs, get_backups_dir

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

@view_config(route_name='admin_list_files', renderer='/admin/list_files.mako', permission='admin')
def list_files(request):
    c = dict()
    
    dbsession = DBSession()
    c['files'] = dbsession.query(File).all()
    return c

@view_config(route_name='admin_upload_file', permission='admin')
def upload_file(request):
    """
    Process file upload request
    """
    c = dict(errors=dict())
    
    c['file'] = File()

    # process file upload
    # extract file params etc
    req = ('filedata', 'filename', 'dltype')

    for x in req:
        if x not in request.POST:
            return HTTPBadRequest()

    hfile = request.POST['filedata']

    # guess content type
    content_type = guess_type(hfile.filename)[0] or 'application/octet-stream'

    dbsession = DBSession()
    transaction.begin()
    
    file = File()
    file.name = request.POST['filename']
    file.size = len(hfile.value)
    file.dltype = 'download' if request.POST['dltype']=='download' else 'auto'
    file.content_type = content_type

    # save file to the storage
    storage_dirs = get_storage_dirs()
    orig_filename = os.path.join(storage_dirs['orig'], file.name)
    fp = open(orig_filename, 'w')
    shutil.copyfileobj(hfile.file, fp)
    hfile.file.close()
    fp.close()

    dbsession.add(file)
    dbsession.flush()
    dbsession.expunge(file)
    

    try:
        transaction.commit()
    except IntegrityError:
        # display error etc
        transaction.abort()
        return HTTPFound(location=route_url('admin_list_files', request))

    return HTTPFound(location=route_url('admin_list_files', request))
    
    
@view_config(route_name='admin_upload_file_check_ajax', renderer='json', permission='admin', request_method='POST')
def upload_file_check_ajax(request):
    c = dict(exists=False)

    # check filename
    if 'filename' in request.POST:
        filename = request.POST['filename']
        dbsession = DBSession()
        file = dbsession.query(File).filter(File.name==filename).first()
        if file is not None:
            c['exists'] = True;

    return c