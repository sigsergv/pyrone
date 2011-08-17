## -*- coding: utf-8 -*-
import logging
import re
import transaction
import uuid

from sqlalchemy.orm import eagerload, contains_eager

from pyramid.response import Response
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound

from pyrone.models import DBSession, Article, Comment, Tag
from pyrone.models.config import get as get_config
from pyrone.lib import helpers as h, auth, markup

log = logging.getLogger(__name__)

@view_config(route_name='blog_latest', renderer='/blog/list_articles.mako')
def latest(request):
    """
    Display list of articles sorted by publishing date ascending,
    show rendered previews, not complete articles
    """
    c = dict(articles=list())
    
    page_size = int(get_config('elements_on_page'))
    start_page = 0
    if 'start' in request.GET:
        try:
            start_page = int(request.GET['start'])
        except ValueError:
            start_page = 0
    
    dbsession= DBSession()
    user = auth.get_user(request)
    
    q = dbsession.query(Article).options(eagerload('tags')).options(eagerload('user')).order_by(Article.published.desc())
    if not user.has_permission('edit_article'):
        q = q.filter(Article.is_draft==False)
        
    c['articles'] = q[(start_page * page_size) : (start_page+1) * page_size + 1]
    
    for article in c['articles']:
        log.debug(article.shortcut_date)
    
    c['prev_page'] = None
    if len(c['articles']) > page_size:
        c['prev_page'] = route_url('blog_latest', request, _query=[('start', start_page+1)])
        c['articles'].pop()
        
    c['next_page'] = None
    if start_page > 0:
        c['next_page'] = route_url('blog_latest', request, _query=[('start', start_page-1)])
    
    c['page_title'] = _('Latest articles')
    
    return c

def _check_article_fields(article, request):
    """
    Read article from the POST request, also validate data
    """
    errors = dict()
    # check passed data
    fields = ['title', 'shortcut', 'body']
    for f in fields:
        if f in request.POST:
            setattr(article, f, request.POST[f])

    req_fields = ['title', 'shortcut', 'body']
    for f in req_fields:
        if not getattr(article, f):
            errors[f] = _('field is required')

    # optional boolean values
    fields = ['is_draft', 'is_commentable']
    for f in fields:
        if f in request.POST:
            setattr(article, f, True)
        else:
            setattr(article, f, False)

    # render body
    article.set_body(request.POST['body'])
    
    return errors

@view_config(route_name='blog_write_article', renderer='/blog/write_article.mako', permission='write_article')
def write_article(request):
    c = dict(
         new_article=True, 
         submit_url=route_url('blog_write_article', request),
         errors=dict(),
         tags=list() )

    if request.method == 'GET':
        a = Article('new-article-shortcut', 'New article title')
        c['tags'] = []
        c['article'] = a
        c['article_published_str'] = h.timestamp_to_str(a.published)
        
    elif request.method == 'POST':
        article = Article()
        e = _check_article_fields(article, request)
        c['errors'].update(e)
        c['article_published_str'] = request.POST['published']
        
        if 'published' not in request.POST:
            c['errors']['published'] = _('invalid date and time format')
        else:
            # parse value to check structure
            date_re = re.compile('^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2})$')
            mo = date_re.match(request.POST['published'])
            if mo is None:
                c['errors']['published'] = _('invalid date and time format')
            else:
                # we need to convert LOCAL date and time to UTC seconds
                article.published = h.str_to_timestamp(request.POST['published'])
                article.shortcut_date = '%04d/%02d/%02d' % tuple([int(x) for x in mo.groups()[0:3]])
            
            dbsession = DBSession()
            q = dbsession.query(Article).filter(Article.shortcut_date==article.shortcut_date)\
                .filter(Article.shortcut==article.shortcut)
            res = q.first()
    
            if res is not None:
                c['errors']['shortcut'] = _('duplicated shortcut')
        
        # tags
        c['tags'] = []
        if 'tags' in request.POST:
            tags_str = request.POST['tags']
            tags = set([s.strip() for s in tags_str.split(',')])

            for tag_str in tags:
                if tag_str == '':
                    continue
                c['tags'].append(tag_str)
                
        if len(c['errors']) == 0:
            dbsession = DBSession()
            transaction.begin()
            
            # save and redirect
            user = auth.get_user(request)
            article.user_id = user.id
            dbsession.add(article)
            dbsession.flush() # required as we need to obtain article_id
            
            article_id = article.id

            for tag_str in c['tags']:
                tag = Tag(tag_str, article)
                dbsession.add(tag)
                
            transaction.commit()
            
            return HTTPFound(location=route_url('blog_go_article', request, article_id=article_id))
            
        c['article'] = article
            
    else:
        return HTTPBadRequest()
        
    return c

