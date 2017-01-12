import ssl
import requests
import sys
import re
import time

# local imports
from config.settings import Settings
from config.test import Test
from response import Response
import functions

_session = requests.Session()
_settings = None

def run(config):
    global _settings
    _settings = Settings(config)
    if not(login()):
        raise RuntimeError('Failed to login.')
    applications = _settings.get('applications')
    testsData = []
    for app in applications:
        for test in [Test(testConfig) for testConfig in app['tests']]:
            startTime = time.time()
            response = call(test)
            response.setTime(startTime, str(round(time.time() - startTime, 3)) + ' seconds')
            response.setAppName(app['name'])
            testsData.append(dict(response))

    return testsData

def login():
    req = _session.get(_settings.getLoginUrl())
    hiddenParams = functions.getHiddenParams(req.text)
    return _login(hiddenParams)

def _login(hiddenParams):
    params = {
        '_service': 'default',
        'ux': _settings.get('loginParams.username'),
        'px': _settings.get('loginParams.password'),
        # for SAS 9.4,
        'username': _settings.get('loginParams.username'),
        'password': _settings.get('loginParams.password')
    }
    params.update(hiddenParams)

    try:
        req = _session.post(_settings.getLoginUrl(), params, timeout=30)
        return req.status_code == 200 and not(functions.needToLogin(req.text))
    except:
        return False

def call(test, afterLogin=False):
    try:
        req = _session.post(_settings.get('hostUrl') + test.get('execPath'), test.get('execParams'), timeout=30)
    except requests.exceptions.Timeout:
        return Response('fail', None, None,'Request timeout').setId(test.get('id'))
    except requests.exceptions.ConnectionError:
        return Response('fail', None, None,'Name or service not known').setId(test.get('id'))
    except requests.exceptions.RequestException as e:
        return Response('fail', None, None, str(e)).setId(test.get('id'))

    if req.status_code != 200:
        return Response('fail', None, None, 'Request failed - status ' + str(req.status_code)).setId(test.get('id'))

    if functions.needToLogin(req.text):
        hiddenParams = functions.getHiddenParams(req.text)
        if _login(loginUrl, hiddenParams):
            return call(test, True)
        else:
            return Response('fail', None, None,'Failed login').setId(test.get('id'))
    else:
        # (0|1,) - true or false for "had to login" in csv
        response = functions.validateResponse(req.text, test.get('validations'))
        if afterLogin:
            response.setHadToLoginFlag()
        return response.setId(test.get('id'))
