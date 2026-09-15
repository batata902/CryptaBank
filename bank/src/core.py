from src.utils import Response
from src.session import Session

import socket
import threading

BANNER: str = 'CryptaBank Account System :: v1.0 :: CBAS\n'

HELP: list[dict[str, str]] = []

class Bank:
    def __init__(self):
        self.threads: list = []

        self.commands: dict = {}

    def help(self) -> str:
        return HELP

    def config_sock(self, host, port) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((host, port))
        sock.listen(10)

        return sock

    def start_server(self, host: str = '0.0.0.0', port: int = 9000):
        sock = self.config_sock(host, port)

        print(f'[+] Serviço CryptaBank iniciado em {host} na porta {port}')
        while True:
            con, client = sock.accept()

            print(f'[ + ] Cliente conectado -> {client[0]}')

            t = threading.Thread(target=self.handle_client, args=(con,client))
            t.start()

            self.threads.append(t)


    def command(self, cmd: str, help: str = ''):
        def wrapper(func):
            global HELP
            HELP.append({cmd: help})

            self.commands[cmd] = func

            return func
        return wrapper


    def handle_client(self, con: socket.socket, client):
        con.send(BANNER.encode('utf-8'))
        
        session: Session = Session()
        while True:
            try:
                data: bytes = con.recv(1024)
            except ConnectionResetError:
                break

            if not data:
                print(f'[-] Cliente desconectado -> {client[0]}')
                con.close()
                return

            data: str = data.decode('utf-8').strip().split()

            cmd = data[0].upper()
            args = data[1:]

            if cmd == 'EXIT':
                con.send(b'bye\n')
                con.close()
                return

            func = self.commands.get(cmd)
            print(self.commands)

            if not func:
                response = Response.render_response('Invalid command', 'E')
                con.send(response)
                continue

            response = func(session, args)
            con.send(response)

            

