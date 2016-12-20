#!/usr/bin/python

import sys
import json
import csv

import sas

def main():
    #python main.py [settings.json path]
    if len(sys.argv) < 3:
        print('') #for new row
        sys.stderr.write('Missing arguments. Please read documentation and try again.')
        print('') #for new row
        sys.exit(1)

    try:
        testConfigObjects = json.load(open(sys.argv[1]))
        testsData = sas.run(testConfigObjects)

        # CSV file headers - "id, status, which test failed, failed pattern, message, had to login, time of execution, execution duration"
        with open(sys.argv[2], "a") as outFile:
            writer = csv.writer(outFile)
            writer.writerows(testsData)
    except ValueError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('\nInvalid json with message: {0}\n\n'.format(str(e)))
        sys.exit(1)
    except IOError as e:
        sys.stderr.write('\n{0}\n\n'.format(str(e)))
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
