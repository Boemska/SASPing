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
        self.assertIsNotNone(self.settings.get('execParams._program'))
        self.assertIsNotNone(self.settings.get('loginParams.username'))
        self.assertIsNotNone(self.settings.get('loginParams.password'))

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
        self.assertTrue(type(data['execParams']['_program']) is unicode)
        self.assertTrue(type(data['loginParams']['username']) is unicode)
        self.assertTrue(type(data['loginParams']['password']) is unicode)


class TestFunctions(unittest.TestCase):
    def setUp(self):
        testConfigObjects = json.load(open('./settings.json'))
        self.settings = Settings(testConfigObjects[0])

    def testGetHostUrl(self):
        hostUrl = re.search('(^https?:\/\/.+?)\/', self.settings.get('execUrl')).group(1)
        self.assertEqual(sas.functions.getHostUrl(self.settings.get('execUrl')), hostUrl)

    def validateResponse(self):
        response1 = """
                    {
                       "toplevelUser":[
                            {
                                "NAME":"William",
                                "SEX":"M",
                                "AGE":15,
                                "HEIGHT":66.5,
                                "WEIGHT":112
                            }
                        ],
                        "usermessage":"blank",
                        "logmessage":"blank",
                        "requestingUser":"jimdemo",
                        "requestingPerson":"sasdemo",
                        "executingPid":9440,
                        "sasDatetime":1797484856.6,
                        "status":"success"
                    }
                    """
        response2 = """
                    <div class="solutionsErrorTitle">
                    <img src="https://apps.boemskats.com/SASTheme_default/themes/default/images/MessageError24.gif" border="0" height="24" width="24" alt="Error" title="Error" align="absmiddle" />
                    Stored Process Error
                    </div>
                    ERROR 79-322: Expecting a FROM.
                    """
        validations = self.settings.get('validations')

        validation1 = functions.validateResponse(response1, validations)
        validation2 = functions.validateResponse(response2, validations)
        self.assertEqual(validation1[0], 'success')
        self.assertEqual(validation2[0], 'fail')


if __name__ == '__main__':
    unittest.main()
