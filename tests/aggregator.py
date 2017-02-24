import unittest
import csv
import copy

from sas.aggregator import Aggregator
from sas.response import Response

class TestAggregator(unittest.TestCase):
    def setUp(self):
        csvList = [
            'sasping login request,1,,,,1487012255,0.118,,,1487012255',
            'id,1,,,,1487012255,0.658,,Stored Process Web Application,1487012255',
            'sasping login request,1,,,,1487012556,0.092,,,1487012556',
            'id,1,,,,1487012556,0.592,,Stored Process Web Application,1487012556',
            'sasping login request,1,,,,1487012857,0.082,,,1487012857',
            'id,1,,,,1487012857,0.753,,Stored Process Web Application,1487012857',
            'sasping login request,1,,,,1487013158,0.084,,,1487013158',
            'id,1,,,,1487013158,0.647,,Stored Process Web Application,1487013158'
        ]
        data = []
        for row in csv.DictReader(csvList, fieldnames=Response.getKeys()):
            # remove unused data
            del row['failed test group']
            del row['failed pattern']
            del row['message']
            row['timestamp'] = int(row['timestamp'])
            row['program exec timestamp'] = int(row['program exec timestamp'])
            data.append(row)
        # split in 2 runs
        self.data = [
            [data[0], data[1]],
            [data[2], data[3]],
            [data[4], data[5]],
            [data[6], data[6]]
        ]

    def testShrink(self):
        self.assertEqual(2, len(Aggregator.shrink(self.data, 2)))
        self.assertEqual(1, len(Aggregator.shrink(self.data, 1)))

    def testShrinkWithDifferentRowCount(self):
        # clone
        data = copy.deepcopy(self.data)
        del data[0][0]
        Aggregator.shrink(self.data, 2)
        Aggregator.shrink(self.data, 1)

        data = copy.deepcopy(self.data)
        del data[1][0]
        Aggregator.shrink(self.data, 2)
        Aggregator.shrink(self.data, 1)

        data = copy.deepcopy(self.data)
        del data[1][1]
        Aggregator.shrink(self.data, 2)
        Aggregator.shrink(self.data, 1)

        data = copy.deepcopy(self.data)
        del data[2][0]
        Aggregator.shrink(self.data, 2)
        Aggregator.shrink(self.data, 1)

        data = copy.deepcopy(self.data)
        del data[2][1]
        Aggregator.shrink(self.data, 2)
        Aggregator.shrink(self.data, 1)

    def testShrinkWithInvalidTimestamp(self):
        data = copy.deepcopy(self.data)
        data[0][0]['timestamp'] = 'NaN'
        Aggregator.shrink(self.data, 2)
        Aggregator.shrink(self.data, 1)
