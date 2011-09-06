"""User model"""
import uuid

from hashlib import md5
from time import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation, eagerload
from sqlalchemy.types import String, Unicode, Integer, Boolean

from . import Base, DBSession

class User(Base):
    __tablename__ = 'pbuser'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    
    _str_permissions = None
    
    id = Column(Integer, primary_key=True)
    login = Column(String(255))
    password = Column(String(255))
    display_name = Column(Unicode(255))
    email = Column(Unicode(255))
    # user kind (class, type), possible values: "local", "twitter"
    kind = Column(String(20))
    
    permissions = relation('Permission')

    def has_permission(self, p):
        return p in self.get_permissions()
    
    def get_permissions(self):
        if self._str_permissions is None:
            self._str_permissions = [x.name for x in self.permissions]
            
        return self._str_permissions
    
class AnonymousUser:
    kind = 'anonymous'
    
    def has_permission(self, p):
        return False
    
anonymous = AnonymousUser()

class Permission(Base):
    __tablename__ = 'pbpermission'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('pbuser.id'))
    name = Column(String(50))
    
    def __init__(self, id, user_id, name):
        self.id = id
        self.user_id = user_id
        self.name = name
        
class VerifiedEmail(Base):
    __tablename__ = 'pbverifiedemail'
    __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')
    
    # stripperd lowcased email address
    id = Column(Integer, primary_key=True)
    email = Column(Unicode(255), unique=True)
    is_verified = Column(Boolean)
    last_verify_date = Column(Integer)
    verification_code = Column(String(255))
    
    def __init__(self, email):
        self.last_verify_date = int(time())
        self.email = email
        self.is_verified = False
        self.verification_code = str(uuid.uuid4())
        
def find_local_user(login, password):
    hashed_password = md5(password).hexdigest()
    dbsession = DBSession()
    q = dbsession.query(User).options(eagerload('permissions')).filter(User.kind=='local').\
        filter(User.login==login).filter(User.password==hashed_password)
    user = q.first()
    return user

def normalize_email(email):
    return email

#def get_user(user_id):
#    user = Session.query(User).options(eagerload('permissions')).get(user_id)
#    return user
    
def find_twitter_user(username):
    dbsession = DBSession()
    q = dbsession.query(User).options(eagerload('permissions')).filter(User.kind=='twitter').\
        filter(User.login==username)
    user = q.first()
    return user