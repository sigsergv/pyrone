"""This module contains SQLAlchemy models
"""
#__all__ = ['Base', 'DBSession']

import logging
import transaction

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

log = logging.getLogger(__name__)

# create session factory
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

from .user import User, Role, VerifiedEmail
from .config import Config
from .article import Article, Comment, Tag
from .file import File
