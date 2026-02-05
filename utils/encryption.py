from cryptography.fernet import Fernet
import json
import rsa

class Encryption:
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(2048)
        self.fernet = None

    def set_fernet(self, key):
        self.fernet = Fernet(key)

    def enc(self, data):
        return self.fernet.encrypt(json.dumps({'REQUEST-INFO': data}).encode())

    def dec(self, data):
        return json.loads(self.fernet.decrypt(data).decode())

    def get_key(self):
        return self.key

    def rsa_pub_key(self):
        return self.public_key.save_pkcs1()

    def rsa_priv_dec(self, encoded_data):
        data = rsa.decrypt(encoded_data, self.private_key)
        return data