# LoginHandler for authenticating users and issuing access tokens ===
import bcrypt
from datetime import datetime, timedelta
from time import mktime
from tornado.escape import json_decode, utf8
from tornado.gen import coroutine
from uuid import uuid4
from .base import BaseHandler

class LoginHandler(BaseHandler):

    # generate a session token for a user that expires in 2 hours
    @coroutine
    def generate_token(self, email):
        token_uuid = uuid4().hex
        expires_in = datetime.now() + timedelta(hours=2)
        expires_in = mktime(expires_in.utctimetuple())

        token = {
            'token': token_uuid,
            'expiresIn': expires_in,
        }

        # update user's record with new token info
        yield self.db.users.update_one({
            'email': email
        }, {
            '$set': token
        })

        return token
    
    # handle POST /login request for user authentication
    @coroutine
    def post(self):
        try:
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            if not isinstance(email, str):
                raise Exception()
            password = body['password']
            if not isinstance(password, str):
                raise Exception()
        except:
            self.send_error(400, message='You must provide an email address and password!')
            return

        if not email:
            self.send_error(400, message='The email address is invalid!')
            return

        if not password:
            self.send_error(400, message='The password is invalid!')
            return

        # Retreive user record by email
        user = yield self.db.users.find_one({
            'email': email
        })

        if user is None:
            self.send_error(403, message='The email address and password are invalid!')
            return
        
        # extract stored hash and salt from DB
        stored_hashed_password = user.get('password')
        salt = user.get('salt')

        # if one or both of these values are missing an error is returned
        if stored_hashed_password is None or salt is None:
            self.send_error(500, message='User account is not properly configured')
            return
        
        # hash the password with the stored salt and compare to the stored hash
        entered_hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # check the password matches what is stored and respond accordingly with a token
        if stored_hashed_password == entered_hashed_password:
            token = yield self.generate_token(email)
            self.response = {}
            self.response['token'] = token['token']
            self.response['expiresIn'] = token['expiresIn']
            self.set_status(200)
            self.write_json()

        else:
            self.send_error(403, message='The email address and password are invalid!')
