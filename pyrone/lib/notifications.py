"""
Notifications
"""

import logging
import urllib
import re
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process


from pyramid.url import route_url
from pyramid import threadlocal
from pyramid.renderers import render

from pyrone.models.config import get as get_config
from pyrone.models.user import normalize_email
from pyrone.lib.lang import lang
from pyrone.lib import helpers as h

log = logging.getLogger(__name__)

enable_email = False
smtp_server = None


def init_notifications_from_settings(settings):
    global enable_email, smtp_server

    if settings.get('pyrone.notifications.mail') != 'true':
        return

    m_transport = settings.get('pyrone.notifications.mail_transport')
    if m_transport not in ('smtp',):
        log.error('Not supported email transport "{0}"'.format(m_transport))
        return

    enable_email = True
    smtp_server = settings.get('pyrone.notifications.mail_smtp_server')

COMMASPACE = ', '
SUBJECT_RE = re.compile(r'^Subject: ([^\n\r]+)')

def send_email_process(request, template_name, recipients, sender, params):
    """Process for real sending emails"""
    language = lang(request)

    html = render('/email/'+template_name+'.mako', params, request)

    # now cut out subject line from the message
    mo = SUBJECT_RE.match(html)
    if mo is None:
        subject = 'NO-SUBJECT'
    else:
        subject = mo.group(1)
        html = SUBJECT_RE.sub('', html, 1)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(recipients)
    msg.preamble = 'Use multipart, Luke'

    html_part = MIMEText(html, 'html', 'utf-8')
    msg.attach(html_part)

    log.debug('--------------------------------------------------')
    debug_data = '''
        SEND NOTIFICATION:
        Subject: {subject}
        To: {to}

        {body}
        '''.format(subject=subject, to=msg['To'], body=html)
    log.debug(debug_data)
    log.debug('--------------------------------------------------')

    with SMTP(smtp_server) as smtp:
        smtp.send_message(msg)


class Notification:
    """
    Object represents notification object
    """
    to = None
    request = None
    params = None

    def send(self):

        if not enable_email:
            log.debug('mail sending is not allowed in config')
            return

        sender = get_config('notifications_from_email')
        Process(target=send_email_process, args=(self.request, self.template_name, 
            [self.to], sender, self.params)).start()

    def __init__(self, template_name, to, params, request=None):
        self.to = to
        self.template_name = template_name
        self.params = params

        if request is None:
            request = threadlocal.get_current_request()

        self.request = request


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

    comment_date = h.timestamp_to_str(comment.published)
    res = {
        'comment_author_email': author_email,
        'comment_author_name': author_name,
        'comment_text': comment.body,
        'comment_date': comment_date,
        'comment_url': comment_url
        }
    return res


def _extract_article_sub(request, article):
    """
    Extract placeholders substitution strings from the article object
    """
    article_url = h.article_url(request, article)

    res = {
        'article_title': article.title,
        'article_url': article_url
        }
    return res


def gen_comment_response_notification(request, article, comment, top_comment, email):
    """
    Generate comment answer notification
    """

    email = normalize_email(email)
    if not email:
        return None

    # placeholders replacements
    params = {
        'site_title': get_config('site_title')
    }
    params.update(_extract_comment_sub(request, comment))
    params.update(_extract_article_sub(request, article))

    n = Notification('comment_response', email, params, request=request)

    return n


def gen_email_verification_notification(request, email, verification_code):
    """
    Generate email address verification notification.
    """

    email = normalize_email(email)
    if not email:
        return None

    # placeholders replacements
    base_url = get_config('site_base_url')
    q = urllib.parse.urlencode({'token': verification_code, 'email': email})
    verify_url = base_url + '/verify-email?' + q
    params = {
        'site_title': get_config('site_title'),
        'email': email,
        'verify_url': verify_url
    }

    n = Notification('email_verification', email, params, request=request)

    return n


def gen_new_comment_admin_notification(request, article, comment):
    """
    Generate new comment notification for the administrator.
    """
    email = normalize_email(get_config('admin_notifications_email'))
    if not email:
        return None

    # placeholders replacements
    params = {
        'site_title': get_config('site_title')
    }
    params.update(_extract_comment_sub(request, comment))
    params.update(_extract_article_sub(request, comment.article))

    n = Notification('admin_new_comment', email, params, request=request)

    return n
