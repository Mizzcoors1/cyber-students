# RegistrationHandler handles user sign-up and encryption of personal data
from abc import ABC
import bcrypt
from tornado.escape import json_decode
from tornado.gen import coroutine
from .base import BaseHandler
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets
import json


# encrypt_value encrypts sensitive strings using AES CTR with random key + nonce
def encrypt_value(value):
    # generate a 32-byte key 
    key = secrets.token_bytes(32)
    key_bytes = bytes(key)
    
    # 16 bytes nonce created using the secrets module
    nonce_bytes = secrets.token_bytes(16)
    
    # Applies a new cipher object using AES in CTR mode with the nonce_bytes
    aes_ctr_cipher = Cipher(algorithms.AES(key_bytes), mode=modes.CTR(nonce_bytes))
    
    # initialises a new encryptor object from the cipher object
    aes_ctr_encryptor = aes_ctr_cipher.encryptor()
    
    # utf-8 encoding used 
    plaintext_bytes = bytes(value, "utf-8")
    
    # converts ciphertext_bytes to a hex string
    ciphertext_bytes = aes_ctr_encryptor.update(plaintext_bytes)
    ciphertext = ciphertext_bytes.hex()
    
    # returns ciphertext, key_bytes and nonce_bytes
    return ciphertext, key_bytes, nonce_bytes

class RegistrationHandler(BaseHandler, ABC):

    @coroutine
    def post(self):
        try:
            body = json_decode(self.request.body)

            # extract and validate core fields
            email = body['email'].lower().strip()
            if not isinstance(email, str):
                raise Exception()
            
            password = body['password']
            if not isinstance(password, str):
                raise Exception()
            
            display_name = body.get('displayName')
            if display_name is None:
                display_name = email
            if not isinstance(display_name, str):
                raise Exception()
            
             # Extract and validate additional profile data
            # Obtain full_name
            full_name = body.get('fullName')
            if not isinstance(full_name, str):
                raise Exception()
            
            # Obtain address
            address = body.get('address')
            if not isinstance(address, str):
                raise Exception()
            
            # Obtain phone
            phone = body.get('phone')
            if not isinstance(phone, str):
                raise Exception()
            
            # Obtain disabilities
            disabilities = body.get('disabilities')
            if not isinstance(disabilities, str):
                raise Exception()
            
            # Obtain Date of Birth
            dob = body.get('dob')
            if not isinstance(dob, str):
                raise Exception()
            
        except Exception as e:
            self.send_error(400, message='You must provide an email address, password, display name, Full Name, address, Phone Number, Disabilitiy - if none just add none and a Date of Birth!')
            return

        # Verifies if inputs are valid or empty.
        if not email:
            self.send_error(400, message='The email address is invalid! Please enter a valid email address')
            return

        if not password:
            self.send_error(400, message='The password is invalid! Please enter a valid password')
            return

        if not display_name:
            self.send_error(400, message='The display name is invalid! Please enter a valid display name')
            return

        if not full_name:
            self.send_error(400, message='Please enter a full name!')
            return

        if not address:
            self.send_error(400, message='Please enter an address!')
            return

        if not phone:
            self.send_error(400, message='Please enter a valid phone number!')
            return

        if not disabilities:
            self.send_error(400, message='If this field does not apply please enter NONE!')
            return
        
        if not dob:
            self.send_error(400, message='Please enter a valid date of birth!')
            return

        # check if user already exists
        user = yield self.db.users.find_one({
            'email': email
        }, {})

        if user is not None:
            self.send_error(409, message='A user with this email address already exists!')
            return

        # function created to hash the user's password
        def hash_password(password):
            
            # Using the bcrypt module, create a salt for the password hash
            salt = bcrypt.gensalt()
            
            # Using bcrypt with the salt hash the password 
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # return the salt & hashed password
            return hashed_password, salt

        # hash the password 
        hashed_password, salt = hash_password(password)

        # encrypt personal fields, along with key and nonce
        encrypted_full_name, key_full_name, nonce_full_name = encrypt_value(full_name)
        encrypted_address, key_address, nonce_address = encrypt_value(address)
        encrypted_phone, key_phone, nonce_phone = encrypt_value(phone)
        encrypted_disabilities, key_disabilities, nonce_disabilities = encrypt_value(disabilities)
        encrypted_dob, key_dob, nonce_dob = encrypt_value(dob)

        # Store the encrypted new user values in the users collection of the db
        yield self.db.users.insert_one({
            'email': email,
            'password': hashed_password,
            'displayName': display_name,
            'salt': salt,
            'full_name': encrypted_full_name,
            'address': encrypted_address,
            'phone': encrypted_phone,
            'disabilities': encrypted_disabilities,
            'dob': encrypted_dob,
        })

        # write encryption keys and nonces to local file (dangerous for production!)
        with open('keyfile', 'w') as f:
            json.dump([
                {'name': 'full_name', 'key': key_full_name.hex(), 'nonce': nonce_full_name.hex()},
                {'name': 'address', 'key': key_address.hex(), 'nonce': nonce_address.hex()},
                {'name': 'phone', 'key': key_phone.hex(), 'nonce': nonce_phone.hex()},
                {'name': 'disabilities', 'key': key_disabilities.hex(), 'nonce': nonce_disabilities.hex()},
                {'name': 'dob', 'key': key_dob.hex(), 'nonce': nonce_dob.hex()}
            ], f)

        # respond with minimal user info
        self.set_status(200)
        self.response['email'] = email
        self.response['displayName'] = display_name

        self.write_json()
