from app import app 
from app.cryptacommuni import access

from flask import render_template, request, url_for, make_response, redirect
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        a = access()
        token = request.cookies.get('token')
        if token:
            if a.check_token(token):
                return f(a, *args, **kwargs)
        return redirect(url_for('login'))
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username: str = request.form.get('username')
    password: str = request.form.get('password')

    if not username or not password:
        return render_template('login.html', error='Digite o username e a senha!')

    log = access().login(username, password)
    if log[0]:
        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('token', log[1])
        return response

    return render_template('login.html', error='Username ou senha inválidos!')


@app.route('/register', methods=['POST'])
def register():
    username: str = request.form.get('username')
    password: str = request.form.get('password')

    if not username or not password:
        return render_template('login.html', error='Digite o username e a senha!')

    log = access().register(username, password)

    if log[0]:
        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('token', log[1])
        return response

    return render_template('login.html', error='Username ou senha inválidos!')


@app.route('/dashboard')
@login_required
def dashboard(_):
    return render_template('dashboard.html')