import unittest
import re

import sas.functions
import sas.settings

class TestSettings(unittest.TestCase):
    def testSetException(self):
        with self.assertRaises(KeyError):
            sas.settings.set('wrongKey', None)

    def testSetAndGet(self):
        sas.settings.set('username', 'testUsername')
        self.assertEqual(sas.settings.get('username'), 'testUsername')

    def testGetAll(self):
        data = sas.settings.getAll()
        self.assertTrue(type(data) is dict)
        self.assertTrue(type(data['execUrl']) is unicode)
        self.assertTrue(type(data['program']) is unicode)
        self.assertTrue(type(data['username']) is unicode)
        self.assertTrue(type(data['password']) is unicode)


class TestFunctions(unittest.TestCase):
    def testGetHostUrl(self):
        hostUrl = re.search('(^https?:\/\/.+?)\/', sas.settings.get('execUrl')).group(1)
        self.assertEqual(sas.functions.getHostUrl(), hostUrl)

if __name__ == '__main__':
    unittest.main()
