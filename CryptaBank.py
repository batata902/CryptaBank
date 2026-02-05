import socket
import threading
import cryptography
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
        client.senddata('[-] Email não está cadastrado no nosso sistema, deseja cadastra-lo? [y/n]')
        opc = client.recvdata()['msg']
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
            client.close()
            return False, None
        client.senddata('[+] Digite o código enviado para o seu email:')
        codigo = client.recvdata()['msg']
        if code == codigo:
            client.senddata('[+] Digite a sua nova senha!')
            senha = client.recvdata()['msg']
            db.cadastrar(email, senha)
            return True, db.seeinfo(email, senha)['infos']
        else:
            tentativas += 1


def autenticar(client):
    email = client.recvdata()['msg']
    if db.email_exists(email):
        client.senddata('[+] Digite a sua senha:')
        senha = client.recvdata()['msg']

        login = db.login(email, senha)["login"]
        if login == "no":
            client.close()
            return False, None

        if db.verifica_tfa(email, senha):
            code = Utils.generate_code()
            send_email(email, code, None, None, None, 'confirm-code')
            client.senddata('[+] Digite o código enviado para o seu email:')
            codigo = client.recvdata()['msg']
            if codigo == code:
                return True, login
            client.close()
            return False, None

        return True, login

    else:
        return True, cadastro(client, email)


def handleclient(client):
    try:
        auth = autenticar(client)
        if auth[0] is False:
            return
        client.senddata(f'[+] Autenticado como {auth[1]["email"]}')
        while True:
            cmd = client.recvdata()
            client.senddata('Rocheda dms pivete')
    except cryptography.fernet.InvalidToken:
        client.close()
        print('Cliente se desconectou')
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