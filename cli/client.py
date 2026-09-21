import socket
import json
import argparse
import sys
import os
from glob import glob

# Cores para o terminal
R = '\033[31m'  # Vermelho (Erro)
G = '\033[32m'  # Verde (Sucesso)
E = '\033[m'    # Reset
C = '\033[36m'  # Ciano (Menus/Destaques)


class BankCli:
    def __init__(self, addr: str, port: int, session_file: str = None):
        self.addr: str = addr
        self.port: int = port
        self.session_file: str = session_file
        self.sock: socket.socket = None

    def connect_and_run(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.sock.settimeout(10.0)
            self.sock.connect((self.addr, self.port))
            self.sock.settimeout(None)
            
            banner: str = self.sock.recv(4096).decode('utf-8').strip()
            if banner:
                print(banner)

            # Tenta autenticar via arquivo passado por parâmetro CLI
            if self.session_file:
                if not self._import_session_from_file(self.session_file):
                    print(self.format_error("Falha ao importar sessão. Direcionando para o menu de autenticação."))
                    if not self.auth_menu():
                        return
            else:
                if not self.auth_menu():
                    return
            
            self.main_menu()

        except ConnectionRefusedError:
            print(self.format_error(f"Conexão recusada pelo servidor em {self.addr}:{self.port}"))
        except socket.timeout:
            print(self.format_error(f"Tempo limite de conexão excedido ({self.addr}:{self.port})"))
        except Exception as e:
            print(self.format_error(f"Erro inesperado: {e}"))
        finally:
            if self.sock:
                self.sock.close()

    def _send_and_recv(self, command: str) -> dict:
        """Helper para enviar comandos e receber o JSON parseado."""
        try:
            self.sock.send(command.encode('utf-8'))
            raw_data = self.sock.recv(4096).decode('utf-8')
            
            if not raw_data:
                print(self.format_error("A conexão com o servidor foi perdida."))
                sys.exit(1)

            parsed = json.loads(raw_data)
            return parsed if isinstance(parsed, dict) else {"status": "S", "data": parsed}
            
        except json.JSONDecodeError:
            print(self.format_error('Resposta inválida (JSON) do servidor'), file=sys.stderr)
            return {"status": "E", "data": "Erro de decodificação do servidor"}
        except Exception as e:
            print(self.format_error(f'Erro durante envio do comando: {e}'), file=sys.stderr)
            return {"status": "E", "data": str(e)}

    def _is_error(self, response: dict) -> bool:
        """Verifica se a resposta do servidor indica um erro."""
        status = response.get('status')
        return status in ['E', 100]

    def _import_session_from_file(self, filepath: str) -> bool:
        """Lê a sessão em formato Base64/pickle do arquivo e envia ao servidor."""
        try:
            with open(filepath, 'r') as f:
                session_data = f.read().strip()
            
            response = self._send_and_recv(f'IMPORT {session_data}')
            
            if self._is_error(response):
                print(self.format_error('Erro ao importar a sessão: ' + str(response.get('data'))))
                return False
            
            print(self.format_success('Sessão importada com sucesso! Bem-vindo de volta.'))
            return True
        except FileNotFoundError:
            print(self.format_error(f"Arquivo '{filepath}' não encontrado."))
            return False

    def auth_menu(self) -> bool:
        """Menu interativo de autenticação e cadastro."""
        while True:
            print(f"\n{C}=== CryptaBank - Login / Cadastro ==={E}")
            print("1. Fazer Login")
            print("2. Registrar Novo Usuário")
            print("3. Importar Arquivo de Sessão (.dat)")
            print("0. Sair")
            
            try:
                escolha = input("\nEscolha uma opção: ").strip()
            except EOFError:
                return False

            if escolha == '1':
                if self.do_login():
                    input(f"\n{C}[Pressione Enter para continuar...]{E}")
                    os.system('clear' if os.name == 'posix' else 'cls')
                    return True
            elif escolha == '2':
                self.do_register()
            elif escolha == '3':
                if self.interactive_import():
                    input(f"\n{C}[Pressione Enter para continuar...]{E}")
                    os.system('clear' if os.name == 'posix' else 'cls')
                    return True
            elif escolha == '0':
                return False
            else:
                print(self.format_error("Opção inválida!"))
            
            input(f"\n{C}[Pressione Enter para tentar novamente...]{E}")
            os.system('clear' if os.name == 'posix' else 'cls')

    def do_register(self) -> bool:
        """Realiza o cadastro de novos usuários."""
        print(f"\n{C}--- Novo Cadastro ---{E}")
        user = input('Username: ').strip()
        password = input('Password: ').strip()

        if not user or not password:
            print(self.format_error("Usuário e senha não podem ser vazios."))
            return False

        response = self._send_and_recv(f'REGISTER "{user}" "{password}"')
        if self._is_error(response):
            print(self.format_error(f"Falha no cadastro: {response.get('data')}"))
            return False

        print(self.format_success("Usuário registrado com sucesso! Faça login para acessar."))
        return True

    def do_login(self) -> bool:
        """Inicia a autenticação em duas etapas (LOGIN -> PASSWORD)."""
        try:
            user_input = input('Username: ').strip()
            if not user_input:
                return False
            
            res_login = self._send_and_recv(f'LOGIN {user_input}')
            if self._is_error(res_login):
                print(self.format_error(res_login.get('data', 'Erro ao enviar usuário')))
                return False

            pass_input = input('Password: ').strip()
            res_pass = self._send_and_recv(f'PASSWORD {pass_input}')
            
            if not self._is_error(res_pass) and res_pass.get('data') == 'WELCOME':
                print(self.format_success('Autenticado com sucesso!'))
                return True
            
            print(self.format_error('Usuário ou senha inválidos.'))
            return False
                
        except EOFError:
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)

    def interactive_import(self) -> bool:
        """Lista e escolhe arquivo de sessão (.dat) no diretório atual."""
        dat_files = glob("*.dat")
        
        print(f"\n{C}--- Arquivos de sessão encontrados ---{E}")
        if not dat_files:
            print("Nenhum arquivo .dat encontrado no diretório atual.")
            print("[M] Digitar o caminho manualmente")
        else:
            for i, f in enumerate(dat_files):
                print(f"[{i+1}] {f}")
            print("[M] Digitar o caminho manualmente")
        print("[0] Voltar")

        escolha = input("Escolha uma opção: ").strip().lower()
        
        if escolha == '0':
            return False
        
        filepath = ""
        if escolha == 'm':
            filepath = input("Digite o caminho do arquivo de sessão: ").strip()
        elif escolha.isdigit() and 1 <= int(escolha) <= len(dat_files):
            filepath = dat_files[int(escolha) - 1]
        else:
            print(self.format_error("Opção inválida."))
            return False

        if not filepath:
            return False

        return self._import_session_from_file(filepath)

    def main_menu(self) -> None:
        """Menu principal com as operações atualizadas."""
        os.system('clear' if os.name == 'posix' else 'cls')

        while True:
            print(f"\n{C}=== CryptaBank - Menu Principal ==={E}")
            print("1. Ver Saldo")
            print("2. Ver Informações da Conta")
            print("3. Realizar Transferência")
            print("4. Extrato de Transferências")
            print("5. Gerenciar Cartões")
            print("6. Atualizar Chave da Conta")
            print("7. Exportar Sessão")
            print("0. Sair")

            try:
                escolha = input("\nEscolha uma opção: ").strip()
            except EOFError:
                print(self.format_success('\nConexão encerrada pelo usuário'))
                break

            if escolha == '0':
                print(self.format_success('Conexão encerrada'))
                break

            os.system('clear' if os.name == 'posix' else 'cls')

            if escolha == '1':
                self._handle_command('BALANCE')
            elif escolha == '2':
                self._handle_command('INFO')
            elif escolha == '3':
                self.interactive_transfer()
            elif escolha == '4':
                self._handle_command('TRANSACTIONS')
            elif escolha == '5':
                self.cards_menu()
            elif escolha == '6':
                self.interactive_update_key()
            elif escolha == '7':
                self.interactive_export()
            else:
                print(self.format_error("Opção inválida!"))

            input(f"\n{C}[Pressione Enter para continuar...]{E}")
            os.system('clear' if os.name == 'posix' else 'cls')

    def cards_menu(self) -> None:
        """Submenu para gerenciamento de cartões."""
        print(f"\n{C}=== Gestão de Cartões ==={E}")
        print("1. Listar Cartões")
        print("2. Criar Novo Cartão")
        print("3. Bloquear/Desbloquear Cartão")
        print("4. Deletar Cartão")
        print("0. Voltar")

        sub = input("\nEscolha uma opção: ").strip()

        if sub == '1':
            self._handle_command('CARDS')
        elif sub == '2':
            holder = input("Nome do titular impresso no cartão: ").strip()
            if holder:
                self._handle_command(f'CREATE card "{holder}"')
        elif sub == '3':
            card_id = input("ID do Cartão: ").strip()
            status = input("Status de bloqueio (1 = Bloquear, 0 = Desbloquear): ").strip()
            if card_id and status in ['0', '1']:
                self._handle_command(f'UPDATE card {card_id} {status}')
            else:
                print(self.format_error("Parâmetros inválidos."))
        elif sub == '4':
            card_id = input("ID do Cartão a deletar: ").strip()
            if card_id:
                self._handle_command(f'DELETE card {card_id}')

    def _handle_command(self, cmd: str):
        """Envia comando simples e lida com resposta formatada."""
        response = self._send_and_recv(cmd)
        if self._is_error(response):
            print(self.format_error(response.get('data', 'Unknown Error')))
        else:
            print(self.format_success(response.get('data', '')))

    def interactive_transfer(self):
        """Transferência adaptada para o novo protocolo (4 argumentos)."""
        print(f"\n{C}--- Nova Transferência ---{E}")
        destiny = input("Conta de destino: ").strip()
        if not destiny: return
        
        value = input("Valor a transferir (Ex: 150.50): ").strip()
        if not value: return

        card_number = input("Número do cartão utilizado: ").strip()
        if not card_number: return

        cvv = input("CVV do cartão: ").strip()
        if not cvv: return

        cmd = f"TRANSFER {destiny} {value} {card_number} {cvv}"
        self._handle_command(cmd)

    def interactive_update_key(self):
        """Atualização de chave adaptada ao protocolo UPDATE key <valor>."""
        print(f"\n{C}--- Atualizar Chave da Conta ---{E}")
        new_key = input("Digite a nova chave: ").strip()
        if not new_key: return
        
        cmd = f"UPDATE key {new_key}"
        self._handle_command(cmd)

    def interactive_export(self):
        """Solicita a serialização da sessão e salva em arquivo local."""
        print(f"\n{C}--- Exportar Sessão ---{E}")
        response = self._send_and_recv('EXPORT')
        
        if self._is_error(response):
            print(self.format_error(response.get('data', 'Erro ao gerar exportação.')))
            return

        data = response.get('data', '')
        default_name = "session.dat"
        filepath = input(f"Salvar em (Enter para './{default_name}'): ").strip()
        
        if not filepath:
            filepath = default_name

        try:
            with open(filepath, 'w') as f:
                f.write(data)
            print(self.format_success(f'Sessão salva em -> {filepath}'))
        except Exception as e:
            print(self.format_error(f"Falha ao salvar o arquivo: {e}"))

    def format_error(self, msg: str) -> str:
        return f'[{R}Err{E}] {msg}'

    def format_success(self, msg) -> str:
        response: str = ''

        if isinstance(msg, dict):
            for key, item in msg.items():
                response += f'[{G}+{E}] {key} - {item}\n'

        elif isinstance(msg, list):
            for dic in msg:
                if isinstance(dic, dict):
                    flow = dic.get('flow', '')
                    if flow == 'in':
                        response += f'[{G}+{E}] '
                    elif flow == 'out':
                        response += f'[{R}-{E}] '
                    else:
                        response += f'[{G}+{E}] '
                        
                    response += ' :: '.join([f"{k} - {v}" for k, v in dic.items()]) + '\n'
                else:
                    response += f'[{G}+{E}] {dic}\n'

        elif isinstance(msg, str):
            response = f'[{G}+{E}] {msg}'

        return response.strip()


def main():
    parser = argparse.ArgumentParser(description="Cliente para o servidor CryptaBank")
    parser.add_argument('addr', type=str, help='Endereço IP do servidor CryptaBank')
    parser.add_argument('port', type=int, nargs='?', default=9000, help='Porta do servidor (default=9000)')
    parser.add_argument('-s', '--session', type=str, help='Caminho para arquivo de sessão (.dat)')
    
    args = parser.parse_args()

    bank = BankCli(addr=args.addr, port=args.port, session_file=args.session)
    
    try:
        bank.connect_and_run()
    except KeyboardInterrupt:
        print('\n\nO usuário escolheu sair (Ctrl+C)')
        sys.exit(0)

if __name__ == '__main__':
    main()