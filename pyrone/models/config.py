"""Config model, store site global options"""
import logging
import pytz
import transaction

from sqlalchemy import Column
from sqlalchemy.types import String, UnicodeText

from . import Base, DBSession

try:
    import cPickle as pickle
except ImportError:
    import pickle

UWSGI = False
try:
    import uwsgi
    UWSGI = True
except ImportError:
    pass

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

def cache_set(key, value):
    if UWSGI:
        if uwsgi.cache_exists(key):
            uwsgi.cache_update(key, pickle.dumps(value))
        else:
            uwsgi.cache_set(key, pickle.dumps(value))
    else:
        _cache[key] = value

def cache_get(key):
    value = None
    if UWSGI:
        value = uwsgi.cache_get(key)
        if value is not None:
            value = pickle.loads(value)
    else:
        if key in _cache:
            value = _cache[key]

    return value

# config values are cached

def get_all():
    """
    Fetch all config options, not cached
    """
    dbsession = DBSession()
    all = dbsession.query(Config).all()
    return all

def get(key, force=False):
    """
    Get settings value, set "force" to True to update corresponding value in the cache
    """
    value = cache_get(key)
    if value is None or force==False:
        dbsession = DBSession()
        c = dbsession.query(Config).get(key)
        if c is not None:
            v = c.value
            if key == 'timezone':
                v = pytz.timezone(v)
            cache_set(key, v)
        
    return cache_get(key)

def set(key, value, dbsession=None):
    is_transaction = False
    
    if dbsession is None:
        dbsession = DBSession()
        is_transaction = True
        transaction.begin()
        
    c = dbsession.query(Config).get(key)
    if c is None:
        c = Config(key, value)
        dbsession.add(c)
    else:
        c.value = value
    
    if is_transaction:
        transaction.commit()

    cache_set(key, value)
