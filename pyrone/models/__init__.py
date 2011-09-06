"""
This module contains SQLAlchemy models
"""
__all__ = ['Base', 'DBSession']

import logging
import transaction

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    ## Initialization code here
    try:
        transaction.begin() 
        
        dbsession = DBSession()
        setup_config(dbsession)
        user_setup(dbsession)
        
        transaction.commit()
    except IntegrityError:
        log.debug('SOMETHING WRONG WITH INIT DB')
        transaction.abort()
    
from user import User, Permission, VerifiedEmail
from config import Config
from article import Article, Comment, Tag
from file import File
from .setup.config import setup as setup_config
from .setup.user import setup as user_setup