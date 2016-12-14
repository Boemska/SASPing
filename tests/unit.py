import unittest
import re

from sas.functions import getHostUrl
from sas.settings import getSettings

class Tests(unittest.TestCase):
    def testGetHostUrl(self):
        hostUrl = re.search('(^http:\/\/.+?)\/', getSettings()['execUrl']).group(1)
        self.assertEqual(getHostUrl(), hostUrl)

if __name__ == '__main__':
    unittest.main()
