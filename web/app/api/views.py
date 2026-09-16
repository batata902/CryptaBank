from app.api import api
from app.cryptacommuni import access
from app.views import login_required

from flask import jsonify, request, make_response

@api.route('/cards', methods=['GET', 'POST'])
@login_required
def cards(a):
    if request.method == 'GET':
        cards_: dict = a.send_recv('CARDS')
        return jsonify(cards_['data']), 200

    holder = request.json.get('holder')

    create_card: dict = a.send_recv(f'CREATE card {holder}')

    return jsonify(create_card), 200


@api.route('/cards/<card_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
@login_required
def card(a, card_id):
    card_id: str = request.view_args.get('card_id')

    if request.method == 'GET':
        card_: dict = a.send_recv(f'CARD {card_id}')
        return jsonify(card_), 200

    if request.method == 'DELETE':
        delete_card: dict = a.send_recv(f'DELETE card {card_id}')
        return jsonify(delete_card), 200

    if request.method == 'PATCH':
        blocked = request.json.get('blocked')
        update_card: dict = a.send_recv(f'UPDATE card {card_id} {"0" if blocked is False else "1"}')
        return jsonify(update_card), 200

    if request.method == 'PUT':
        holder: str = request.json.get('holder')
        update_card: dict = a.send_recv(f'')


@api.route('/balance')
@login_required
def balance(a):
    balance_ = a.send_recv('BALANCE')

    return jsonify(balance_), 200

@api.route('/transactions')
@login_required
def transactions(a):
    transactions_ = a.send_recv('TRANSACTIONS')

    return jsonify(transactions_['data']), 200

@api.route('/transfers', methods=['POST'])
@login_required
def transfer(a):
    destiny: str = request.json.get('destination')
    value: str = request.json.get('value')
    card_number: str = request.json.get('cardNumber')
    cvv: str = request.json.get('cvv')

    value: float = float(value)
    response = a.send_recv(f'TRANSFER {destiny} {value} {card_number} {cvv}')

    if response['status'] == 100:
        return jsonify(error='Não foi possível fazer a transferencia'), 400
    
    return jsonify(response), 200

@api.route('/transfer-key')
@login_required
def key(a):
    response: dict = a.send_recv(f'INFO')

    if response['status'] == 100:
        return jsonify(error='Não foi possível obter a chave'), 400
    return jsonify(response['data']), 200


@api.route('/logout', methods=['POST'])
@login_required
def logout(_):
    response = make_response(jsonify(success=True), 200)
    response.delete_cookie('token')

    return response
