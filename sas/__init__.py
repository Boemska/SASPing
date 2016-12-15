# from .functions import login
import ssl
import requests

# local imports
import settings
import functions


_session = requests.Session()

def _login(loginUrl, hiddenParams):
    params = {
        '_service': 'default',
        'ux': settings.get('username'),
        'px': settings.get('password'),
        # for SAS 9.4,
        'username': settings.get('username'),
        'password': settings.get('password')
    }
    params.update(hiddenParams)

    req = _session.post(functions.getHostUrl() + loginUrl, params, verify=False)
    return not(functions.needToLogin(req.text))

def call():
    params = {'_program': settings.get('program')}
    req = _session.post(settings.get('execUrl'), params, verify=False)

    if functions.needToLogin(req.text):
        loginUrl = functions.getLoginUrl(req.text)
        hiddenParams = functions.getHiddenParams(req.text)
        if _login(loginUrl, hiddenParams):
            print('Login successful')
            call()
    else:
        print(req.text)
