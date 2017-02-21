from base import Base

class Settings(Base):
    _keys = [
        # key, required
        ('hostUrl', True),
        ('loginPath', True),
        ('loginParams', True),
        ('loginParams.username', True),
        ('loginParams.password', True),
        ('applications', True)
    ]

    def __init__(self, data):
        super(Settings, self).__init__(data)
        # remove last slash because loginPath and execPath should start with slash
        if self.get('hostUrl')[-1] == '/':
            self.set('hostUrl', self.get('hostUrl')[0:-1])
        if self.get('loginPath')[0] != '/':
            raise ValueError('Login path must start with /');
        if len(self.get('applications')) == 0:
            raise ValueError("Property 'applications' cannot be empty")
        for app in self.get('applications'):
            if not('name' in app):
                raise KeyError("Missing required 'application.name' property")
            if not('tests' in app):
                raise KeyError("Missing required 'application.tests' property")
            if not(app['name']):
                raise ValueError("Application property 'name' cannot be empty")
            if not(app['tests']) or len(app['tests']) == 0:
                raise ValueError("Application property 'tests' cannot be empty")
            # tests are validated in test.py

    def getLoginUrl(self):
        return self.get('hostUrl') + self.get('loginPath')
