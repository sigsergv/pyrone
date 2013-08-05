from pyramid.security import Allow, Authenticated
#from pyramid.security import Everyone


class RootFactory(object):
    __acl__ = [
        # action, principal, permission
        (Allow, 'role:writer', 'write_article'),
        (Allow, 'role:editor', 'edit_article'),
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'role:admin', 'admin')
    ]

    def __init__(self, request):
        pass
