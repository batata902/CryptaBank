import json

from dbOperations.database import Database
from utils.encryption import Encryption
from utils.utils import Utils
from utils.EmailSender import send_email

R = '\033[31m'
G = '\033[32m'
Y = '\033[33m'
B = '\033[35m'
E = '\033[m'

class ClientHandlener:
    def __init__(self, sock, client):
        self.s = sock
        self.db = Database()
        self.client = client
        self.encrypter = Encryption()
        self.key = self.handshake()
        self.email = ''

    def handshake(self):
        self.s.send(self.encrypter.rsa_pub_key())
        enc_key = self.s.recv(1024)
        key = self.encrypter.rsa_priv_dec(enc_key)
        self.encrypter.set_fernet(key)
        self.s.send(self.encrypter.enc(f'[{G}+{E}] {Y}BEM VINDO AO CRYPTA BANK{E} [{G}+{E}]\n[{G}+{E}] {G}Digite seu email{E}:\nCrypta~> '))
        print(key)
        return key

    def recvdata(self):
        return self.encrypter.dec(self.s.recv(1024))

    def senddata(self, raw_data):
        data = raw_data + '\nCrypta~> '
        self.s.sendall(self.encrypter.enc(data))

    def cadastro(self, email):
        while True:
            self.senddata('[-] Email não está cadastrado no nosso sistema, deseja cadastra-lo? [y/n]')
            opc = self.recvdata()['msg']
            if opc == 'y':
                break
            elif opc == 'n':
                self.close()
                return False, None
        code = Utils.generate_code()
        send_email(email, code, None, None, None, 'confirm-code') # Envio do email

        tentativas = 0
        while True:
            if tentativas >= 3:
                self.senddata('\033[31mLimite de tentativas excedido!\033[m')
                self.close()
                return False, None
            self.senddata('[+] \033[33mDigite o código enviado para o seu email:\033[m')
            codigo = self.recvdata()['msg']
            if code == codigo:
                self.senddata('[+] \033[32mDigite a sua nova senha!\033[m')
                senha = self.recvdata()['msg']
                self.db.cadastrar(email, senha)
                self.email = email
                return True, self.db.seeinfo(email, Utils.gethash(senha))
            else:
                tentativas += 1

    def autenticar(self):
        email = self.recvdata()['msg']
        if self.db.email_exists(email):
            self.senddata('[+] \033[32mDigite a sua senha:\033[m')

            tentativas = 0
            while True:
                if tentativas >= 3:
                    self.senddata(f'{R}Limite de tentativas excedido.{E}')
                    self.close()
                    return False, None
                senha = self.recvdata()['msg']

                login = self.db.login(email, senha)["login"]
                if login == "no":
                    self.senddata(f'{R}Senha errada, tente novamente. {3 - tentativas} tentativas restantes{E}')
                    tentativas += 1
                    continue
                break

            if self.db.verifica_tfa(email, senha):
                code = Utils.generate_code()
                send_email(email, code, None, None, None, 'confirm-code') # Envio do email
                self.senddata('[+] \033[32mDigite o código enviado para o seu email:\033[m')
                codigo = self.recvdata()['msg']
                if codigo == code:
                    self.email = email
                    return True, login
                self.close()
                return False, None

            self.email = email
            return True, login

        else:
            self.email = email
            return self.cadastro(email)

    def confirm_password(self):
        self.senddata('[+] \033[32mDigite a sua senha para confirmar a ação\033[m')
        senha = self.recvdata()['msg']
        if self.db.login(self.email, senha)['login'] != "no":
            self.senddata(f'[+] {G}Senha correta! Alterações feitas.{E}')
            return True, senha
        self.senddata(f'[-] {R}Senha incorreta inserida. Tente novamente mais tarde.{E}')
        return False, None

    def get_wallet(self, wallet, password):
        return self.db.seeinfo(wallet, password)

    def transfer(self, origin_wallet, destiny_wallet, value):
        self.db.transaction(origin_wallet, destiny_wallet, value)

        real_value = value / 100000000
        edited_value = f"{real_value:.10f}".rstrip('0').rstrip('.')

        send_email(self.email, edited_value, origin_wallet, destiny_wallet, Utils.new_uuid(0), 'transaction')

    def myhistory(self, swallet):
        return self.db.client_history(swallet)

    def changetfa(self):
        password = self.confirm_password()[1]
        return self.db.atualizar_2fa(self.email, password)

    def close(self):
        self.s.close()