@view_config(route_name='blog_edit_article', renderer='/blog/write_article.mako', permission='write_article')
def edit_article(request):
    article_id = int(request.matchdict['article_id'])
    c = dict()
    c['errors'] = dict()
    c['new_article'] = False
    
    dbsession = DBSession()
    
    if request.method == 'GET':
        article = dbsession.query(Article).get(article_id)
        c['tags'] = [tag.tag for tag in article.tags]
        c['article_published_str'] = h.timestamp_to_str(article.published)
    elif request.method == 'POST':
        transaction.begin()
        article = dbsession.query(Article).get(article_id)
        # check fields etc
        e = _check_article_fields(article, request)
        c['errors'].update(e)
        c['article_published_str'] = request.POST['published']
        
        if 'published' not in request.POST:
            c['errors']['published'] = _('invalid date and time format')
        else:
            # parse value to check structure
            date_re = re.compile('^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2})$')
            mo = date_re.match(request.POST['published'])
            if mo is None:
                c['errors']['published'] = _('invalid date and time format')
            else:
                # we need to convert LOCAL date and time to UTC seconds
                article.published = h.str_to_timestamp(request.POST['published'])
                article.shortcut_date = '%04d/%02d/%02d' % tuple([int(x) for x in mo.groups()[0:3]])
            
            dbsession = DBSession()
            q = dbsession.query(Article).filter(Article.shortcut_date==article.shortcut_date)\
                .filter(Article.id != article_id)\
                .filter(Article.shortcut==article.shortcut)
            res = q.first()
    
            if res is not None:
                c['errors']['shortcut'] = _('duplicated shortcut')
                
        # tags
        c['tags'] = [] # these are new tags
        if 'tags' in request.POST:
            tags_str = request.POST['tags']
            tags = set([s.strip() for s in tags_str.split(',')])

            for tag_str in tags:
                if tag_str == '':
                    continue
                c['tags'].append(tag_str)
                
        if len(c['errors']) == 0:
            for tag in article.tags:
                dbsession.delete(tag)
                
            for tag_str in c['tags']:
                tag = Tag(tag_str, article)
                dbsession.add(tag)
                
            transaction.commit()
            
            return HTTPFound(location=route_url('blog_go_article', request, article_id=article_id))
        else:
            transaction.abort()
        
    else:
        return HTTPBadRequest()
    
    if article is None:
        return HTTPNotFound()
    
    c['article'] = article
    c['submit_url'] = route_url('blog_edit_article', request, article_id=article_id)
    return c

@view_config(route_name='blog_preview_article', permission='write_article')
def preview_article(request):
    preview, complete = markup.render_text_markup(request.POST['body']) #@UnusedVariable
    
    return Response(body=complete, content_type='text/html')

def _view_article(request, article_id=None, article=None):
    c = dict()
    
    dbsession = DBSession()
    
    if article is None:
        article = dbsession.query(Article).get(article_id)
        
    if article is None:
        return HTTPNotFound()
    
    comments = dbsession.query(Comment).filter(Comment.article==article).all()
    comments_dict = dict()
    
    for x in comments:
        if x.parent_id not in comments_dict:
            comments_dict[x.parent_id] = list()
        if x.user is not None:
            x._real_email = x.user.email
        else:
            x._real_email = x.email
        if x._real_email == '':
            x._real_email = None
        comments_dict[x.parent_id].append(x)

    scope = dict(thread=[])

    def build_thread(parent_id, indent):
        if parent_id not in comments_dict:
            return

        for x in comments_dict[parent_id]:
            setattr(x, '_indent', indent)
            scope['thread'].append(x)
            build_thread(x.id, indent+1)

    build_thread(None, 0)
    c['comments'] = scope['thread']
    
    signature = str(uuid.uuid4()).replace('-', '')
    is_subscribed = False
    
    for cn in ('comment_display_name', 'comment_email', 'comment_website'):
        if cn in request.cookies:
            c[cn] = request.cookies[cn]
        else:
            c[cn] = ''
    
    c['article'] = article
    c['signature'] = signature
    c['is_subscribed'] = is_subscribed
    
    return c

@view_config(route_name='blog_go_article', renderer='/blog/view_article.mako')
def go_article(request):
    article_id = int(request.matchdict['article_id'])
    
    return _view_article(request, article_id=article_id)

