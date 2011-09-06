"""Page model"""
from time import time
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, Boolean

from . import Base
from user import User
from pyrone.lib import markup

class Article(Base):
    __tablename__ = 'pbarticle'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
        
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    shortcut_date = Column(Unicode(50)) # somethig like "2011/03/29"
    shortcut = Column(Unicode(255)) # somrthing like "test-post-subject"
    title = Column(Unicode(255))
    body = Column(UnicodeText)
    rendered_preview = Column(UnicodeText)
    rendered_body = Column(UnicodeText)
    # UTC timestamp of publishing
    published = Column(Integer)
    # UTC timestamp of article update
    updated = Column(Integer)
    # cached comments number
    comments_total = Column(Integer, default=0)
    comments_approved = Column(Integer, default=0)
    is_commentable = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=True)
    is_splitted = Column(Boolean, default=False)
    
    comments = relation('Comment')
    user = relation('User')
    tags = relation('Tag')
    
    def __init__(self, shortcut='', title='', is_draft=True, is_commentable=True):
        self.shortcut = shortcut
        self.title = title
        self.is_commentable = is_commentable
        self.is_draft = is_draft
        
        self.published = int(time()) # UTC time
        self.updated = int(time()) # UTC time

    def set_body(self, body):
        """
        Set article body: parse, render, split into preview and complete parts etc
        """
        self.body = body
        preview, complete = markup.render_text_markup(body)
        self.rendered_preview = preview
        self.rendered_body = complete
        self.is_splitted = preview is not None
        
    def get_html_preview(self):
        if self.rendered_preview is None:
            return self.rendered_body
        else:
            return self.rendered_preview
        
class Tag(Base):
    __tablename__ = 'pbtag'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey(Article.id))
    tag = Column(Unicode(255))
    
    # we don't need explict reference to article
    
    def __init__(self, name, article):
        self.tag = name
        self.article_id = article.id
    
class Comment(Base):
    __tablename__ = 'pbarticlecomment'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    article_id = Column(Integer, ForeignKey(Article.id))
    parent_id = Column(Integer, ForeignKey(__tablename__+'.id'))
    display_name = Column(Unicode(255))
    email = Column(Unicode(255))
    website = Column(Unicode(255))
    body = Column(UnicodeText)
    rendered_body = Column(UnicodeText)
    published = Column(Integer)
    ip_address = Column(String(30))
    xff_ip_address = Column(String(30))
    is_approved = Column(Boolean, default=False)
    # uf True then all answers to this comment will be send to email
    is_subscribed = Column(Boolean, default=False)
    
    article = relation('Article')
    user = relation('User')
    parent = relation('Comment', remote_side=[id])
    
    def set_body(self, body):
        """
        Set comment body
        """
        self.body = body
        self.rendered_body = markup.render_text_markup_mini(body)
        
    def __init__(self):
        self.user_id = None
        self.published = int(time())
    