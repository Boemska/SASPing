import re
from urlparse import urlparse
from response import Response

# local imports

_formPatt = '<form.+action="(.*Logon[^"]*).*>'

def needToLogin(responseHtml):
    matches = re.search(_formPatt, responseHtml)
    if matches:
        return True
    else:
        # there's no form, we are in. hooray!
        return False

def getLoginUrl(responseHtml):
    matches = re.search(_formPatt, responseHtml)
    return re.sub('\?.*', '', matches.group(1))

def getHostUrl(fromUrl):
    result = urlparse(fromUrl)
    return result.scheme + '://' + result.netloc

def getHiddenParams(responseHtml):
    matches = re.findall('<input.*"hidden"[^>]*>', responseHtml)
    if matches != None:
        params = {}
        for match in matches:
            subMatch = re.search('name="([^"]*)"\svalue="([^"]*)', match)
            params[subMatch.group(1)] = subMatch.group(2)
        return params

def validateResponse(responseHtml, validations):
    # validation return tuple - (status, which test failed, failed pattern, message)
    for validationGroup in ['mustContain', 'cantContain']:
        for validationPatt in validations[validationGroup]:
            if not(re.search(validationPatt, responseHtml)):
                return Response('fail', validationGroup, validationPatt)
    return Response('success')
