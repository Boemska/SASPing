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
    programExecTime = time.time()
    outData = []
    _settings = Settings(config)
    try:
        startTime = time.time()
        loginStatus = login()
        loginTime = round(time.time() - startTime, 3)
        loginResponse = Response('sasping login request', 'success', timestamp=time.time(), execTime=(str(loginTime) + ' seconds'))
        if not(loginStatus):
            raise RuntimeError('Failed to login.')
    except requests.exceptions.Timeout as err:
        loginResponse = Response('sasping login request', 'fail', message='Request timeout')
    except Exception as err:
        loginResponse = Response('sasping login request', 'fail', message=str(err))
    finally:
        loginResponse.setTime(startTime, str(round(time.time() - startTime, 3)) + ' seconds')

    outData.append(dict(loginResponse.setProgramExecTime(programExecTime)))
    applications = _settings.get('applications')
    for app in applications:
        for test in [Test(testConfig) for testConfig in app['tests']]:
            try:
                startTime = time.time()
                response = call(test)
            except requests.exceptions.Timeout:
                response = Response(test.get('id'), 'fail', message='Request timeout')
            except requests.exceptions.ConnectionError:
                response = Response(test.get('id'), 'fail', message='Name or service not known')
            except requests.exceptions.RequestException as e:
                response = Response(test.get('id'), 'fail', message=str(e))
            finally:
                response.setTime(startTime, str(round(time.time() - startTime, 3)) + ' seconds')
                response.setAppName(app['name'])
                outData.append(dict(response.setProgramExecTime(programExecTime)))

    return outData

def login():
    req = _session.get(_settings.getLoginUrl(), timeout=30)
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

    req = _session.post(_settings.getLoginUrl(), params, timeout=30)
    return req.status_code == 200 and not(functions.needToLogin(req.text))

def call(test, afterLogin=False):
    req = _session.post(_settings.get('hostUrl') + test.get('execPath'), test.get('execParams'), timeout=30)

    if req.status_code != 200:
        return Response(test.get('id'), 'fail', message='Request failed - status ' + str(req.status_code))

    if functions.needToLogin(req.text):
        hiddenParams = functions.getHiddenParams(req.text)
        if _login(loginUrl, hiddenParams):
            return call(test, True)
        else:
            return Response(test.get('id'), 'fail', message='Failed login')
    else:
        # (0|1,) - true or false for "had to login" in csv
        response = functions.validateResponse(req.text, test.get('id'), test.get('validations'))
        if afterLogin:
            response.setHadToLoginFlag()
        return response
