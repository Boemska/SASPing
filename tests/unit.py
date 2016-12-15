import unittest
import re
import json

import sas.functions
from sas.settings import Settings

class TestSas(unittest.TestCase):
    def testInit(self):
        pass

class TestSettings(unittest.TestCase):
    def setUp(self):
        testConfigObjects = json.load(open('./settings.json'))
        self.settings = Settings(testConfigObjects[0])

    def testSetException(self):
        with self.assertRaises(KeyError):
            self.settings.set('wrongKey', None)

    def testSetAndGet(self):
        self.settings.set('execUrl', 'testValue')
        self.assertEqual(self.settings.get('execUrl'), 'testValue')

    def testDotNotationGet(self):
        self.assertIsNotNone(self.settings.get('execParams.program'))

    def testDotNotationSet(self):
        self.settings.set('execParams.testParam', 'testValue')
        self.assertEqual(self.settings.get('execParams.testParam'), 'testValue')

    def testGetAll(self):
        data = self.settings.getAll()
        self.assertTrue(type(data) is dict)
        self.assertTrue(data['id'] != None)
        self.assertTrue(type(data['execUrl']) is unicode)
        self.assertTrue(type(data['loginUrl']) is unicode)
        self.assertTrue(type(data['execParams']) is dict)
        self.assertTrue(type(data['loginParams']) is dict)
        self.assertTrue(type(data['execParams']['program']) is unicode)
        self.assertTrue(type(data['loginParams']['username']) is unicode)
        self.assertTrue(type(data['loginParams']['password']) is unicode)


class TestFunctions(unittest.TestCase):
    def setUp(self):
        testConfigObjects = json.load(open('./settings.json'))
        self.settings = Settings(testConfigObjects[0])

    def testGetHostUrl(self):
        hostUrl = re.search('(^https?:\/\/.+?)\/', self.settings.get('execUrl')).group(1)
        self.assertEqual(sas.functions.getHostUrl(self.settings.get('execUrl')), hostUrl)

if __name__ == '__main__':
    unittest.main()
