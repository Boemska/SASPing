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

    def getLoginUrl(self):
        return self.get('hostUrl') + self.get('loginPath')
