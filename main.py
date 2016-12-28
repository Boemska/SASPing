#!/usr/bin/python

import sys
import json
import csv
import os
import re
from shutil import copyfile

import sas

def main():
    #python main.py [settings.json path]
    if len(sys.argv) < 3:
        sys.stderr.write('\nMissing arguments. Please read documentation and try again.\n\n')
        sys.exit(1)

    try:
        testConfigObjects = json.load(open(sys.argv[1]))
    except ValueError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('\nInvalid json with message: {0}\n\n'.format(str(e)))
        sys.exit(1)

    try:
        testsData = sas.run(testConfigObjects)
    # KeyError throw by Settings class if configuration is not ok
    except KeyError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('Please read the documentation and fix errors.\n')
        sys.stderr.write('Error message: {0}\n\n'.format(str(e)))
        sys.exit(1)

    try:
        keys = ['id', 'status', 'failed test group', 'failed pattern', 'message', 'timestamp', 'execution time', 'had to login']
        if not(os.path.isdir(sys.argv[2])):
            sys.stderr.write('\nWrong output path. Please check if the dir exists.\n\n')
            sys.exit(1)
        csvFilePath = os.path.join(sys.argv[2], 'sasping_data.csv')
        indexFilePath = os.path.join(sys.argv[2], 'index.html')
        csvFileExists = os.path.isfile(csvFilePath)
        with open(csvFilePath, "a") as outFile:
            writer = csv.DictWriter(outFile, keys)
            if outFile.tell() == 0:
                writer.writeheader()
            writer.writerows(testsData)
            if csvFileExists:
                print('Updated file {0}\n'.format(indexFilePath))
            else:
                print('Created file {0}\n'.format(indexFilePath))

            buildStatus = os.system('cd ./report && npm run build')
            if buildStatus != 0:
                sys.stderr.write('\nError building index.html. Please try to run "npm run build" from "./reports" manually.\n\n')
                sys.exit(1)
            copyfile('./report/build/index.html', indexFilePath)
    except IOError as e:
        sys.stderr.write('\n{0}\n\n'.format(str(e)))
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
