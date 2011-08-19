from pyramid.security import Allow, Authenticated
#from pyramid.security import Everyone

class RootFactory(object):
    __acl__ = [ 
               # action, principal, permission
               # in our case principal==permission name
               (Allow, 'write_article', 'write_article'),
               (Allow, Authenticated, 'authenticated'),
               (Allow, 'admin', 'admin')
                ]
    
    def __init__(self, request):
        pass