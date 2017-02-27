#!/usr/bin/python

import sys
import getopt
import json
import csv
import os
import re
from shutil import copyfile

import sas
from sas.response import Response

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:o:hd', ['settings=', 'debug=', 'output=', 'help'])
    except getopt.GetoptError:
        sys.stdout.write('\npython main.py -s [settings file path] -o [output dir]\n')
        sys.stdout.write('\nRun `python main.py --help` or check the Readme file\n\n')
        return 2

    if len(opts) == 0:
        return printHelp()

    debug = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            return printHelp()
        elif opt in ('-s', '--settings'):
            settingsPath = arg
        elif opt in ('-o', '--output'):
            outputPath = arg
        elif opt in ('--debug'):
            debug = True if arg == '' else arg

    if len(opts) < 2:
        sys.stdout.write('\npython main.py -s [settings file path] -o [output dir]\n')
        sys.stdout.write('\nRun `python main.py --help` or check the Readme file\n\n')
        return 2

    try:
        config = json.load(open(settingsPath))
    except ValueError as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('\nInvalid json with message: {0}\n\n'.format(str(e)))
        return 1

    try:
        testsData = sas.run(config, debug)
    # KeyError throw by Settings class if configuration is not ok
    except (KeyError, ValueError) as e:
        sys.stderr.write('\nThere is an error in settings.json.\n')
        sys.stderr.write('Please read the documentation and fix errors.\n')
        sys.stderr.write('Error message: {0}\n\n'.format(str(e)))
        return 1
    except RuntimeError as e:
        # RuntimeError is describing wrong workflow - the script should continue working after that
        sys.stderr.write('\nThere was an issue with message: {0}\n\n'.format(str(e)))

    try:
        keys = Response.getKeys()
        if not(os.path.isdir(outputPath)):
            sys.stderr.write('\nWrong output path. Please check if the dir exists.\n\n')
            return 1
        csvFilePath = os.path.join(outputPath, 'sasping_data.csv')
        csvFileExists = os.path.isfile(csvFilePath)
        with open(csvFilePath, "a") as outFile:
            writer = csv.DictWriter(outFile, keys)
            if outFile.tell() == 0:
                #writeheader not supported in old versions, so we are using this hack
                writer.writerow(dict((k, k) for k in keys))
            writer.writerows(testsData)
            if csvFileExists:
                print('\nUpdated file {0}\n'.format(csvFilePath))
            else:
                print('\nCreated file {0}\n'.format(csvFilePath))
    except IOError as e:
        sys.stderr.write('\n{0}\n\n'.format(str(e)))
        return 1

def printHelp():
    sys.stdout.write('\nCollect data about SAS services.\n')
    sys.stdout.write('\nMandatory arguments:\n')
    sys.stdout.write('\t-s, --settings        Settings JSON file path.\n')
    sys.stdout.write('\t-o, --output          Output directory (sasping_data.csv file will be saved there)\n\n')
    sys.stdout.write('\nOptional arguments:\n')
    sys.stdout.write('\t-d, --debug           Debug flag or file path.\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
