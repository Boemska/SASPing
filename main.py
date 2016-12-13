import sys

from sas.settings import getSettings
from sas import Sas

def main():
    #python main.py [url] [program] [username] [password]
    settings = getSettings()
    adapter = Sas(settings['execUrl'])
    adapter.call(settings['program'])

if __name__ == '__main__':
    sys.exit(main())
