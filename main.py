#!/usr/bin/python

import sys
import json
import csv
import os
import re

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
        if sys.argv[2].endswith('.csv'):
            with open(sys.argv[2], "a") as outFile:
                writer = csv.DictWriter(outFile, keys)
                if outFile.tell() == 0:
                    writer.writeheader()
                writer.writerows(testsData)
                print 'Created file {0}\n'.format(sys.argv[2])
        elif sys.argv[2].endswith('.html'):
            testsArrays = [[test[key] for key in keys] for test in testsData];
            if os.path.isfile(sys.argv[2]):
                with open(sys.argv[2], 'r') as finput:
                    html = finput.read()
                    jsonData = re.search('<script>var data = (.+)<\/script>', html).group(1)
                    existingDataArray = json.loads(jsonData)
                    testsArrays = existingDataArray + testsArrays
                    finput.close()
            with open('./report/build/index.html', 'r') as finput:
                status = os.system('cd ./report && npm run build')
                if status == 0:
                    html = finput.read()
                    finput.close();
                else:
                    sys.stderr.write('\nError building index.html. Please try to run "npm run build" from "./reports" manually.\n\n')
                    sys.exit(1)
            with open(sys.argv[2], 'w') as foutput:
                # extract ordered values from testsData
                jsonOut = json.dumps(testsArrays)
                foutput.write(html.replace('<!-- data -->', '<script>var data = {0}</script>'.format(jsonOut)))
                foutput.close();
            print 'Created file {0}\n'.format(sys.argv[2])
        else:
            sys.stderr.write('\nWrong output format. Please read documentation and try again.\n\n')
            sys.exit(1)
    except IOError as e:
        sys.stderr.write('\n{0}\n\n'.format(str(e)))
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
