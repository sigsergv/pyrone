# -*- coding: utf-8 -*-
"""
Notifications
"""

import logging

from pyramid.url import route_url

from pyrone.models.config import get as get_config
from pyrone.models.user import normalize_email
from pyrone.lib import helpers as h

log = logging.getLogger(__name__)

class Notification:
    """
    Object represents notification object
    """
    subject = None
    body = None
    to = None
    
    def send(self):
        log.debug('--------------------------------------------------')
        debug_data = '''
            SEND NOTIFICATION:
            Subject: %(subject)s
            To: %(to)s

            %(body)s
            ''' % dict(subject=self.subject, to=self.to, body=self.body)
        log.debug(debug_data)
        log.debug('--------------------------------------------------')
    
    def __init__(self, to, subject, body):
        self.subject = subject
        self.body = body
        self.to = to

def _extract_comment_sub(request, comment):
    """
    Extract placeholders substitution strings from the comment object
    """
    author_name = comment.display_name
    author_email = comment.email
    
    if comment.user is not None:
        author_name = comment.user.display_name
        author_email = comment.user.email
        
    # construct comment link
    article = comment.article
    comment_url = h.article_url(request, article) + '#comment-' + str(comment.id)
    comment_link = '<a href="%(url)s">%(title)s</a>' % dict(url=comment_url, title=comment_url)
    
    comment_date = h.timestamp_to_str(comment.published)
    res = dict(comment_author_email=author_email, comment_author_name=author_name, comment_text=comment.body,
               comment_link=comment_link, comment_date=comment_date)
    return res

def _extract_article_sub(request, article):
    """
    Extract placeholders substitution strings from the article object
    """
    article_url = h.article_url(request, article)
    article_link = '<a href="%(url)s">%(title)s</a>' % dict(url=article_url, title=article.title)
    
    res = dict(article_title=article.title, article_link=article_link)
    return res

def gen_comment_response_notification(email, comment, top_comment):
    # generate notification using templates
    subject_tpl = get_config('comment_answer_msg_subject_tpl')
    body_tpl = get_config('comment_answer_msg_body_tpl')
    
    subject = ''
    body = ''
    
    n = Notification(email, subject, body)
    return n

def gen_email_verification_notification(email):
    """
    Generate email address verification notification.
    Placeholders for the subject:
        {site_title}
    Placeholders for the body:
        {site_title}
        {email}
        {verify_link}
    """
    subject_tpl = get_config('verification_msg_sibject_tpl')
    body_tpl = get_config('verification_msg_body_tpl')
    
    subject = subject_tpl
    verify_link = '<a href="%(url)s">%(title)s</a>' % dict(url='http://example.com', title='http://example.com')
    body = body_tpl.replace('{email}', email).replace('{verify_link}', verify_link)
    n = Notification(email, subject, body)
    
    return n

def gen_new_comment_admin_notification(request, article, comment):
    """
    Generate new comment notification for the administrator.
    Plaseholders for the subject:
        {article_title}
        {comment_author_name} — author of the comment
        {comment_author_email} 
    Plaseholders for the body: 
        {comment_date} — date, when comment was written
        {comment_author_name} — author of the comment
        {comment_author_email} 
        {comment_text} — comment text
        {comment_link} — link to the comment
        {article_title}
        {article_link}
    """
    subject_tpl = get_config('admin_notify_new_comment_subject_tpl')
    body_tpl = get_config('admin_notify_new_comment_body_tpl')
    
    repl = dict()
    repl.update(_extract_comment_sub(request, comment))
    repl.update(_extract_article_sub(request, comment.article))
    
    subject = subject_tpl
    for k in ('comment_author_name', 'comment_author_email', 'article_title'):
        if k in repl:
            subject = subject.replace('{%s}'%k, repl[k])
    
    body = body_tpl
    for k in ('comment_author_name', 'comment_author_email', 'article_title', 'comment_date', 
              'comment_text', 'comment_link', 'article_title', 'article_link'):
        if k in repl:
            body = body.replace('{%s}'%k, repl[k])
    
    email = normalize_email(get_config('admin_notifications_email'))
    if not email:
        return None
    
    n = Notification(email, subject, body)
    
    return n
    