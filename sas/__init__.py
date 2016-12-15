# from .functions import login
import ssl
import requests
import json

# local imports
from settings import Settings
import functions

_session = requests.Session()

def run(settingsPath):
    testConfigObjects = json.load(open(settingsPath))
    for testConfig in testConfigObjects:
        call(Settings(testConfig))

def _login(loginUrl, hiddenParams, settings):
    params = {
        '_service': 'default',
        'ux': settings.get('loginParams.username'),
        'px': settings.get('loginParams.password'),
        # for SAS 9.4,
        'username': settings.get('loginParams.username'),
        'password': settings.get('loginParams.password')
    }
    params.update(hiddenParams)

    req = _session.post(functions.getHostUrl(settings.get('execUrl')) + loginUrl, params, verify=False)
    return not(functions.needToLogin(req.text))

def call(settings):
    req = _session.post(settings.get('execUrl'), settings.get('execParams'), verify=False)

    if functions.needToLogin(req.text):
        loginUrl = functions.getLoginUrl(req.text)
        hiddenParams = functions.getHiddenParams(req.text)
        if _login(loginUrl, hiddenParams, settings):
            print('Login successful')
            call(settings)
    else:
        print(req.text)
