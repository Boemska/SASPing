#!/usr/bin/python

import sys
import os
import csv

from sas.response import Response
from sas.aggregator import Aggregator

inFilePath = sys.argv[1]
maxDatapoints = int(sys.argv[2]) if len(sys.argv) > 2 else 200

csvStrPos = inFilePath.find('.csv');
latestFilePath = inFilePath[:csvStrPos] + '_latest.csv'
weekFilePath = inFilePath[:csvStrPos] + '_week.csv'
monthFilePath = inFilePath[:csvStrPos] + '_month.csv'
allTimeFilePath = inFilePath[:csvStrPos] + '_allTime.csv'

keys = Response.getKeys()
keys.remove('failed test group')
keys.remove('failed pattern')
keys.remove('message')

descDataFilePath = os.path.split(os.path.abspath(inFilePath))[0] + '/.sasping_agg_data.json'

def writeAll(data):
    with open(allTimeFilePath, "w") as file:
        writer = csv.DictWriter(file, keys)
        writer.writerows(data)
        print('\nCreated file {0} with {1} rows\n'.format(allTimeFilePath, len(data)))
def writeMonth(data):
    with open(monthFilePath, "w") as file:
        writer = csv.DictWriter(file, keys)
        writer.writerows(data)
        print('\nCreated file {0} with {1} rows\n'.format(monthFilePath, len(data)))
def writeWeek(data):
    with open(weekFilePath, "w") as file:
        writer = csv.DictWriter(file, keys)
        writer.writerows(data)
        print('\nCreated file {0} with {1} rows\n'.format(weekFilePath, len(data)))
def writeLatest(data):
    with open(latestFilePath, "w") as file:
        writer = csv.DictWriter(file, keys)
        writer.writerows(data)
        print('\nCreated file {0} with {1} rows\n'.format(latestFilePath, len(data)))


with open(inFilePath, "r") as file:
    # check if file with only latest data exists, and is older than master csv file
    aggregation = Aggregator(file, maxDatapoints, descDataFilePath)

    if aggregation.getLatestUpdateTime() < int(os.path.getmtime(inFilePath)):
        if aggregation.shouldUpdateAll():
            writeAll([row for execution in aggregation.getShrinkedAllTimeData() for row in execution])
            writeMonth([row for execution in aggregation.getShrinkedMonthData() for row in execution])
            writeWeek([row for execution in aggregation.getShrinkedWeekData() for row in execution])
            writeLatest([row for execution in aggregation.getDayData() for row in execution])
        elif aggregation.shouldUpdateMonth():
            writeMonth([row for execution in aggregation.getShrinkedMonthData() for row in execution])
            writeWeek([row for execution in aggregation.getShrinkedWeekData() for row in execution])
            writeLatest([row for execution in aggregation.getDayData() for row in execution])
        elif aggregation.shouldUpdateWeek():
            writeWeek([row for execution in aggregation.getShrinkedWeekData() for row in execution])
            writeLatest([row for execution in aggregation.getDayData() for row in execution])
        else:
            writeLatest([row for execution in aggregation.getDayData() for row in execution])
