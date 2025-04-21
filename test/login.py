# LoginHandlerTest runs functional tests for the /login API endpoint
from json import dumps
from tornado.escape import json_decode, utf8
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.web import Application
import bcrypt
from .base import BaseTest

from api.handlers.login import LoginHandler

import urllib.parse

class LoginHandlerTest(BaseTest):
    
    # setup Tornado application for testing
    @classmethod
    def setUpClass(self):
        self.my_app = Application([(r'/login', LoginHandler)])
        super().setUpClass()

    # insert a test user into the database with a hashed password
    @coroutine
    def register(self):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), salt)
        yield self.get_app().db.users.insert_one({
            'email': self.email,
            'password': hashed_password,  # 
            'salt': salt,
            'displayName': self.display_name,
            'full_name': 'fake_full_name_hex',
            'address': 'fake_address_hex',
            'phone': 'fake_phone_hex',
            'disabilities': 'fake_disability_hex',
            'dob': 'fake_dob_hex'
        })

    # prepare test data before each test
    def setUp(self):
        super().setUp()

        self.email = 'test@test.com'
        self.password = 'testPassword'
        self.display_name = 'testDisplayName'
        IOLoop.current().run_sync(self.register)

    # test successful login using correct credentials
    def test_login(self):
        body = {
          'email': self.email,
          'password': self.password
        }

        response = self.fetch('/login', method='POST', body=dumps(body))
        self.assertEqual(200, response.code)

        body_2 = json_decode(response.body)
        self.assertIsNotNone(body_2['token'])
        self.assertIsNotNone(body_2['expiresIn'])

    # test login using same credentials but email with swapped case
    def test_login_case_insensitive(self):
        body = {
          'email': self.email.swapcase(),
          'password': self.password
        }

        response = self.fetch('/login', method='POST', body=dumps(body))
        self.assertEqual(200, response.code)

        body_2 = json_decode(response.body)
        self.assertIsNotNone(body_2['token'])
        self.assertIsNotNone(body_2['expiresIn'])

  # test login with incorrect email
    def test_login_wrong_email(self):
        body = {
          'email': 'wrongUsername',
          'password': self.password
        }

        response = self.fetch('/login', method='POST', body=dumps(body))
        self.assertEqual(403, response.code)

    # test login with incorrect password
    def test_login_wrong_password(self):
        body = {
          'email': self.email,
          'password': 'wrongPassword'
        }

        response = self.fetch('/login', method='POST', body=dumps(body))
        self.assertEqual(403, response.code)
