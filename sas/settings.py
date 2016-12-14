import sys
import json

if len(sys.argv) < 5:
    try:
        data = json.load(open('settings.json'))
    except IOError:
        data = None
        sys.stderr.write('Please read documentation and add valid data.')
        print('') #for new row
        sys.exit(1)
else:
    data = {
        'execUrl' : sys.argv[1],
        'program' : sys.argv[2],
        'username': sys.argv[3],
        'password': sys.argv[4]
    }

def _validateKey(key):
    if not(key in ['execUrl', 'program', 'username', 'password']):
        raise KeyError('Wrong settings key')


def getAll():
    return data

def get(key):
    _validateKey(key)
    return data[key]

def set(key, value):
    _validateKey(key)
    data[key] = value
