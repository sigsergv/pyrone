"""Config model, store site global options"""
import logging
import pytz
import transaction

from sqlalchemy import Column
from sqlalchemy.types import String, UnicodeText

from . import Base, DBSession

log = logging.getLogger(__name__)

class Config(Base):
    __tablename__ = 'pbconfig'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    
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
            v = c.value
            if id == 'timezone':
                v = pytz.timezone(v)
            _cache[id] = v
                
        
    return _cache[id]

def set(id, value, dbsession=None):
    is_transaction = False
    
    if dbsession is None:
        dbsession = DBSession()
        is_transaction = True
        transaction.begin()
        
    c = dbsession.query(Config).get(id)
    if c is None:
        c = Config(id, value)
        dbsession.add(c)
    else:
        c.value = value
    
    if is_transaction:
        transaction.commit()

    #if commit:
    #    Session.commit()
    
def clear_cache():
    _cache.clear()