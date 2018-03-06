import logging
import transaction
import shutil
import base64
import os
import zipfile
from pyramid.security import forget
from lxml import etree
from datetime import datetime

from base64 import b64encode, b64decode
from mimetypes import guess_type
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import Sequence

from pyrone.lib import helpers as h, httpcode, cache
from pyrone.models import config, DBSession, Article, Comment, Tag, File, Config, User, Role, VerifiedEmail
from pyrone.models.file import get_storage_dirs, get_backups_dir, allowed_dltypes
from pyrone.lib.jsonhttpresponse import JSONResponse

log = logging.getLogger(__name__)


@view_config(route_name='admin_settings', renderer='/admin/settings.mako', permission='admin', request_method='GET')
def view_settings(request):
    """
    Display blog settings
    """
    c = {
        'settings': {}, 
        'errors': {}
        }
    for p in config.get_all():
        c['settings'][p.id] = p.value

    defaults = {
        'ui_theme': 'default',
        'social_facebook_share': True
    }

    for k,v in defaults.items():
        if k not in c['settings'] or c['settings'][k] is None:
            c['settings'][k] = v

    return c


@view_config(route_name='admin_settings_save_ajax', renderer='json', permission='admin', request_method='POST')
def save_settings_ajax(request):
    """
    Save settings
    """
    _ = request.translate
    c = {}
    errors = {}

    epp = request.POST['elements_on_page']

    try:
        epp = int(epp)
    except (ValueError, TypeError):
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

        # save settings
        settings = ('site_title', 'site_base_url', 'site_copyright', 'elements_on_page',
              'admin_notifications_email', 'notifications_from_email',
              'image_preview_width', 'google_analytics_id', 'timezone', 'ui_lang', 
              'tw_consumer_key', 'tw_consumer_secret', 'social_twitter_share_link',
              'social_twitter_share_link_show_count', 'social_twitter_share_link_via',
              'social_gplusone', 'social_facebook_share', 'site_search_widget_code', 'ui_theme')

        for id in settings:
            try:
                v = request.POST[id]
                config.set(id, v)
            except KeyError:
                continue

        bool_settings = ('admin_notify_new_comments',
            'admin_notify_new_user', 'social_twitter_share_link',
            'social_twitter_share_link_show_count',
            'social_gplusone', 'social_facebook_share')
        for id in bool_settings:
            if id in request.POST:
                v = 'true'
            else:
                v = 'false'
            config.set(id, v, dbsession)

        # refresh data in the cache
        h.get_gplusone_button(True)
        h.get_twitter_share_link_button(True)

    return c


@view_config(route_name='admin_list_files', renderer='/admin/list_files.mako', permission='admin')
def list_files(request):
    c = {}

    dbsession = DBSession()
    c['files'] = dbsession.query(File).all()
    return c


@view_config(route_name='admin_list_visitors_emails', renderer='/admin/list_visitors_emails.mako', permission='admin')
def list_visitors_emails(request):
    c = {}

    dbsession = DBSession()
    c['emails'] = dbsession.query(VerifiedEmail).all()
    return c


@view_config(route_name='admin_visitor_email_edit_ajax', renderer='json', permission='admin', request_method='POST')
def visitor_email_edit_ajax(request):
    c = {}

    id = int(request.POST['id'])
    is_verified = request.POST['is_verified'] == 'true'

    dbsession = DBSession()
    vf = dbsession.query(VerifiedEmail).get(id)
    if vf is None:
        return HTTPNotFound()

    vf.is_verified = is_verified
    return c


@view_config(route_name='admin_visitors_emails_delete_ajax', renderer='json', permission='admin', request_method='POST')
def visitors_emails_delete_ajax(request):
    c = {
        'deleted': [], 
        'failed': False
        }
    uids_raw = request.POST['uids']
    uids = [int(s.strip()) for s in uids_raw.split(',')]

    dbsession = DBSession()
    dbsession.query(VerifiedEmail).filter(VerifiedEmail.id.in_(uids)).delete(False)
    c['deleted'] = uids
    return c


