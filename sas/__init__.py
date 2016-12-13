# from .functions import login
import urllib
import urllib2
import ssl
import requests
from .settings import getSettings
from .functions import needToLogin, getLoginUrl, getHostUrl, getHiddenParams

unsecureContext = ssl._create_unverified_context()

class Sas:
    _execUrl = None

    def __init__(self, execUrl):
        self.session = requests.Session()
        self._execUrl = execUrl

    def _login(self, loginUrl, hiddenParams):
        settings = getSettings();
        params = {
            '_service': 'default',
            'ux': settings['username'],
            'px': settings['password'],
            # for SAS 9.4,
            'username': settings['username'],
            'password': settings['password']
        }
        params.update(hiddenParams)

        req = self.session.post(getHostUrl() + loginUrl, params, verify=False)
        return not(needToLogin(req.text))

    def call(self, program):
        params = {'_program': getSettings()['program']}
        req = self.session.post(self._execUrl, params, verify=False)

        if needToLogin(req.text):
            loginUrl = getLoginUrl(req.text)
            hiddenParams = getHiddenParams(req.text)
            if self._login(loginUrl, hiddenParams):
                print('Login successful')
                self.call(program)
        else:
            print(req.text)
