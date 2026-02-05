import json
from utils.encryption import Encryption

R = '\033[31m'
G = '\033[32m'
Y = '\033[33m'
B = '\033[35m'
E = '\033[m'

class ClientHandlener:
    def __init__(self, sock, client):
        self.s = sock
        self.client = client
        self.encrypter = Encryption()
        self.key = self.handshake()

    def handshake(self):
        self.s.send(self.encrypter.rsa_pub_key())
        enc_key = self.s.recv(1024)
        key = self.encrypter.rsa_priv_dec(enc_key)
        self.encrypter.set_fernet(key)
        self.s.send(self.encrypter.enc(f'[{G}+{E}] BEM VINDO AO {Y}CRYPTA BANK{E} [{G}+{E}]\n[{G}+{E}] Digite seu {B}email{E}:\nCrypta~> '))
        print(key)
        return key

    def recvdata(self):
        raw_data = self.encrypter.dec(self.s.recv(1024))
        data = json.loads(raw_data)
        return data

    def senddata(self, raw_data):
        raw_data = raw_data + '\nCrypta~> '
        data = json.dumps({'REQUEST-INFO': raw_data}).encode()
        self.s.sendall(self.encrypter.enc(data))

    def close(self):
        self.s.close()