@view_config(route_name='admin_upload_file', permission='admin')
def upload_file(request):
    """
    Process file upload request
    """
    c = {'errors': {}}

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

    now = datetime.utcnow()

    file = dbsession.query(File).filter(File.name==request.POST['filename']).first()
    if file is None:
        file = File()
    file.name = request.POST['filename']
    file.size = len(hfile.value)
    file.dltype = 'download' if request.POST['dltype'] == 'download' else 'auto'
    file.content_type = content_type
    file.updated = h.dt_to_timestamp(now)

    # save file to the storage
    storage_dirs = get_storage_dirs()
    orig_filename = os.path.join(storage_dirs['orig'], file.name)
    fp = open(orig_filename, 'wb')
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
    c = {'exists': False}

    # check filename
    if 'filename' in request.POST:
        filename = request.POST['filename']
        dbsession = DBSession()
        file = dbsession.query(File).filter(File.name == filename).first()
        if file is not None:
            c['exists'] = True

    return c


@view_config(route_name='admin_delete_files_ajax', renderer='json', permission='admin', request_method='POST')
def delete_files(request):
    uids_raw = request.POST['uids']
    uids = [int(s.strip()) for s in uids_raw.split(',')]

    c = {
        'deleted': uids, 
        'failed': False
        }
    dbsession = DBSession()
    dbsession.query(File).filter(File.id.in_(uids)).delete(False)

    return c


@view_config(route_name='admin_edit_file_props', renderer='/admin/edit_file_props.mako', permission='admin')
def edit_file_props(request):
    c = {'errors': {}}

    file_id = int(request.matchdict['file_id'])
    dbsession = DBSession()

    if request.method == 'POST':
        content_type = request.POST['content_type']
        dltype = request.POST['dltype']
        filename = request.POST['filename']

        file = dbsession.query(File).get(file_id)
        if file is None:
            return HTTPNotFound()
        if dltype in allowed_dltypes:
            file.dltype = dltype

        if content_type != '':
            file.content_type = content_type

        # rename file on disk
        if file.name != filename:
            storage_dirs = get_storage_dirs()
            old_name = os.path.join(storage_dirs['orig'], str(file.name))
            new_name = os.path.join(storage_dirs['orig'], filename)
            os.rename(old_name, new_name)
            file.name = filename

        return HTTPFound(location=route_url('admin_list_files', request))
    elif request.method == 'GET':
        c['file'] = dbsession.query(File).get(file_id)

        if c['file'] is None:
            return HTTPNotFound()

    return c


@view_config(route_name='admin_edit_file_props_check_ajax', renderer='json', permission='admin', request_method='POST')
def edit_file_props_check_ajax(request):
    c = {}
    file_id = int(request.matchdict['file_id'])

    # check filename
    if 'filename' in request.POST:
        filename = request.POST['filename']
        dbsession = DBSession()
        file = dbsession.query(File).filter(File.name == filename).filter(File.id != file_id).first()
        if file is not None:
            c['exists'] = True

    return c


@view_config(route_name='admin_list_backups', renderer='/admin/list_backups.mako', permission='admin')
def list_backups(request):
    c = {'backups': []}

    backups_dir = get_backups_dir()
    ind = 1

    for fn in os.listdir(backups_dir):
        full_fn = os.path.join(backups_dir, fn)
        if not os.path.isfile(full_fn):
            continue
        br = {
            'id': ind,
            'filename': fn, 
            'filename_b64': b64encode(fn.encode('utf-8')).decode('utf-8'), 
            'size': os.path.getsize(full_fn)
            }
        c['backups'].append(br)
        ind += 1

    c['backups'] = sorted(c['backups'], key=lambda x: x['filename'])

    return c


