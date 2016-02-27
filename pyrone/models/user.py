"""User model"""
import uuid
import hashlib

from time import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.types import String, Unicode, Integer, Boolean

from . import Base, DBSession


def md5(s):
    return hashlib.md5(s.encode('utf8')).hexdigest()


def sha1(s):
    return hashlib.sha1(s.encode('utf8')).hexdigest()


class User(Base):
    __tablename__ = 'pbuser'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    _str_roles = None

    id = Column(Integer, primary_key=True)
    login = Column(String(255))
    password = Column(String(255))
    display_name = Column(Unicode(255))
    email = Column(Unicode(255))
    # user kind (class, type), possible values: "local", "twitter"
    kind = Column(String(20))

    roles = relationship('Role')

    def detach(self):
        dbsession = Session.object_session(self)
        if dbsession is None:
            return

        for x in self.roles:
            dbsession.expunge(x)

        dbsession.expunge(self)

    def has_role(self, r):
        return r in self.get_roles()

    def get_roles(self):
        if self._str_roles is None:
            self._str_roles = [x.name for x in self.roles]

        return self._str_roles


class AnonymousUser:
    kind = 'anonymous'

    def has_role(self, r):
        return False

anonymous = AnonymousUser()


class Role(Base):
    __tablename__ = 'pbuserrole'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('pbuser.id'))
    name = Column(String(50))

    def __init__(self, id, user_id, name):
        self.id = id
        self.user_id = user_id
        self.name = name


class VerifiedEmail(Base):
    __tablename__ = 'pbverifiedemail'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

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
    hashed_password = md5(password)
    dbsession = DBSession()
    q = dbsession.query(User).options(joinedload('roles')).filter(User.kind == 'local').\
        filter(User.login == login)
    user = q.first()

    if user is None:
        return None

    if user.password == hashed_password:
        # old password hashing method is used
        return user
    else:
        # possibly a new method is used
        salt = user.password[:8]
        hashed_password = salt + sha1(salt + sha1(password))
        if user.password == hashed_password:
            return user

    return None


def normalize_email(email):
    return email


def get_user(user_id):
    dbsession = DBSession()
    user = dbsession.query(User).options(joinedload('roles')).get(user_id)
    return user


def find_twitter_user(username):
    dbsession = DBSession()
    q = dbsession.query(User).options(joinedload('roles')).filter(User.kind == 'twitter').\
        filter(User.login == username)
    user = q.first()
    return user
