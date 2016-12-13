import re
from urlparse import urlparse
from .settings import getSettings

formPatt = '<form.+action="(.*Logon[^"]*).*>'

def needToLogin(responseHtml):
    matches = re.search(formPatt, responseHtml)
    if matches:
        return True
    else:
        # there's no form, we are in. hooray!
        return False

def getLoginUrl(responseHtml):
    matches = re.search(formPatt, responseHtml)
    return re.sub('\?.*', '', matches.group(1))

def getHostUrl():
    result = urlparse(getSettings()['execUrl'])
    return result.scheme + '://' + result.netloc

def getHiddenParams(responseHtml):
    matches = re.findall('<input.*"hidden"[^>]*>', responseHtml)
    if matches != None:
        params = {}
        for match in matches:
            subMatch = re.search('name="([^"]*)"\svalue="([^"]*)', match)
            params[subMatch.group(1)] = subMatch.group(2)
        return params
