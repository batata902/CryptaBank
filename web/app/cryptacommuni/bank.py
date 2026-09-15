import socket
import json

class BankAccess:
    def __init__(self):
        self.host: str = 'localhost'
        self.port: int = 9000
        self.sock = self.get_connection()

    def get_connection(self) -> socket.socket:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))

        s.recv(1024)

        return s

    def send_recv(self, cmd: str) -> dict:
        self.sock.send(cmd.encode('utf-8'))

        raw_response: str = self.sock.recv(1024).decode('utf-8').strip()
        if not raw_response:
            raise Exception('Server down')

        return json.loads(raw_response)

    def login(self, username: str, password: str) -> tuple[bool, str | None]:
        self.sock.send(f'LOGIN {username}'.encode('utf-8'))

        response: dict = json.loads(self.sock.recv(1024).decode('utf-8'))
        if response['status'] == 200:
            self.sock.send(f'PASSWORD {password}'.encode('utf-8'))
            if json.loads(self.sock.recv(1024).decode('utf-8'))['status'] == 200:
                self.sock.send('EXPORT'.encode('utf-8'))
                session: str = json.loads(self.sock.recv(1024).decode('utf-8'))['data']
                return (True, session)

        return (False, None)

    def register(self, username, password) -> tuple[bool, str | None]:
        self.sock.send(f'CREATE user {username} {password}'.encode('utf-8'))
        
        response: dict = json.loads(self.sock.recv(1024).decode('utf-8'))
        if response['status'] == 200:
            return self.login(username, password)

        return (False, None)
            
    def check_token(self, token: str) -> bool:
        self.sock.send(f'IMPORT {token}'.encode('utf-8'))

        response: dict = json.loads(self.sock.recv(1024).decode('utf-8'))
        if response['status'] == 200:
            return True

        return False