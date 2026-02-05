import socket
import threading
from dbOperations.database import Database
from network.ClientHandlener import ClientHandlener
from utils.EmailSender import send_email
from utils.utils import Utils

#cores
R = '\033[31m'
G = '\033[32m'
B = '\033[35m'
Y = '\033[33m'
E = '\033[m'

db = Database()

def linha():
        return '[+]' + ('='*30) + '[+]'


def cadastro(client, email):
    while True:
        client.sendData('[-] Email não está cadastrado no nosso sistema, deseja cadastra-lo? [y/n]')
        opc = client.recvData()
        if opc == 'y':
            break
        elif opc == 'n':
            client.close()
            return False, None
    code = Utils.generate_code()
    send_email(email, code, None, None, None, 'confirm-code')

    tentativas = 0
    while True:
        if tentativas >= 3:
            return False, None
        client.sendData('[+] Digite o código enviado para o seu email:')
        codigo = client.recvData()
        if code == codigo:
            client.sendData('[+] Digite a sua nova senha!')
            senha = client.recvData()
            db.cadastrar(email, senha)
            return True, db.seeinfo(email, senha)['infos']
        else:
            client.sendData('[-] Código errado! Digite novamente:')
            tentativas += 1


def autenticar(client):
    email = client.recvData()['msg']
    if db.email_exists(email):
        client.sendData('[+] Digite a sua senha:')
        senha = client.recvData()['msg']

        login = db.login(email, senha)["login"]
        if login == "no":
            client.close()
            return False, None

        if db.verifica_tfa(email, senha):
            code = Utils.generate_code()
            send_email(email, code, None, None, None, 'confirm-code')
            client.sendData('[+] Digite o código enviado para o seu email:')
            codigo = client.recvData()['msg']
            if codigo == code:
                return True, login
            return False, None

        return True, login

    else:
        return cadastro(client, email)


def handleclient(client):
    success = autenticar(client)
    if success is False:
        return


def handlerequests(sock):
        while True:
            con, addr = sock.accept()
            print(f'Conexão recebida --> {addr}')
            client = ClientHandlener(con, addr)
            t = threading.Thread(target=handleclient, args=(client,))
            t.start()



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 8080))
s.listen(10)
print ('Servidor iniciado, escutando...')

handlerequests(s)