"""User model"""
from hashlib import md5
from time import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation, eagerload
from sqlalchemy.types import String, Unicode, Integer, Boolean

from . import Base, DBSession
from pyrone.lib import notifications

class User(Base):
    __tablename__ = 'user'
    
    _str_permissions = None
    
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    display_name = Column(Unicode)
    email = Column(Unicode)
    # user kind (class, type), possible values: "local", "twitter"
    kind = Column(String)
    
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
    __tablename__ = 'permission'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String)
    
    def __init__(self, id, user_id, name):
        self.id = id
        self.user_id = user_id
        self.name = name
        
class VerifiedEmail(Base):
    __tablename__ = 'verifiedemail'
    
    # stripperd lowcased email address
    id = Column(Unicode, primary_key=True)
    is_verified = Column(Boolean)
    last_verify_date = Column(Integer)
    
    def __init__(self, email):
        self.last_verify_date = time()
        self.id = email
        is_verified = False
        
def find_local_user(login, password):
    hashed_password = md5(password).hexdigest()
    dbsession = DBSession()
    q = dbsession.query(User).options(eagerload('permissions')).filter(User.kind=='local').\
        filter(User.login==login).filter(User.password==hashed_password)
    user = q.first()
    return user

def verify_email(email):
    """
    Send email verification message if required
    """
    email = normalize_email(email)
    send = False
    
    vf = Session.query(VerifiedEmail).get(email)
    if vf is not None:
        diff = time.time() - vf.last_verify_date
        if diff > 86400:
            # delay between verifications requests must be more than 24 hours
            send = True
        vf.last_verify_date = time()
        Session.commit()
        
    else:
        send = True
        vf = VerifiedEmail(email)
        Session.add(vf)
        Session.commit()
    
    if send:
        notifications.gen_email_verification_notification(email)

def normalize_email(email):
    return email

def get_user(user_id):
    user = Session.query(User).options(eagerload('permissions')).get(user_id)
    return user
    
def find_twitter_user(username):
    q = Session.query(User).options(eagerload('permissions')).filter(User.kind=='twitter').\
        filter(User.login==username)
    user = q.first()
    return user