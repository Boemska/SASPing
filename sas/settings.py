import sys
import json

if len(sys.argv) < 5:
    try:
        settings = json.load(open('settings.json'))
    except IOError:
        settings = None
        sys.stderr.write('Please read documentation and add valid settings.')
        print('') #for new row
        sys.exit(1)
else:
    settings = {
        'execUrl' : sys.argv[1],
        'program' : sys.argv[2],
        'username': sys.argv[3],
        'password': sys.argv[4]
    }

def getSettings():
    return settings
