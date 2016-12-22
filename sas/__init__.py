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
    try:
        for testConfig in testConfigObjects:
            startTime = time.time()
            response = call(Settings(testConfig))
            response.addTime(startTime, str(round(time.time() - startTime, 3)) + ' seconds')
            testsData.append(dict(response))
    # KeyError throw by Settings class if configuration is not ok
    except KeyError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('Please read the documentation and fix errors.\n')
        sys.stderr.write('Error message: {0}\n\n'.format(str(e)))
        print 'Test {0} failed because of the wrong config object\n'.format(testConfig['id'])
        sys.exit(1)

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
        return ('fail', None, None,'Request timeout', 0)

    if req.status_code != 200:
        return ('fail', None, None, 'Request failed - status ' + req.status_code, 0)

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