@view_config(route_name='admin_restore_backup', renderer='json', permission='admin')
def restore_backup(request):

    _ = request.translate
    backup_id = request.matchdict['backup_id']

    backups_dir = get_backups_dir()
    filename = b64decode(backup_id).decode('utf-8')
    all_backups = [x for x in os.listdir(backups_dir) if os.path.isfile(os.path.join(backups_dir, x))]

    if filename not in all_backups:
        return {'error': _('Backup file not found')}

    full_filename = os.path.join(backups_dir, filename)

    try:
        z = zipfile.ZipFile(full_filename)
    except zipfile.BadZipfile:
        return {'error': _('Backup file is broken!')}

    # now check zip file contents, first extract file "index.xml"
    try:
        xml_f = z.open('index.xml')
    except KeyError:
        return {'error': _('Backup file is broken, no catalog file inside!')}

    try:
        xmldoc = etree.parse(xml_f)
    except etree.XMLSyntaxError:
        return {'error': _('Backup file is broken, XML catalog is broken!')}

    root = xmldoc.getroot()
    NS = 'http://regolit.com/ns/pyrone/backup/1.0'

    def t(name):
        """
        Convert tag name "name" to full qualified name like "{http://regolit.com/ns/pyrone/backup/1.0}name"
        """
        return '{{{0}}}{1}'.format(NS, name)

    def unt(name):
        """
        Remove namespace
        """
        return name.replace('{{{0}}}'.format(NS), '')

    # now check is backup version supported
    if root.tag != t('backup'):
        return {'error': _('Unknown XML format of catalog file.')}

    backup_version = root.get('version')

    if backup_version not in ('1.0', '1.1'):
        return {'error': _('Unsupported backup version: “{0}”!'.format(root.get('version')))}

    dbsession = DBSession()
    dialect_name = dbsession.bind.name
    # now start to extract all data and fill DB
    # first delete everything from the database
    dbsession.query(Comment).delete()
    dbsession.query(Tag).delete()
    dbsession.query(Article).delete()
    dbsession.query(VerifiedEmail).delete()
    dbsession.query(Role).delete()
    dbsession.query(File).delete()  # also remove files from the storage dir
    dbsession.query(Config).delete()
    dbsession.query(User).delete()
    namespaces = {'b': NS}

    # first restore config
    nodes = xmldoc.xpath('//b:backup/b:settings', namespaces=namespaces)

    if len(nodes) == 0:
        return JSONResponse(httpcode.NotFound, {'error': _('Backup file is broken: settings block not found')})

    node = nodes[0]
    nodes = node.xpath('//b:config', namespaces=namespaces)

    def recursively_restore_commits(tree, root):
        if root not in tree:
            return
        for comment in tree[root]:
            dbsession.add(comment)
        dbsession.flush()
        for comment in tree[root]:
            recursively_restore_commits(tree, comment.id)

    for node in nodes:
        c = dbsession.query(Config).get(node.get('id'))
        if c is None:
            c = Config(node.get('id'), node.text)
            dbsession.add(c)
        else:
            c.value = node.text

    # now restore users
    nodes = xmldoc.xpath('//b:backup/b:users', namespaces=namespaces)
    if len(nodes) == 0:
        return JSONResponse(httpcode.NotFound, {'error': _('Backup file is broken: users block not found')})

    node = nodes[0]
    nodes = node.xpath('./b:user', namespaces=namespaces)

    for node in nodes:
        u = User()
        u.id = int(node.get('id'))

        subnodes = node.xpath('./*', namespaces=namespaces)
        m = {}
        for sn in subnodes:
            m[unt(sn.tag)] = sn.text

        props = {'login': 'login', 'password': 'password', 'display-name': 'display_name',
                 'email': 'email', 'kind': 'kind'}
        for k, v in props.items():
            if k in m:
                setattr(u, v, m[k])

        dbsession.add(u)

        if backup_version == '1.0':
            # restore permissions now
            permissions_roles_map = {
                'write_article': 'writer',
                'edit_article': 'editor',
                'admin': 'admin',
                'files': 'filemanager'
                }
            subnodes = node.xpath('./b:permissions/b:permission', namespaces=namespaces)
            for sn in subnodes:
                permission_name = sn.text
                if permission_name not in permissions_roles_map:
                    continue

                role_name = permissions_roles_map[permission_name]
                r = Role(None, u.id, role_name)
                dbsession.add(r)
        elif backup_version == '1.1':
            # restore roles directly
            subnodes = node.xpath('./b:roles/b:role', namespaces=namespaces)
            for sn in subnodes:
                r = Role(None, u.id, sn.text)
                dbsession.add(r)

    # restore verified emails
    nodes = xmldoc.xpath('//b:backup/b:verified-emails', namespaces=namespaces)
    if len(nodes) != 0:
        # block is optional
        node = nodes[0]
        nodes = node.xpath('./b:email', namespaces=namespaces)
        for node in nodes:
            vf = VerifiedEmail(node.text)
            vf.last_verify_date = int(node.get('last-verification-date'))
            vf.is_verified = node.get('verified') == 'true'
            vf.verification_code = node.get('verification-code')
            dbsession.add(vf)

    # now restore articles
    nodes = xmldoc.xpath('//b:backup/b:articles', namespaces=namespaces)
    if len(nodes) == 0:
        return JSONResponse(httpcode.NotFound, {'error': _('Backup file is broken: articles block not found')})

    node = nodes[0]
    nodes = node.xpath('./b:article', namespaces=namespaces)

    for node in nodes:
        article = Article()
        article.id = int(node.get('id'))
        article.user_id = int(node.get('user-id'))

        subnodes = node.xpath('./*', namespaces=namespaces)
        m = {}
        for sn in subnodes:
            m[unt(sn.tag)] = sn.text

        props = {'title': 'title', 'body': 'body', 'shortcut': 'shortcut', 'shortcut-date': 'shortcut_date'}
        for k, v in props.items():
            if k in m:
                setattr(article, v, m[k])

        article.set_body(m['body'])

        props = {'published': 'published', 'updated': 'updated'}
        for k, v in props.items():
            if k in m:
                setattr(article, v, int(m[k]))

        props = {'is-commentable': 'is_commentable', 'is-draft': 'is_draft'}

        for k, v in props.items():
            if k in m:
                res = False
                if m[k].lower() == 'true':
                    res = True
                setattr(article, v, res)

        article.comments_total = 0
        article.comments_approved = 0

        # now restore tags
        subnodes = node.xpath('./b:tags/b:tag', namespaces=namespaces)
        tags_set = set()
        for sn in subnodes:
            tags_set.add(sn.text.strip())

        for tag_str in tags_set:
            log.debug('tag: '+tag_str)
            tag = Tag(tag_str, article)
            dbsession.add(tag)

        # now process comments
        # we need to preserve comments hierarchy
        # local_comments = {}  # key is a comment ID, value - comment object
        local_parents = {}  # key is a parent-id, value is a list of child IDs

        subnodes = node.xpath('./b:comments/b:comment', namespaces=namespaces)
        for sn in subnodes:
            comment = Comment()
            comment.article_id = article.id
            comment.id = int(sn.get('id'))
            try:
                comment.parent_id = int(sn.get('parent-id'))
            except KeyError:
                pass
            except TypeError:
                pass

            try:
                comment.user_id = int(sn.get('user-id'))
            except TypeError:
                pass
            except KeyError:
                pass

            subsubnodes = sn.xpath('./*', namespaces=namespaces)
            m = {}
            for sn in subsubnodes:
                m[unt(sn.tag)] = sn.text

            props = {'display-name': 'display_name', 'email': 'email', 'website': 'website',
                     'ip-address': 'ip_address', 'xff-ip-address': 'xff_ip_address'}
            for k, v in props.items():
                if k in m:
                    setattr(comment, v, m[k])

            comment.set_body(m['body'])
            comment.published = int(m['published'])

            props = {'is-approved': 'is_approved', 'is-subscribed': 'is_subscribed'}
            for k, v in props.items():
                if k in m:
                    res = False
                    if m[k].lower() == 'true':
                        res = True
                    setattr(comment, v, res)

            article.comments_total += 1
            if comment.is_approved:
                article.comments_approved += 1

            parent_id = comment.parent_id
            if parent_id not in local_parents:
                local_parents[parent_id] = []
            local_parents[parent_id].append(comment)

        dbsession.add(article)
        dbsession.flush()
        
        recursively_restore_commits(local_parents, None)

    # now process files
    nodes = xmldoc.xpath('//b:backup/b:files', namespaces=namespaces)
    if len(nodes) == 0:
        return JSONResponse(httpcode.NotFound, {'error': _('Backup file is broken: articles block not found')})

    node = nodes[0]
    nodes = node.xpath('./b:file', namespaces=namespaces)

    storage_dirs = get_storage_dirs()
    for node in nodes:
        file = File()
        src = node.get('src')
        # read "name", "dltype", "updated", "content_type"

        subnodes = node.xpath('./*', namespaces=namespaces)
        m = {}
        for sn in subnodes:
            m[unt(sn.tag)] = sn.text

        props = {'name': 'name', 'dltype': 'dltype', 'content-type': 'content_type'}
        for k, v in props.items():
            if k in m:
                setattr(file, v, m[k])

        # check "file.name"
        if file.name == '.' or file.name == '..':
            continue
        if file.name.find('/') != -1 or file.name.find('\\') != -1:
            continue

        if file.dltype not in allowed_dltypes:
            file.dltype = 'auto'

        # extract file from the archive, put to the storage dir, fill attribute "size"
        file_f = z.open(src)
        file_full_path = os.path.join(storage_dirs['orig'], file.name)
        file_out_f = open(file_full_path, 'wb')
        shutil.copyfileobj(file_f, file_out_f)
        file_f.close()
        file_out_f.close()
        file.size = os.path.getsize(file_full_path)

        dbsession.add(file)

    # catch IntegrityError here!
    try:
        transaction.commit()
        
        # reset sequences
        if dialect_name == 'postgresql':
            dbsession.bind.execute(text("SELECT setval('pbarticle_id_seq', (SELECT MAX(id) FROM pbarticle));"))
            dbsession.bind.execute(text("SELECT setval('pbarticlecomment_id_seq', (SELECT MAX(id) FROM pbarticlecomment));"))

    except IntegrityError:
        return JSONResponse(httpcode.BadRequest, {'error': _('Unable to restore backup: database error, maybe your backup file is corrupted')})
    except Exception as e:
        return JSONResponse(httpcode.BadRequest, {'error': _('Unable to restore backup: database error, maybe your backup file is corrupted')})

    # we should also destroy current session (logout)
    forget(request)

    # clear config cache
    cache.clear_cache()

    return {'success': True}


