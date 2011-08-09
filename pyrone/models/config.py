"""Config model, store site global options"""
import logging

from sqlalchemy import Column
from sqlalchemy.types import String, UnicodeText

from . import Base

log = logging.getLogger(__name__)

class Config(Base):
    __tablename__ = 'config'
    
    id = Column(String(50), primary_key=True)
    value = Column(UnicodeText)

    def __init__(self, id, value):
        self.id = id
        self.value = value

def get_all():
    all = Session.query(Config).all()
    return all

def get(id):
    # TODO: cache values?
    cv = Session.query(Config).get(id)
    return cv

def set(id, value, commit=True):
    cv = Session.query(Config).get(id)
    if cv is None:
        cv = Config(id, value)
        Session.add(cv)
    else:
        cv.value = value
        
    if commit:
        Session.commit()
    