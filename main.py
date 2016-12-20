import sys

import sas

def main():
    #python main.py [settings.json path]
    if len(sys.argv) < 3:
        print('') #for new row
        sys.stderr.write('Missing arguments. Please read documentation and try again.')
        print('') #for new row
        sys.exit(1)

    sas.run(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    sys.exit(main())