@view_config(route_name='admin_backup_now', renderer='json', permission='admin')
def backup_now(request):
    """
    Perform complete blog backup: articles, comments, files and settings.
    """
    backups_dir = get_backups_dir()
    now = datetime.now()
    stamp = now.strftime('%Y%m%d-%H%M%S')
    backup_file_name = 'backup-{0}.zip'.format(stamp)
    backup_tmp_dir = os.path.join(backups_dir, 'tmp-{0}'.format(stamp))

    os.mkdir(backup_tmp_dir)

    nsmap = {None: 'http://regolit.com/ns/pyrone/backup/1.0'}

    def e(parent, name, text=None):
        node = etree.SubElement(parent, name, nsmap=nsmap)
        if text is not None:
            node.text = text
        return node

    root = etree.Element('backup', nsmap=nsmap)
    root.set('version', '1.1')

    #info_el = e(root, 'info')
    articles_el = e(root, 'articles')
    vf_el = e(root, 'verified-emails')
    files_el = e(root, 'files')
    settings_el = e(root, 'settings')
    users_el = e(root, 'users')

    dbsession = DBSession()
    # dump tables, create xml-file with data, dump files, pack all in the zip-file
    for article in dbsession.query(Article).all():
        article_el = e(articles_el, 'article')
        article_el.set('id', str(article.id))
        article_el.set('user-id', str(article.user_id))
        e(article_el, 'title', article.title)
        e(article_el, 'shortcut-date', article.shortcut_date)
        e(article_el, 'shortcut', article.shortcut)
        e(article_el, 'body', article.body)
        e(article_el, 'published', str(article.published))
        e(article_el, 'updated', str(article.updated))
        e(article_el, 'is-commentable', str(article.is_commentable))
        e(article_el, 'is-draft', str(article.is_draft))
        tags_el = e(article_el, 'tags')

        for t in article.tags:
            e(tags_el, 'tag', t.tag)

        comments_el = e(article_el, 'comments')

        for comment in article.comments:
            comment_el = e(comments_el, 'comment')
            comment_el.set('id', str(comment.id))
            if comment.user_id is not None:
                comment_el.set('user-id', str(comment.user_id))
            if comment.parent_id is not None:
                comment_el.set('parent-id', str(comment.parent_id))
            e(comment_el, 'body', comment.body)
            e(comment_el, 'email', comment.email)
            e(comment_el, 'display-name', comment.display_name)
            e(comment_el, 'published', str(comment.published))
            e(comment_el, 'ip-address', comment.ip_address)
            if comment.xff_ip_address is not None:
                e(comment_el, 'xff-ip-address', comment.xff_ip_address)
            e(comment_el, 'is-approved', str(comment.is_approved))

    # dump verified emails
    for vf in dbsession.query(VerifiedEmail).all():
        s = e(vf_el, 'email', vf.email)
        s.set('verified', 'true' if vf.is_verified else 'false')
        s.set('last-verification-date', str(int(vf.last_verify_date)))
        s.set('verification-code', vf.verification_code)

    # dump settings
    for setting in dbsession.query(Config).all():
        s = e(settings_el, 'config', setting.value)
        s.set('id', setting.id)

    # dump users and roles
    for user in dbsession.query(User).all():
        user_el = e(users_el, 'user')
        user_el.set('id', str(user.id))
        e(user_el, 'login', user.login)
        e(user_el, 'password', user.password)
        e(user_el, 'display-name', user.display_name)
        e(user_el, 'email', user.email)
        e(user_el, 'kind', user.kind)
        perms_el = e(user_el, 'roles')

        for p in user.roles:
            e(perms_el, 'role', p.name)

    # dump files
    ind = 1
    storage_dirs = get_storage_dirs()

    for f in dbsession.query(File).all():
        # check is file exists

        full_path = os.path.join(storage_dirs['orig'], f.name)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            continue

        target_file = 'file{0:05}'.format(ind)
        shutil.copy(full_path, os.path.join(backup_tmp_dir, target_file))

        file_el = e(files_el, 'file')
        file_el.set('src', target_file)
        e(file_el, 'name', f.name)
        e(file_el, 'dltype', f.dltype)
        e(file_el, 'updated', str(f.updated))
        e(file_el, 'content-type', f.content_type)
        ind += 1

    # write xml
    data = {}
    index_xml = os.path.join(backup_tmp_dir, 'index.xml')
    out = open(index_xml, 'wb')
    etree.ElementTree(root).write(index_xml, pretty_print=True, encoding='UTF-8', xml_declaration=True)
    out.close()

    # compress directory
    z = zipfile.ZipFile(os.path.join(backups_dir, backup_file_name), 'w')
    for fn in os.listdir(backup_tmp_dir):
        fn_full = os.path.join(backup_tmp_dir, fn)
        if not os.path.isfile(fn_full):
            continue

        z.write(fn_full, fn)
    z.close()
    data['backup_file'] = backup_file_name

    # cleanup
    shutil.rmtree(backup_tmp_dir, ignore_errors=True)

    data['success'] = True
    return data


