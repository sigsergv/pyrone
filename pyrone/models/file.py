"""File model"""
from time import time
import uuid
import os
import logging

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, Boolean

from . import Base

log = logging.getLogger(__name__)


class File(Base):
    __tablename__ = 'pbstoragefile'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    content_type = Column(String(50))
    size = Column(Integer)
    dltype = Column(String(10))  # "download"|"auto"
    etag = Column(String(50))
    updated = Column(Integer)

    def __init__(self):
        self.etag = str(uuid.uuid4())
        self.dltype = 'auto'
        self.updated = int(time())

allowed_dltypes = ('auto', 'download')

_storage_directory = False


def get_storage_dirs():
    # create if required
    if not os.path.exists(_storage_directory):
        os.mkdir(_storage_directory)

    subdirs = ('orig', 'img_preview_mid')
    res = {}
    for s in subdirs:
        path = os.path.join(_storage_directory, s)
        res[s] = path
        if not os.path.exists(path):
            os.mkdir(path)

    # TODO: also check that dir is a really dir

    return res


def get_backups_dir():
    backups_dir = os.path.join(_storage_directory, 'backups')

    if not os.path.exists(_storage_directory):
        os.mkdir(_storage_directory)

    if not os.path.exists(backups_dir):
        os.mkdir(backups_dir)

    return backups_dir


def init_storage_from_settings(settings):
    global _storage_directory
    # init storage directory settings['pyrone.storage_directory']
    _storage_directory = settings['pyrone.storage_directory']
    get_storage_dirs()
    get_backups_dir()
