import socket
import threading
from datetime import datetime

import cryptography.fernet
from network.ClientHandlener import ClientHandlener
from utils.utils import Utils

#cores
R = '\033[31m'
G = '\033[32m'
Y = '\033[33m'
B = '\033[35m'
E = '\033[m'

c_help = f'''
{Utils.linha()}
[{G}+{E}] {G}my-wallet{E} - Ver informações da sua carteira 
[{G}+{E}] {G}history{E} - Ver histórico de transferências
[{G}+{E}] {G}transfer{E} [{Y}carteira-destino{E}] [{Y}quantia{E}] - Transferir dinheiro para Carteira de destino
[{G}+{E}] {G}2fa{E} - Muda o estado da autenticação de 2 fatores para ativado ou desativado
{Utils.linha()}
'''

def handleclient(client):
    try:
        success, auth = client.autenticar()

        if success is False:
            return
        client.senddata('clear')
        client.recvdata()
        client.senddata(f'[{G}+{E}] {Y}BEM VINDO AO CRYPTA BANK{E} [{G}+{E}]\n[{G}+{E}] Autenticado como {B}{auth["email"]}{E}')
        wallet = auth['wallet']
        password = auth['password']

        while True:
            cmd = client.recvdata()['msg'].strip()

            if cmd == 'help':
                client.senddata(c_help)
                continue

            elif cmd in ['clear', 'cls']:
                client.senddata(f'[{G}+{E}] {Y}BEM VINDO AO CRYPTA BANK{E} [{G}+{E}]')
                continue

            elif cmd in ['my-wallet', 'mywallet', 'carteira', 'minhacarteira']:
                auth = client.get_wallet(wallet, password)
                real_value = int(auth["currency"]) / 100000000
                edited_value = f"{real_value:.10f}".rstrip('0').rstrip('.')

                carteira = (f'{Utils.linha()}\n'
                            f'{G}wallet{E}: {auth["wallet"]}\n'
                            f'{G}email{E}: {auth["email"]}\n'
                            f'{G}creation-date{E}: {auth["created_at"]}\n'
                            f'{G}currency{E}: ₿ {edited_value} -> R$ {(real_value * 366887.57):.2f}\n'
                            f'{G}2FA{E}: {auth["tfa"]}\n{Utils.linha()}')
                client.senddata(carteira)
                continue

            elif cmd[:8] == 'transfer':
                try:
                    destiny = cmd.split(' ')[1]
                    quantity = cmd.split(' ')[2]
                except IndexError:
                    client.senddata(f'{R}Comando incompleto{E}')
                    continue
                client.transfer(auth['wallet'], destiny, int(float(quantity) * 100000000))
                client.senddata(f'{G}Transferencia realizada com sucesso!{E}')
                continue

            elif cmd in ['history', 'historico', 'transacoes']:
                historico = client.myhistory(auth['wallet'])
                itens = ''
                for h in historico:
                    parts = [f"{k}: {v}" for k, v in h.items()]
                    linha = ",".join(parts)
                    linha += '\n'
                    itens += linha
                client.senddata(itens)

            client.senddata(f'[{R}ERRO{E}] Comando não encontrado.')


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
