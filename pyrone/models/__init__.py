"""This module contains SQLAlchemy models
"""

import logging
import transaction

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config
from zope.sqlalchemy import register as zope_sqlalchemy_register
from pyramid_beaker import session_factory_from_settings

log = logging.getLogger(__name__)

from .user import User, Role, VerifiedEmail
from .config import Config
from .article import Article, Comment, Tag
from .file import File


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager, request=None):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example:

      .. code-block:: python

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    This function may be invoked with a ``request`` kwarg, such as when invoked
    by the reified ``.dbsession`` Pyramid request attribute which is configured
    via the ``includeme`` function below. The default value, for backwards
    compatibility, is ``None``.

    The ``request`` kwarg is used to populate the ``sqlalchemy.orm.Session``'s
    "info" dict.  The "info" dict is the official namespace for developers to
    stash session-specific information.  For more information, please see the
    SQLAlchemy docs:
    https://docs.sqlalchemy.org/en/stable/orm/session_api.html#sqlalchemy.orm.session.Session.params.info

    By placing the active ``request`` in the "info" dict, developers will be
    able to access the active Pyramid request from an instance of an SQLAlchemy
    object in one of two ways:

    - Classic SQLAlchemy. This uses the ``Session``'s utility class method:

      .. code-block:: python

          from sqlalchemy.orm.session import Session as sa_Session

          dbsession = sa_Session.object_session(dbObject)
          request = dbsession.info["request"]

    - Modern SQLAlchemy. This uses the "Runtime Inspection API":

      .. code-block:: python

          from sqlalchemy import inspect as sa_inspect

          dbsession = sa_inspect(dbObject).session
          request = dbsession.info["request"]
    """
    dbsession = session_factory(info={'request': request})
    zope_sqlalchemy_register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize model and database
    """

    settings = config.get_settings()

    # hook to share the dbengine fixture in testing
    dbengine = settings.get('dbengine')
    if not dbengine:
        dbengine = engine_from_config(settings, 'sqlalchemy.')

    session_factory = get_session_factory(dbengine)
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    
    def dbsession(request):
        # hook to share the dbsession fixture in testing
        dbsession = request.environ.get('app.dbsession')
        if dbsession is None:
            # request.tm is the transaction manager used by pyramid_tm
            dbsession = get_tm_session(
                session_factory, request.tm, request=request
            )
        return dbsession

    config.add_request_method(dbsession, reify=True)