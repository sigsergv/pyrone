"""Config model, store site global options"""
import logging

from sqlalchemy import Column
from sqlalchemy.types import String, UnicodeText

from . import Base, DBSession

log = logging.getLogger(__name__)

class Config(Base):
    __tablename__ = 'config'
    
    id = Column(String(50), primary_key=True)
    value = Column(UnicodeText)

    def __init__(self, id, value):
        self.id = id
        self.value = value

# internal cache for setting values
_cache = dict()

# config values are cached

def get_all():
    dbsession = DBSession()
    all = dbsession.query(Config).all()
    return all

def get(id):
    if id not in _cache:
        dbsession = DBSession()
        c = dbsession.query(Config).get(id)
        if c is not None:
            _cache[id] = c.value
        
    return _cache[id]

def set(id, value, commit=True):
    dbsession = DBSession()
    c = dbsession.query(Config).get(id)
    if c is None:
        c = Config(id, value)
        dbsession.add(c)
    else:
        c.value = value
        
    #if commit:
    #    Session.commit()
    