# -*- coding: utf-8 -*-
"""
Notifications
"""

import logging

#from pylons import app_globals as g

log = logging.getLogger(__name__)

class Notification:
    """
    Object represents notification object
    """
    subject = None
    body = None
    
    def send(self):
        log.debug('SEND NOTIFICATION')
    
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body

def gen_comment_response_notification(email, comment, top_comment):
    # generate notification using templates
    subject_tpl = g.get_config('comment_answer_msg_subject_tpl')
    body_tpl = g.get_config('comment_answer_msg_body_tpl')
    
    subject = ''
    body = ''
    
    n = Notification(subject, body)
    # u'notification to “%s” for comment “%s”' % (email, comment.id)
    return n

def gen_email_verification_notification(email):
    subject = ''
    body = ''
    n = Notification(subject, body)
    
    return n