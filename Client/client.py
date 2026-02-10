import rsa
#import readline
import os
import json
import cryptography
from cryptography.fernet import Fernet
import socket

os.system('cls || clear')

R = '\033[31m'
G = '\033[32m'
Y = '\033[33m'
B = '\033[34m'
P = '\033[35m'
E = '\033[m'


print ('''
\033[33m
 _____                  _       ______             _    
/  __ \\                | |      | ___ \\           | |   
| /  \\/_ __ _   _ _ __ | |_ __ _| |_/ / __ _ _ __ | | __
| |   | '__| | | | '_ \\| __/ _` | ___ \\/ _` | '_ \\| |/ /
| \\__/\\ |  | |_| | |_) | || (_| | |_/ / (_| | | | |   < 
 \\____/_|   \\__, | .__/\ \__\\__,_\\____/ \\__,_|_| |_|_|\\_\\
             __/ | |                                    
            |___/|_|   
\033[m''')



def handshake(sock):
        key_bytes = sock.recv(1024)
        print (f'[{Y}INFO{E}] Desserializando a chave recebida pelo servidor...')
        public_key = rsa.PublicKey.load_pkcs1(key_bytes)
        key = Fernet.generate_key()
        print (f'[{Y}INFO{E}] Chave gerada, criptografando e enviando ao servidor...')
        enc_key = rsa.encrypt(key, public_key)
        sock.sendall(enc_key)
        print (f'[{G}GREAT{E}] Handshake completo!')
        return Fernet(key)


def enc(fernet, data):
        return fernet.encrypt(json.dumps({'msg': data}).encode())


def dec(fernet, data):
        return json.loads(fernet.decrypt(data).decode())


IP = '192.168.56.1'
PORT = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
        try:
                s.connect((IP, PORT))
        except ConnectionRefusedError:
                print ('O servidor esta fora do ar.')
                exit(0)

        print (f'[{Y}INFO{E}] Fazendo handshake com {B}{IP}{E}...')
        fernet = handshake(s)


        while True:
                try:
                        answer = dec(fernet, s.recv(1024))['REQUEST-INFO']
                except cryptography.fernet.InvalidToken:
                        print ('Servidor desconectou.')
                        s.close()
                        break
                if answer.strip().startswith('clear'):
                        os.system('clear || cls')
                        s.sendall(enc(fernet, 'ok'))
                        continue

                #print (answer, end='')
                msg = input(answer)
                if msg == 'exit':
                        print ('Usuario escolheu sair.')
                        s.close()
                        break
                elif msg.strip() in ['clear', 'cls']:
                        os.system('clear || cls')
                s.sendall(enc(fernet, msg))
except ConnectionResetError:
        print ('Conexao fechada')