@view_config(route_name='admin_download_backup')
def download_backup(request):
    encoded_filename = request.matchdict['backup_id']

    headers = []

    try:
        filename = base64.b64decode(encoded_filename).decode('utf-8')
    except TypeError:
        return HTTPNotFound()

    backups_dir = get_backups_dir()
    all_backups = [x for x in os.listdir(backups_dir) if os.path.isfile(os.path.join(backups_dir, x))]
    if filename not in all_backups:
        return HTTPNotFound()

    full_path = os.path.join(backups_dir, filename)
    if not os.path.isfile(full_path):
        return HTTPNotFound()

    headers = []
    content_length = os.path.getsize(full_path)
    headers.append(('Content-Length', str(content_length)))
    headers.append(('Content-Disposition', str('attachment; filename={0}'.format(filename))))

    response = Response(content_type='application/octet-stream')
    try:
        response.app_iter = open(full_path, 'rb')
    except IOError:
        return HTTPNotFound()

    response.headerlist += headers

    return response


@view_config(route_name='admin_delete_backups_ajax', renderer='json', permission='admin')
def delete_backups(request):
    c = {'deleted': []}
    backups_dir = get_backups_dir()

    uids_raw = request.POST['uids']
    uids = [s.strip() for s in uids_raw.split(',')]

    all_backups = [x for x in os.listdir(backups_dir) if os.path.isfile(os.path.join(backups_dir, x))]

    for backup_id in uids:
        filename = b64decode(backup_id).decode('utf-8')
        if filename not in all_backups:
            continue
        full_filename = os.path.join(backups_dir, filename)
        try:
            os.unlink(full_filename)
        except OSError:
            continue

        c['deleted'].append(backup_id)
        # make sure that "filename" doesn't contain dangerous characters like "/", "\" etc

    return c


