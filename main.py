import sys

import sas

def main():
    #python main.py [settings.json path]
    if len(sys.argv) < 2:
        print('') #for new row
        sys.stderr.write('File path missing')
        print('') #for new row
        sys.exit(1)

    sas.run(sys.argv[1])

if __name__ == '__main__':
    sys.exit(main())
