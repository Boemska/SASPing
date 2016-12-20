import ssl
import requests
import json
import sys
import re
import time
import csv

# local imports
from settings import Settings
import functions

_session = requests.Session()

def run(settingsPath, outputPath):
    try:
        testConfigObjects = json.load(open(settingsPath))
        # TODO: validate if all ids are unique
        testsData = []
        for testConfig in testConfigObjects:
            startTime = time.time()
            status = call(Settings(testConfig))
            testsData.append(status + (startTime, str(round(time.time() - startTime, 3)) + ' seconds'))

        # CSV file headers - "status, which test failed, failed pattern, message, had to login, time of execution, execution duration"
        with open(outputPath, "a") as outFile:
            writer = csv.writer(outFile)
            writer.writerows(testsData)

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
    except IOError as e:
        sys.stderr.write('\n{0}\n\n'.format(str(e)))
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

def call(settings, afterLogin=False):
    req = _session.post(settings.get('execUrl'), settings.get('execParams'), verify=False)

    if functions.needToLogin(req.text):
        loginUrl = functions.getLoginUrl(req.text)
        hiddenParams = functions.getHiddenParams(req.text)
        if _login(loginUrl, hiddenParams, settings):
            return call(settings, True)
        else:
            return ('fail', None, None,'Failed login')
    else:
        # (0|1,) - true or false for "had to login" in csv
        return functions.validateResponse(req.text, settings.get('validations')) + (1 if afterLogin else 0,)