@view_config(route_name='admin_list_accounts', renderer='/admin/list_accounts.mako', permission='admin')
def list_accounts(request):
    c = {}

    dbsession = DBSession()
    c['users'] = dbsession.query(User).all()
    return c


@view_config(route_name='admin_delete_accounts_ajax', renderer='json', permission='admin')
def delete_accounts_ajax(request):
    uids_raw = request.POST['uids']
    uids = [int(s.strip()) for s in uids_raw.split(',')]

    c = {
        'deleted': uids, 
        'failed': False
        }
    dbsession = DBSession()
    dbsession.query(User).filter(User.id.in_(uids)).delete(False)

    return c


@view_config(route_name='admin_settings_widget_pages', renderer='/admin/settings_widget_pages.mako', permission='admin', request_method='GET')
def view_pages_widget_settings(request):
    c = {
        'errors': {}, 
        'settings': {}
        }

    widget_pages_pages_spec = config.get('widget_pages_pages_spec')

    c['settings']['widget_pages_pages_spec'] = widget_pages_pages_spec

    return c


@view_config(route_name='admin_settings_widget_pages_save_ajax', renderer='json', permission='admin', request_method='POST')
def save_pages_widget_settings_ajax(request):
    c = {}

    widget_pages_pages_spec = request.POST['widget_pages_pages_spec']
    config.set('widget_pages_pages_spec', widget_pages_pages_spec)
    # force reload page links cache
    h.get_pages_widget_links(True)
    return c
