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
    except ValueError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('\nInvalid json with message: {0}\n\n'.format(str(e)))
        sys.exit(1)

    try:
        testsData = sas.run(testConfigObjects)
        keys = ['id', 'status', 'failed test group', 'failed pattern', 'message', 'timestamp', 'execution time', 'had to login']

        with open(sys.argv[2], "a") as outFile:
            writer = csv.DictWriter(outFile, keys)
            if outFile.tell() == 0:
                writer.writeheader()
            writer.writerows(testsData)
    except IOError as e:
        sys.stderr.write('\n{0}\n\n'.format(str(e)))
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
