from src import bank, User, Transfers, Cards
from src.utils import Response
from src.session import Session

import base64
import pickle


def require_auth(f):
    def wrapper(session: Session, *args, **kwargs):
        if not session.user:
            return Response.render_response('Not authorized', 'E')
        return f(session, *args, **kwargs)
    return wrapper


@bank.command('HELP', help='Exibe essa mensagem')
def help(*_) -> bytes:
    return Response.render_response(bank.help(), 'S')

@bank.command('BALANCE', help='Exibe o saldo da sua conta')
@require_auth
def saldo(session: Session, _) -> bytes:
    saldo_ = session.user.balance / 100

    return  Response.render_response(saldo_, 'S')

@bank.command('REGISTER', help='Registra usuário (ex: REGISTER "username" "password")')
def register(session, args) -> bytes:
    if len(args) < 2:
        return Response.render_response('Você precisa informar o username e a senha', 'E')
    success: bool = User.create_user(args[0], args[1])
    if success:
        return Response.render_response('OK', 'S')

    return Response.render_response('Erro no cadastro', 'E')


@bank.command('CREATE', help='Cria algo, opções: card "holder", user "username" "password"')
@require_auth
def create(session: Session, args) -> bytes:
    if len(args) < 2:
        return Response.render_response('Argumentos insuficientes', 'E')
    if args[0].lower() == 'card':
        holder: str = " ".join(args[1:])
        success: bool = Cards.create_card(session.user, holder)

        if success:
            return Response.render_response('OK', 'S')

        return Response.render_response('Cartão já existe', 'E')

    return Response.render_response('Erro no Create', 'E')


@bank.command('CARDS', help='Lista de cartoes')
@require_auth
def list_cards(session: Session, args) -> bytes:
    cards = Cards.list_user_cards(session.user)
    if not cards:
        return Response.render_response('O usuário não possui nenhum cartão', 'S')

    return Response.render_response(cards, 'S')


@bank.command('TRANSACTIONS', help='Historico de transferencias')
@require_auth
def transfers(session: Session, _) -> bytes:
    transfers: list[dict[str, str]] = Transfers.list_user_transfs(session.user.id)
    
    for t in transfers:
        if t['source'] == session.user.id:
            t['flow'] = 'out'
            t['source'] = session.user.username
            t['destiny'] = User.load_user(t['destiny']).username

        if t['destiny'] == session.user.id:
            t['flow'] = 'in'
            t['destiny'] = session.user.username
            t['source'] = User.load_user(t['source']).username

        t['value'] = int(t['value']) / 100

    return Response.render_response(transfers, 'S')


@bank.command('INFO', help='Exibe as informações da sua conta')
@require_auth
def info(session: Session, _) -> bytes:
    saldo = f'{(session.user.balance / 100):.2f}'.replace('.', ',')
    infos = {
        'id': session.user.id, 
        'username': session.user.username, 
        'balance': saldo, 
        'key': session.user.key
        }

    return Response.render_response(infos, 'S')    


@bank.command('DELETE', help='DELETE a user item (card)')
def delete(session: Session, args: list[str]) -> bytes:
    if len(args) < 2:
        return Response.render_response('DELETE command takes 2 argumments (item, item_id)')

    if args[0].lower() == 'card':
        Cards.delete_card(args[1])
        return Response.render_response('Card deleted successfully', 'S')

    return Response.render_response('Invalid DELETE option')


@bank.command('UPDATE', help='Updates a user item ($> UPDATE newkey)')
@require_auth
def update_key(session: Session, args: list[str]) -> bytes:
    if len(args) >= 2:
        item: str = args[0]
        value: str = args[1]

        if item.lower() == 'key':
            success: bool = session.user.update_key(value)

            if not success:
                return Response.render_response('Key could not be updated.', 'E')

            return Response.render_response(session.user.key, 'S')

        elif item.lower() == 'card':
            if len(args) != 3:
                return Response.render_response('UPDATE card takes 3 argumments -> UPDATE card card_id block_status (0/1)', 'E')
            
            block = args[2]
            success: bool = Cards.update_card(value, block)
            if not success:
                return Response.render_response('Card UPDATE error', 'E')
            
            return Response.render_response('OK', 'S')

    return Response.render_response('UPDATE command takes 2 argumments', 'E')


@bank.command('TRANSFER', help='TRANSFER an x value to a y account (Ex: TRANSFER conta_y valor_x)')
@require_auth
def transfer(session: Session, args: list) -> bytes:
    if len(args) == 4:
        destiny: str = args[0] 
        card_number: str = args[2]
        cvv: str = args[3]

        try:
            value = int(float(args[1]) * 100)
        except ValueError:
            return Response.render_response('Invalid value', 'E')

        if Cards.transfer(session.user.id, destiny, value, card_number, cvv):
            return Response.render_response(f'Transferência para {destiny} no valor de R$ {value / 100} bem sucedida', 'S')
        
        return Response.render_response(f'Não é possível transferir R$ {value / 100} para {destiny}.', 'E')

    return Response.render_response('Invalid argumments number', 'E')


@bank.command('LIST', help='Lista todas as transferências realizadas')
@require_auth
def list_transfers(session: Session, args) -> bytes:

    if args[0].lower() == 'cards':
        return list_cards(session, args)

    elif args[0].lower() == 'transfers':
        return transfers(session, args)

    return Response.render_response('Você precisa especificar o que quer listar, ex: (LIST cards || LIST transfers)', 'E')


@bank.command('LOGIN', help='Recebe o username como argumento e inicia o processo de login')
def login(session: Session, args) -> bytes:
    session.username = args[0]

    return Response.render_response('OK', 'S')


@bank.command('PASSWORD', help='Recebe a senha para o username digitado anteriormente')
def password(session: Session, args) -> bytes:
    if not session.username:
        return Response.render_response('LOGIN was not given', 'E')

    session.user = User.log_in(session.username, args[0])
    if not session.user:
        return Response.render_response('Invalid LOGIN or PASSWORD', 'E')
    
    return Response.render_response('WELCOME', 'S')


@bank.command('IMPORT', help='Importa uma sessão para o banco')
def import_(session: Session, args) -> bytes:
    try:
        session_bytes = base64.b64decode(args[0])
    except:
        return Response.render_response('Erro ao carregar sessão', 'E')

    try:
        desserial_session: Session = pickle.loads(session_bytes)
    except Exception as e:
        print(f'Erro: {type(e).__name__}: {e!r}')
        return Response.render_response('Erro ao carregar sessão', 'E')

    try:
        session.load_session(desserial_session)
    except AttributeError as e:
        print(f'Erro ao carregar sessão: {e!r}')
        return Response.render_response('Sessão inválida', 'E')

    return Response.render_response('WELCOME', 'S')


@bank.command('EXPORT', help='Exporta a sessão atual')
@require_auth
def export_(session: Session, _) -> bytes:
    serialized_session: str = base64.b64encode(pickle.dumps(session)).decode('utf-8')

    return Response.render_response(serialized_session, 'S')

