import ssl
import requests
import sys
import re
import time

# local imports
from settings import Settings
from response import Response
import functions

_session = requests.Session()

def run(testConfigObjects):
    testsData = []
    for settings in [Settings(testConfig) for testConfig in testConfigObjects]:
        startTime = time.time()
        response = call(settings)
        response.addTime(startTime, str(round(time.time() - startTime, 3)) + ' seconds')
        testsData.append(dict(response))

    return testsData

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

    try:
        req = _session.post(functions.getHostUrl(settings.get('execUrl')) + loginUrl, params, timeout=30)
        return req.status_code == 200 and not(functions.needToLogin(req.text))
    except requests.exceptions.Timeout:
        return False

def call(settings, afterLogin=False):
    try:
        req = _session.post(settings.get('execUrl'), settings.get('execParams'), timeout=30)
    except requests.exceptions.Timeout:
        return Response('fail', None, None,'Request timeout').setId(settings.get('id'))
    except requests.exceptions.ConnectionError:
        return Response('fail', None, None,'Name or service not known').setId(settings.get('id'))
    except requests.exceptions.RequestException as e:
        return Response('fail', None, None, str(e)).setId(settings.get('id'))

    if req.status_code != 200:
        return Response('fail', None, None, 'Request failed - status ' + req.status_code).setId(settings.get('id'))

    if functions.needToLogin(req.text):
        loginUrl = functions.getLoginUrl(req.text)
        hiddenParams = functions.getHiddenParams(req.text)
        if _login(loginUrl, hiddenParams, settings):
            return call(settings, True)
        else:
            return Response('fail', None, None,'Failed login').setId(settings.get('id'))
    else:
        # (0|1,) - true or false for "had to login" in csv
        response = functions.validateResponse(req.text, settings.get('validations'))
        if afterLogin:
            response.setHadToLoginFlag()
        return response.setId(settings.get('id'))
