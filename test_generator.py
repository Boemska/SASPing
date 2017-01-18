#!/usr/bin/python

import sys
import time
import csv
import os
from random import getrandbits, randint
from sas.response import Response

fromTimestamp = int(sys.argv[1])
interval      = int(sys.argv[2])
maximum       = int(sys.argv[3])
testsPerRun   = int(sys.argv[4])
appsCount     = int(sys.argv[5])
outputPath    = sys.argv[6]

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
        testStatus = 'success' if bool(getrandbits(1)) else 'fail'
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
