# RegistrationHandlerTest performs tests on the /registration API endpoint
from json import dumps
from tornado.escape import json_decode
from tornado.ioloop import IOLoop
from tornado.web import Application

from api.handlers.registration import RegistrationHandler

from .base import BaseTest

import urllib.parse

class RegistrationHandlerTest(BaseTest):

    # set up test application with /registration route
    @classmethod
    def setUpClass(self):
        self.my_app = Application([(r'/registration', RegistrationHandler)])
        super().setUpClass()

    # test successful registration with all fields provided
    def test_registration(self):
        email = 'test@test.com'
        display_name = 'testDisplayName'

        body = {
          'email': email,
          'password': 'testPassword',
          'displayName': display_name,
          'fullName': 'Test User',
          'address': 'Test Street',
          'phone': '1234567890',
          'disabilities': 'None',
          'dob': 'fake_dob_hex'
        }

        response = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(200, response.code)

        body_2 = json_decode(response.body)
        self.assertEqual(email, body_2['email'])
        self.assertEqual(display_name, body_2['displayName'])

    # test fallback where displayName is missing (should default to email)
    def test_registration_without_display_name(self):
        email = 'test@test.com'

        body = {
          'email': email,
          'password': 'testPassword',
          'fullName': 'Test User',
          'address': 'Test Street',
          'phone': '1234567890',
          'disabilities': 'None',
          'dob': 'fake_dob_hex'
        }

        response = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(200, response.code)

        body_2 = json_decode(response.body)
        self.assertEqual(email, body_2['email'])
        self.assertEqual(email, body_2['displayName'])

    # test registration of the same email twice (should return 409 conflict)
    def test_registration_twice(self):
        body = {
          'email': 'test@test.com',
          'password': 'testPassword',
          'displayName': 'testDisplayName',
          'fullName': 'Test User',
          'address': 'Test Street',
          'phone': '1234567890',
          'disabilities': 'None',
          'dob': 'fake_dob_hex'
        }

        response = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(200, response.code)

        response_2 = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(409, response_2.code)
