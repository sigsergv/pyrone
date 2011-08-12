## -*- coding: utf-8 -*-
import logging
import re
import transaction

from pyramid.i18n import TranslationString as _

from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound

from pyrone.models import DBSession, Article, Tag
from pyrone.lib import helpers as h, auth

log = logging.getLogger(__name__)

@view_config(route_name='blog_latest', renderer='/blog/list_articles.mako')
def latest(request):
    """
    Display list of articles sorted by publishing date ascending,
    show rendered previews, not complete articles
    """
    c = dict()
    c['page_title'] = _('Latest articles')
    c['articles'] = list()
    c['next_page'] = None
    c['prev_page'] = None
    
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
        
    elif request.method == 'POST':
        article = Article()
        e = _check_article_fields(article, request)
        c['errors'].update(e)
        
        if 'published' not in request.POST:
            c['errors']['published'] = _('field is required')
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

@view_config(route_name='blog_go_article', renderer='/blog/view_article.mako')
def go_article(request):
    article_id = int(request.matchdict['article_id'])
    dbsession = DBSession()
    article = dbsession.query(Article).get(article_id)
    comments = []
    signature = ''
    is_subscribed = False
    comment_display_name = ''
    comment_email = ''
    
    if article is None:
        return HTTPNotFound()
    
    return dict(article=article, comments=comments, signature=signature, is_subscribed=is_subscribed,
                comment_display_name=comment_display_name, comment_email=comment_email)

@view_config(route_name='blog_view_article')
def view_article(request):
    pass
