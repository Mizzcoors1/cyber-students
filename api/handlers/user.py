# UserHandler serves authenticated user profile data by decrypting stored fields
import json
from abc import ABC
from typing import List
from tornado.web import authenticated

from .auth import AuthHandler
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class UserHandler(AuthHandler, ABC):

    # decrypts a hex string using AES CTR and the given key/nonce
    def decrypt_value(self, value, key, nonce):
        if not key or not nonce:
            return None

        aes_ctr_cipher = Cipher(algorithms.AES(key), mode=modes.CTR(nonce))
        aes_ctr_decryptor = aes_ctr_cipher.decryptor()

        try:
            ciphertext_bytes = bytes.fromhex(value)
        except ValueError:
            return None
        
        plaintext_bytes = aes_ctr_decryptor.update(ciphertext_bytes)
        plaintext = plaintext_bytes.decode("utf-8")

        return plaintext
    
    # Retrieve user document from database by email
    async def get_user_data(self, email):
        if not self.db:
            return None

        user_data = await self.db.users.find_one({'email': email})
        return user_data

    # decrypt all encrypted fields for a given user email
    async def generate_user_data(self, email):

        # load the keys and nonces from the keyfile
        with open('keyfile', 'r') as f:
            key_data = json.load(f)

        # function to retrieve a specific key and nonce by name
        def get_key_and_nonce(name):
            for item in key_data:
                if item.get('name') == name:
                    return bytes.fromhex(item.get('key')), bytes.fromhex(item.get('nonce'))
            return None, None

        # retrieve user's encrypted details from the database
        if not self.db:
            return None

        user_data = await self.get_user_data(email)

        # Added fallback to validate presence of encrypted fields
        encrypted_full_name = user_data.get('full_name')
        if not encrypted_full_name:
            self.send_error(500, message='User profile incomplete: full_name missing')
            return
        
        encrypted_address = user_data['address']
        if not encrypted_address:
            self.send_error(500, message='User profile incomplete: address missing')
            return
        
        encrypted_phone = user_data['phone']
        if not encrypted_phone:
            self.send_error(500, message='User profile incomplete: phone missing')
            return
        
        encrypted_disabilities = user_data['disabilities']
        if not encrypted_disabilities:
            self.send_error(500, message='User profile incomplete: disabilities missing')
            return
        
        encrypted_dob = user_data.get('dob')
        if not encrypted_dob:
            self.send_error(500, message='User profile incomplete: dob missing')
            return


        # get decryption keys and nonces for the encrypted fields
        key_full_name, nonce_full_name = get_key_and_nonce('full_name')
        key_address, nonce_address = get_key_and_nonce('address')
        key_phone, nonce_phone = get_key_and_nonce('phone')
        key_disabilities, nonce_disabilities = get_key_and_nonce('disabilities')
        key_dob, nonce_dob = get_key_and_nonce('dob')


        # decrypt each field
        full_name = self.decrypt_value(encrypted_full_name, key_full_name, nonce_full_name)
        address = self.decrypt_value(encrypted_address, key_address, nonce_address)
        phone = self.decrypt_value(encrypted_phone, key_phone, nonce_phone)
        disabilities = self.decrypt_value(encrypted_disabilities, key_disabilities, nonce_disabilities)
        dob = self.decrypt_value(encrypted_dob, key_dob, nonce_dob)

        # return decrypted user profile data
        return {
            'full_name': full_name,
            'address': address,
            'phone': phone,
            'disabilities': disabilities,
            'dob': dob
        }

    # HTTP GET endpoint for retrieving the authenticated user's decrypted data
    @authenticated
    async def get(self):
        self.set_status(200)
        self.response['email'] = self.current_user['email']
        self.response['displayName'] = self.current_user['display_name']

         # populate decrypted data in response
        decrypted_data = await self.generate_user_data(self.current_user['email'])
        if decrypted_data:
            self.response['full_name'] = decrypted_data['full_name']
            self.response['address'] = decrypted_data['address']
            self.response['phone'] = decrypted_data['phone']
            self.response['disabilities'] = decrypted_data['disabilities']
            self.response['dob'] = decrypted_data['dob']
        self.write_json()
