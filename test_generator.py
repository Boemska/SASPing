#!/usr/bin/python

import sys
import getopt
import time
import csv
import os
from random import getrandbits, randint
from sas.response import Response

try:
    opts, args = getopt.getopt(sys.argv[1:], 's:i:m:t:a:o:h', ['start=', 'interval=', 'maximum=', 'tests=', 'apps=', 'output=', 'help'])
except getopt.GetoptError:
    sys.stdout.write('\npython test_generator.py -s [start timestamp] -i [interval] -m [maximum] -t [number of tests] -a [number of apps] -o [output dir]\n')
    sys.stdout.write('\nRun `python test_generator.py --help` or check the Readme file\n\n')
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        sys.stdout.write('\nThe script will generate tests every X seconds based on the interval argument starting from S timestamp.\n')
        sys.stdout.write('\nMandatory arguments:\n')
        sys.stdout.write('\t-s, --start        Start timestamp. Generated data will start from this timestamp.\n')
        sys.stdout.write('\t-i, --interval     Interval in seconds between consecutive tests.\n')
        sys.stdout.write('\t-m, --maximum      Maximum number of tests. The script will stop if the number of tests exceeds this argument.\n')
        sys.stdout.write('\t-t, --tests        Number of tests in one round (an execution of the collector script).\n')
        sys.stdout.write('\t-a, --apps         Number of dummy applications.\n')
        sys.stdout.write('\t-o, --output       Output directory (sasping_data.csv file will be saved there).\n')
        sys.exit(0)
    elif opt in ('-s', '--start'):
        fromTimestamp = int(arg)
    elif opt in ('-i', '--interval'):
        interval = int(arg)
    elif opt in ('-m', '--maximum'):
        maximum = int(arg)
    elif opt in ('-t', '--tests'):
        testsPerRun = int(arg)
    elif opt in ('-a', '--apps'):
        appsCount = int(arg)
    elif opt in ('-o', '--output'):
        outputPath = arg

if len(opts) < 6:
    sys.stdout.write('\npython test_generator.py -s [start timestamp] -i [interval] -m [maximum] -t [number of tests] -a [number of apps] -o [output dir]\n')
    sys.stdout.write('\nRun `python test_generator.py --help` or check the Readme file\n\n')
    sys.exit(2)

currentTimestamp = int(time.time())
run = 0

out = []

while(fromTimestamp + (interval * run) < currentTimestamp and (maximum > 0 and run < maximum)):
    # login request
    response = Response(
        'sasping login request',
        'success',
        timestamp=fromTimestamp + (interval * run),
        execTime=float(randint(50, 3000))/1000,
        programExecTime=fromTimestamp + (interval * run)
    )
    out.append(dict(response))

    for i in range(testsPerRun-1):
        testStatus = 'success' if randint(0, 9) != 9  else 'fail'
        failGroup = 'mustContain' if bool(getrandbits(1)) else 'cantContain'
        response = Response(
            'test ' + str(i),
            testStatus,
            failGroup if testStatus == 'fail' else None,
            'str' if testStatus == 'fail' else None,
            'fail message' if testStatus == 'fail' else None,
            fromTimestamp + (interval * run),
            float(randint(50, 3000))/1000,
            False,
            'test app ' + str(randint(1, appsCount)),
            fromTimestamp + (interval * run)
        )
        out.append(dict(response))
    run += 1

keys = Response.getKeys()
csvFilePath = os.path.join(outputPath, 'sasping_data.csv')
with open(csvFilePath, "w") as outFile:
    writer = csv.DictWriter(outFile, keys)
    #writeheader not supported in old versions, so we are using this hack
    writer.writerow(dict((k, k) for k in keys))
    writer.writerows(out)
    print('\nCreated file {0} with {1} rows\n'.format(csvFilePath, len(out)))
