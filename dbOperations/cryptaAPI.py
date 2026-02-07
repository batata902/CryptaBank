import json

from flask import Flask, request, jsonify
import sqlite3
import threading

from pydantic import validate_email

from utils.utils import Utils

app = Flask(__name__)
lock = threading.Lock()
conn = sqlite3.connect('cryptabank.sql', check_same_thread=False)

conn.row_factory = sqlite3.Row
cur = conn.cursor()

def create_tables():
    conn.execute('''CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY,
        password TEXT,
        wallet TEXT,
        data TEXT,
        currency INTEGER,
        tfa INTEGER
    );''')
    conn.commit()

    conn.execute('''CREATE TABLE IF NOT EXISTS transfer_history(
        source_wallet TEXT,
        destiny_wallet TEXT,
        value TEXT,
        date TEXT
    );''')
    conn.commit()

    # IMPLEMENTAR
    ''' 
    CREATE TABLE command_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    command VARCHAR(50) NOT NULL,
    args JSON,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('SUCCESS', 'ERROR') NOT NULL,
    error_message TEXT,
    ip_address VARCHAR(45)
);
    '''


@app.route('/add-history', methods=['POST'])
def add_history():
    req = request.get_json()
    source_wallet = req['swallet']
    destiny_wallet = req['dwallet']
    value = req['value']
    date = req['date']

    conn.execute('INSERT INTO transfer_history(source_wallet, destiny_wallet, value, date) VALUES (?, ?, ?, ?);',
                (source_wallet, destiny_wallet, value, date))
    conn.commit()
    return {'status': 'ok'}

@app.route('/consult-history', methods=['GET'])
def consult_history():
    history = []
    consulta = cur.execute('SELECT * FROM transfer_history;')
    while True:
        linhas = consulta.fetchmany(10)
        if not linhas:
            break
        for linha in linhas:
            history.append(dict(linha))
    return history

@app.route('/cadastro', methods=['POST'])
def cadas():
    cadastro = request.get_json()
    with lock:
        try:
            conn.execute('INSERT INTO users(email, password, wallet, data, currency, tfa) VALUES ('
                         '?,'
                         '?,'
                         '?,'
                         '?,'
                         '?,'
                         '?);', (cadastro["email"], cadastro["pass"], cadastro["wallet"], cadastro["data"], cadastro["currency"], cadastro["tfa"]))
            conn.commit()
        except sqlite3.IntegrityError:
            return {"status": "Email already registered"}
    return {"status": "ok"}

@app.route('/getcurrency', methods=['POST'])
def get():
    req = request.get_json()
    wallet = req['wallet']
    senha = req['pass']


    try:
        cur.execute('SELECT currency FROM users WHERE wallet = ? AND password = ?;', (wallet, senha))
        row = dict(cur.fetchone())
    except TypeError:
        return {"status": "user not found"}
    return row

@app.route('/updatecurrency', methods=["POST"])
def updatecurrency():
    infos = request.get_json()

    op = infos["operation"]
    wallet = infos["wallet"]
    new_value = infos["nvalue"]

    '''
    #autenticação
    try:
        cur.execute('SELECT ? FROM users WHERE wallet = ?;', (wallet, wallet))
        row = dict(cur.fetchone())
    except TypeError:
        return {"status": "user not found or wrong password"}
    '''

    row = cur.execute('SELECT currency FROM users WHERE wallet = ?;', (wallet,)).fetchone()
    currency = dict(row)['currency']
    if op == 'add':
        currency += new_value
    elif op == 'sub':
        currency -= new_value
    else:
        return {"status": "invalid operation"}

    conn.execute('UPDATE users SET currency = ? WHERE wallet = ?;', (currency, wallet))
    conn.commit()

    return {"status":"ok"}


@app.route('/seeinfos', methods=['POST'])
def seeinfos():
    req = request.get_json()
    wallet = req['wallet']
    senha = req['pass']

    try:
        if not '@' in wallet:
            consulta = cur.execute('SELECT * FROM users WHERE wallet = ? AND password = ?', (wallet, senha))
        else:
            consulta = cur.execute('SELECT * FROM users WHERE email = ? AND password = ?', (wallet, senha))
        return {'infos': dict(consulta.fetchone())}
    except TypeError:
        return {"infos": "no"}


@app.route('/email-exists', methods=['POST'])
def email_exists():
    email = request.get_json()['email']

    try:
        exists = cur.execute('SELECT email FROM users WHERE email = ?', (email,))
        dict(exists.fetchone())
    except TypeError:
        return {"exists": "false"}
    return {"exists": "true"}

@app.route('/tfaupdate', methods=['POST'])
def tfaupdate():
    req = request.get_json()
    email = req['email']
    senha = req['pass']

    try:
        consulta = cur.execute('SELECT tfa FROM users WHERE email = ? AND password = ?', (email, senha))
        tfa = dict(consulta.fetchone())
    except TypeError:
        return {"status": "account doesn't exists"}
    if tfa['tfa'] == 1:
        conn.execute('UPDATE users SET tfa = 0 WHERE email = ?', (email,))
        conn.commit()
    else:
        conn.execute('UPDATE users SET tfa = 1 WHERE email = ?', (email,))
        conn.commit()
    return {"status": "ok"}


@app.route('/istfaenabled', methods=["POST"])
def tfacheck():
    req = request.get_json()
    email = req["email"]
    senha = req["pass"]

    try:
        consulta = cur.execute('SELECT tfa FROM users WHERE email = ? AND password = ?', (email, senha))
        is_enabled = dict(consulta.fetchone())
    except TypeError:
        return {'status': 'false'}

    if is_enabled["tfa"] == 1:
        return {'status': 'true'}
    return {'status': 'false'}

@app.route('/login', methods=["POST"])
def login():
    req = request.get_json()
    email = req['email']
    senha = req['pass']

    consulta = cur.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, senha))
    try:
        infos = dict(consulta.fetchone())
    except TypeError:
        return {"login": "no"}

    return {"login": infos}

@app.route('/allusers', methods=['GET'])
def allusers():
    users = []
    consulta = cur.execute('SELECT * FROM users;')
    while True:
        linhas = consulta.fetchmany(10)
        if not linhas:
            break
        for linha in linhas:
            users.append(dict(linha))
    return users

@app.route('/depositar', methods=['GET'])
def depositar():
    try:
        email = request.args.get('email')
        valor = int(request.args.get('valor'))
    except TypeError:
        return {'status': 'parâmetros invalidos'}

    try:
        consulta = cur.execute('SELECT currency FROM users WHERE email = ?;', (email,))
        currency = dict(consulta.fetchone())['currency']
    except TypeError:
        return {'status': 'user not found'}

    conn.execute('UPDATE users SET currency = ? WHERE email = ?;', (int(currency) + valor, email))
    conn.commit()

    return {'status': 'ok'}


create_tables()
app.run()