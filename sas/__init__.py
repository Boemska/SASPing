import ssl
import requests
import json
import sys
import re
import time

# local imports
from settings import Settings
import functions

_session = requests.Session()

def run(settingsPath):
    try:
        testConfigObjects = json.load(open(settingsPath))
        # TODO: validate if all ids are unique
        testData = []
        for testConfig in testConfigObjects:
            startTime = time.time()
            status = call(Settings(testConfig))
            testData.append(status + (startTime, time.time() - startTime))

        print testData
    # KeyError throw by Settings class if configuration is not ok
    except KeyError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('Please read the documentation and fix errors.\n')
        sys.stderr.write('Error message: {0}\n\n'.format(str(e)))
        print 'Test {0} failed because of the wrong config object\n'.format(testConfig['id'])
        sys.exit(1)
    except ValueError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('\nInvalid json with message: {0}\n\n'.format(str(e)))
        sys.exit(1)

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
            return call(settings)
        else:
            return ('fail', None, None,'Failed login')
    else:
        return functions.validateResponse(req.text, settings.get('validations'))