@view_config(route_name='blog_view_article', renderer='/blog/view_article.mako')
def view_article(request):
    shortcut_date = request.matchdict['shortcut_date']
    shortcut = request.matchdict['shortcut']
    
    dbsession = DBSession()
    q = dbsession.query(Article).filter(Article.shortcut_date==shortcut_date).filter(Article.shortcut==shortcut)
    user = auth.get_user(request)
    if not user.has_permission('edit_article'):
        q = q.filter(Article.is_draft==False)
    article = q.first()
    
    return _view_article(request, article=article)

@view_config(route_name='blog_add_article_comment_ajax', renderer='json', request_method='POST')
def add_article_comment_ajax(request):
    article_id = int(request.matchdict['article_id'])

    dbsession = DBSession(expire_on_commit=False)
    transaction.begin()
    q = dbsession.query(Article).filter(Article.id==article_id)
    user = auth.get_user(request)
    if not user.has_permission('edit_article') or not user.has_permission('admin'):
        q = q.filter(Article.is_draft==False)
    article = q.first()
    
    if article is None or not article.is_commentable:
        transaction.abort()
        return HTTPNotFound()
    
    if 's' not in request.POST:
        transaction.abort()
        return HTTPBadRequest()
    
    json = dict()
    
    key = request.POST['s']

    # all data elements are constructed from the string "key" as substrings
    body_ind = key[3:14]
    parent_ind = key[4:12]
    display_name_ind = key[0:5]
    email_ind = key[13:25]
    website_ind = key[15:21]
    is_subscribed_ind = key[19:27]
    
    for ind in (body_ind, parent_ind, display_name_ind, email_ind, website_ind):
        if ind not in request.POST:
            transaction.abort()
            return HTTPBadRequest()
        
    body = request.POST[body_ind]
        
    if len(body) == 0:
        transaction.abort()
        return dict(error=_('Empty comment body is not allowed.'))
    
    comment = Comment()
    comment.set_body(body)
    
    user = auth.get_user(request)
    
    if user.kind != 'anonymous':
        comment.user_id = user.id
    else:
        # get "email", "display_name" and "website" arguments
        comment.display_name = request.POST[display_name_ind]
        comment.email = request.POST[email_ind]
        comment.website = request.POST[website_ind]
        
        # remember email, display_name and website in browser cookies
        request.response.set_cookie('comment_display_name', comment.display_name, max_age=31536000)
        request.response.set_cookie('comment_email', comment.email, max_age=31536000)
        request.response.set_cookie('comment_website', comment.website, max_age=31536000)
        
    # set parent comment
    parent_id = request.POST[parent_ind]
    try:
        parent_id = int(parent_id)
    except ValueError:
        parent_id = None

    if parent_id:
        parent = dbsession.query(Comment).filter(Comment.id==parent_id).filter(Comment.article_id==article_id).first()
        if parent is not None:
            if not parent.is_approved:
                #
                transaction.abort()
                data = dict(error=_('Answering to not approved comment'))
                return json.dumps(data)
            
    comment.parent_id = parent_id
    comment.article_id = article_id
    
    if is_subscribed_ind in request.POST:
        comment.is_subscribed = True

    request.response.set_cookie('is_subscribed', 'true' if comment.is_subscribed else 'false', max_age=31536000)

    # automatically approve comment if user has permission "admin", "write_article" or "edit_article"
    if user.has_permission('admin') or user.has_permission('write_article') \
            or user.has_permission('edit_article'):
        comment.is_approved = True
        
    # TODO: also automatically approve comment if it's considered as safe:
    # i.e. without hyperlinks, spam etc
    
    # check how much hyperlinks in the body string
    if len(re.findall('https?://', body, flags=re.IGNORECASE)) <= 1:
        comment.is_approved = True

    article.comments_total += 1
    if comment.is_approved:
        article.comments_approved += 1

    # record commenter ip address
    comment.ip_address = request.environ.get('REMOTE_ADDR', 'unknown')
    comment.xff_ip_address = request.environ.get('X_FORWARDED_FOR', None)

    dbsession.add(comment)
    dbsession.flush()
    
    transaction.commit()
    
    # cosntruct comment_id
    # we're not using route_url() for the article because stupid Pyramid urlencodes fragments
    comment_url = '%s%s/%s#comment-%d' % (route_url('blog_latest', request), article.shortcut_date, article.shortcut, comment.id)
    
    # return rendered comment
    data = dict(body=comment.rendered_body, approved=comment.is_approved, id=comment.id, url=comment_url)

    return data
    