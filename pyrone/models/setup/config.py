## -*- coding: utf-8 -*-
from ..config import Config

data = [
    ['site_title', u'Pyrone Blog Engine'],
    ['site_copyright', u'© 2011 Blog Author'],
    ['site_style', 'default'],
    ['elements_on_page', u'10'],
    ['timezone', u'Asia/Novosibirsk'],
    ['site_base_url', 'http://127.0.0.1:5000'],
    ['admin_notifications_email', 'test@example.org'],
    ['admin_notify_new_comments', 'false'],
    ['admin_notify_new_user', 'false'],
    ['verification_msg_sibject_tpl', 'Verify your email address'],
    ['verification_msg_body_tpl', 'Verification email body.'],
    ['comment_answer_msg_subject_tpl', '{visitor} is answered on subscribed message on site {site_title}'],
    ['comment_answer_msg_body_tpl', '{visitor} is answered on subscribed message on site {site_title}. Answer is:\n\n{answer_body}'],
    ['image_preview_width', '300'],
    ['tw_consumer_key', 'XXXXXXXXXXXXXXXXX'],
    ['tw_consumer_secret', 'YYYYYYYYYYYYYYYYYY']
    ]

def setup(dbsession):
    print "Setup model 'Config'"
    
    for r in data:
        config = dbsession.query(Config).get(r[0])
        if config is None:
            config = Config(*r)
            dbsession.add(config)

