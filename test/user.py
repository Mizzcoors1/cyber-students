# UserHandlerTest runs tests for the /user API endpoint and token-protected user profile
from json import dumps
from tornado.escape import json_decode, utf8
from tornado.gen import coroutine
from tornado.httputil import HTTPHeaders
from tornado.ioloop import IOLoop
from tornado.web import Application

from api.handlers.user import UserHandler

from .base import BaseTest

import urllib.parse

class UserHandlerTest(BaseTest):

    # setup application route for test cases
    @classmethod
    def setUpClass(self):
        self.my_app = Application([(r'/user', UserHandler)])
        super().setUpClass()

    # insert fake user into test database with encrypted fields
    @coroutine
    def register(self):
        yield self.get_app().db.users.insert_one({
        'email': self.email,
        'password': b'$2b$12$exampleexampleexampleexampleexampleexamp',  # fake hashed
        'salt': b'$2b$12$exampleexampleexampleexampleexampleexamp',     # fake salt
        'displayName': self.display_name,
        'full_name': 'fake_full_name_hex',
        'address': 'fake_address_hex',
        'phone': 'fake_phone_hex',
        'disabilities': 'fake_disability_hex',
        'dob': 'fake_dob_hex'
        })

    # simulate login by setting token manually in DB
    @coroutine
    def login(self):
        yield self.get_app().db.users.update_one({
            'email': self.email
        }, {
            '$set': { 'token': self.token, 'expiresIn': 2147483647 }
        })

    # initialize test data before each test
    def setUp(self):
        super().setUp()

        self.email = 'test@test.com'
        self.password = 'testPassword'
        self.display_name = 'testDisplayName'
        self.token = 'testToken'

        IOLoop.current().run_sync(self.register)
        IOLoop.current().run_sync(self.login)

     # test authenticated /user route with correct token
    def test_user(self):
        headers = HTTPHeaders({'X-Token': self.token})

        response = self.fetch('/user', headers=headers)
        self.assertEqual(200, response.code)

        body_2 = json_decode(response.body)
        self.assertEqual(self.email, body_2['email'])
        self.assertEqual(self.display_name, body_2['displayName'])

    # test access to /user without authentication token
    def test_user_without_token(self):
        response = self.fetch('/user')
        self.assertEqual(400, response.code)

    # test /user route with invalid token
    def test_user_wrong_token(self):
        headers = HTTPHeaders({'X-Token': 'wrongToken'})

        response = self.fetch('/user')
        self.assertEqual(400, response.code)
