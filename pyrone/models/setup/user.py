## -*- coding: utf-8 -*-
from hashlib import md5

from ..user import User, Permission
from .. import DBSession

data_user = [
    # id, login, password, display name, email, kind, is admin
    [1, 'admin', md5('setup').hexdigest(), u'Blog admin', u'pyrone@example.com', 'local']
    ]

data_permissions = {
    1: ['write_article', 'edit_article', 'admin']
    }

def setup(xxx):
    print "Setup model 'User'"
    
    dbsession = DBSession()
    
    for r in data_user:
        user = dbsession.query(User).get(r[0])
        if user is None:
            user = User()
            user.id, user.login, user.password, user.display_name, \
                user.email, user.kind = r
            dbsession.add(user)

            if user.id in data_permissions:
                for p_str in data_permissions[user.id]:
                    p = Permission(None, user.id, p_str)
                    dbsession.add(p)
