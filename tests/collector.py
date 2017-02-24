import unittest
import re
import json
import mock
import requests

import sas
import sas.functions
from sas.config.settings import Settings
from sas.config.test import Test
from sas.aggregator import Aggregator

class TestSas(unittest.TestCase):
    def testInit(self):
        pass
    def testSettingsConfig(self):
        self.assertRaisesRegexp(KeyError, "Missing required 'hostUrl' property", Settings, json.loads('{}'))
        self.assertRaisesRegexp(ValueError, "Property 'hostUrl' cannot be empty", Settings, json.loads("""{
            "hostUrl": ""
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'loginPath' property", Settings, json.loads("""{
            "hostUrl": "test"
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'loginPath' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": ""
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'loginParams' property", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test"
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'loginParams' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": ""
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'loginParams.username' property", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": {}
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'loginParams.username' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": {
                "username": ""
            }
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'loginParams.password' property", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": {
                "username": "test"
            }
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'loginParams.password' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": {
                "username": "test",
                "password": ""
            }
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'applications' property", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": {
                "username": "test",
                "password": "test"
            }
        }"""))
        self.assertRaisesRegexp(ValueError, "Login path must start with /", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{}]
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'applications' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "/test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": []
        }"""))
        self.assertRaisesRegexp(ValueError, "Login path must start with /", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{}]
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'application.name' property", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "/test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{}]
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'application.tests' property", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "/test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{
                "name": ""
            }]
        }"""))
        self.assertRaisesRegexp(ValueError, "Application property 'name' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "/test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{
                "name": "",
                "tests": ""
            }]
        }"""))
        self.assertRaisesRegexp(ValueError, "Application property 'tests' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "/test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{
                "name": "asd",
                "tests": ""
            }]
        }"""))
        self.assertRaisesRegexp(ValueError, "Application property 'tests' cannot be empty", Settings, json.loads("""{
            "hostUrl": "test",
            "loginPath": "/test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{
                "name": "asd",
                "tests": []
            }]
        }"""))

        # not raising
        Settings(json.loads("""{
            "hostUrl": "test",
            "loginPath": "/test",
            "loginParams": {
                "username": "test",
                "password": "test"
            },
            "applications": [{
                "name": "test",
                "tests": [{}]
            }]
        }"""))

    def testTestsConfig(self):
        self.assertRaisesRegexp(KeyError, "Missing required 'id' property", Test, json.loads('{}'))
        self.assertRaisesRegexp(ValueError, "Property 'id' cannot be empty", Test, json.loads("""{
            "id": ""
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'type' property in config with id 'test'", Test, json.loads("""{
            "id": "test"
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'type' cannot be empty", Test, json.loads("""{
            "id": "test",
            "type": ""
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'execPath' property in config with id 'test'", Test, json.loads("""{
            "id": "test",
            "type": "test"
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'execPath' cannot be empty", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": ""
        }"""))
        self.assertRaisesRegexp(ValueError, "Exec path must start with /", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "test"
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'mustContain' property in config with id 'test'", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": ""
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'mustContain' property in config with id 'test'", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": {}
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'mustContain' should be list", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": {
                "mustContain": ""
            }
        }"""))
        self.assertRaisesRegexp(KeyError, "Missing required 'cantContain' property in config with id 'test'", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": {
                "mustContain": []
            }
        }"""))
        self.assertRaisesRegexp(ValueError, "Property 'cantContain' should be list", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": {
                "mustContain": [],
                "cantContain": ""
            }
        }"""))
        self.assertRaisesRegexp(ValueError, "Validation '\[' is not a valid regular expression", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": {
                "mustContain": ["["],
                "cantContain": []
            }
        }"""))
        self.assertRaisesRegexp(ValueError, "Validation '\)' is not a valid regular expression", Test, json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": {
                "mustContain": [],
                "cantContain": [")"]
            }
        }"""))

        # not raising
        Test(json.loads("""{
            "id": "test",
            "type": "test",
            "execPath": "/test",
            "validations": {
                "mustContain": [],
                "cantContain": []
            }
        }"""))

    @mock.patch('sas._session.post', side_effect=Exception('unknown error'))
    def testRequests1(self, mockedReq):
        config = json.load(open('settings.json'))
        with self.assertRaises(Exception):
            result = sas.run(config, False)
            self.assertEqual(result[0]['message'], 'unknown error')
            self.assertEqual(result[0]['status'], None)

    @mock.patch('sas.login', side_effect=Exception('unknown error'))
    def testRequests2(self, loginReqMock):
        config = json.load(open('settings.json'))
        with self.assertRaises(Exception):
            result = sas.run(config, False)
            self.assertEqual(result[0]['status'], None)
            self.assertEqual(result[0]['message'], 'unknown error')
            loginReqMock.assert_called_once()

    @mock.patch('sas.login', return_value=False)
    def testRequests3(self, loginReq):
        config = json.load(open('settings.json'))
        result = sas.run(config, False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], None)
        self.assertEqual(result[0]['message'], 'Failed to login.')

    @mock.patch('sas._login', return_value=False)
    def testRequests4(self, loginReq):
        config = json.load(open('settings.json'))
        result = sas.run(config, False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], None)
        self.assertEqual(result[0]['message'], 'Failed to login.')

if __name__ == '__main__':
    unittest.main()
