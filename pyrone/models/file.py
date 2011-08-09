"""File model"""
from time import time
import uuid
import os

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, Boolean

from . import Base

class File(Base):
    __tablename__ = 'storagefile'
    
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    content_type = Column(String)
    size = Column(Integer)
    dltype = Column(String) # "download"|"auto"
    etag = Column(String)
    updated = Column(Integer)
    
    def __init__(self):
        self.etag = str(uuid.uuid4())
        self.dltype = 'auto'
        self.updated = int(time())
        
allowed_dltypes = ('auto', 'download')
        
def get_storage_dirs():
    storage_dir = config['pyrone_storage_dir']
    # create if required
    if not os.path.exists(storage_dir):
        os.mkdir(storage_dir)
    
    subdirs = ('orig', 'img_preview_mid')
    res = dict()
    for s in subdirs:
        path = os.path.join(storage_dir, s)
        res[s] = path
        if not os.path.exists(path):
            os.mkdir(path)
    
    # TODO: also check that dir is a really dir
    
    return res

def get_backups_dir():
    storage_dir = config['pyrone_storage_dir']
    backups_dir = os.path.join(storage_dir, 'backups')
    
    if not os.path.exists(storage_dir):
        os.mkdir(storage_dir)
        
    if not os.path.exists(backups_dir):
        os.mkdir(backups_dir)
    
    return backups_dir