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

# do nothing, just create function because of the interface
def _logger(s):
    pass

def run(config, debug):
    global _settings, _logger
    programExecTime = time.time()
    outData = []
    _settings = Settings(config)

    if debug == True:
        _logger = sys.stdout.write
    elif type(debug) == str:
        try:
            logFile = open(debug, "a")
            _logger = logFile.write
        except:
            print('\nCannot open log file. Debug flag ignored.')

    try:
        startTime = time.time()
        loginStatus = login()
        if not(loginStatus):
            loginResponse = Response('sasping login request', 'fail', 'Failed to login.')
        else:
            loginResponse = Response('sasping login request', 'success')
    except requests.exceptions.Timeout as err:
        loginResponse = Response('sasping login request', 'fail', message='Request timeout')
    finally:
        loginResponse.setTime(startTime, time.time() - startTime)
        loginResponse.setProgramExecTime(programExecTime)
        if loginResponse.status == 'fail':
            return [dict(loginResponse)]

    # get request to do sas security check
    # this request is not logged to csv file
    try:
        _session.get(_settings.get('hostUrl') + Test(_settings.get('applications')[0]['tests'][0]).get('execPath'))
    except Exception:
        raise RuntimeError('SAS security check request failed')

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
            except Exception as e:
                response = Response(test.get('id'), 'fail', message=str(e))
            finally:
                response.setTime(startTime, time.time() - startTime)
                response.setAppName(app['name'])
                outData.append(dict(response.setProgramExecTime(programExecTime)))

    try:
        logFile.close()
    finally:
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
    debugStr = '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
    debugStr += req.request.method + '\n'
    debugStr += req.url + '\n\n'
    debugStr += 'Request headers: ' + str(req.request.headers) + '\n\n'
    debugStr += 'Params: ' + req.request.body + '\n\n'
    debugStr += '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n'
    debugStr += 'Response status code: ' + str(req.status_code) + '\n\n'
    debugStr += 'Cookies: ' + str(_session.cookies.get_dict()) + '\n\n'
    debugStr += 'Response headers: ' + str(req.headers) + '\n\n'
    debugStr += req.text + '\n'

    _logger(debugStr)

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
