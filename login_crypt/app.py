from twilio.rest import Client
from flask import Flask, render_template, request
import sqlite3
import bcrypt
import requests


app = Flask(__name__)

account_sid = 'AC81bbdd0121e419f77661c57e067b7883'
auth_token = '43c579e185e7608467f61cd169585530'
service_sid = 'VAc29e600fc81669f26f319833cf1ffc64'


def create_table():
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                passw TEXT,
                number_phone VARCHAR
            )
        ''')

    conn.commit()
    conn.close()


def create_password_hash(passw):
    salt = bcrypt.gensalt()
    hash_passw = bcrypt.hashpw(passw.encode('utf-8'), salt)
    return hash_passw.decode('utf-8')


def register_user(name, passw, number_phone):
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    hash_passw = create_password_hash(passw)

    cursor.execute('INSERT INTO user (name, passw, number_phone) VALUES (?, ?, ?)', (name, hash_passw, number_phone))

    conn.commit()
    conn.close()


def verify_hash_passw(passw, hash_passw):
    return bcrypt.checkpw(passw.encode('utf-8'), hash_passw.encode('utf-8'))


def verify_user(name, passw):
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    cursor.execute('SELECT passw FROM user WHERE name = ?', (name,))
    user = cursor.fetchone()

    conn.close()

    if user is not None:
        hash_passw = user[0]
        if verify_hash_passw(passw, hash_passw):
            return True  # Retorna True se a senha estiver correta
    
    return False  # Retorna False se o usuário não for encontrado ou a senha estiver incorreta


def create_verify_service():
    url = 'https://verify.twilio.com/v2/Services'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'FriendlyName': 'secureLogin'  # Nome amigável do serviço de verificação
    }
    response = requests.post(url, data=data, auth=(account_sid, auth_token), headers=headers)
    service_sid = response.json().get('sid')
    return service_sid

# Envio da solicitação de verificação


def send_verification_sms(number_phone):
    client = Client(account_sid, auth_token)
    verification = client.verify.v2.services(service_sid) \
        .verifications \
        .create(to=number_phone, channel="sms")

    return verification.sid


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    passw = request.form['passw']
    number_phone = request.form.get("number_phone", None)

    if name == '' or passw == '' or number_phone == "":
        return 'Por favor, preencha todos os campos.'

    create_table()
    register_user(name, passw, number_phone)

    return render_template('index.html', message1='Usuário cadastrado com sucesso.')


@app.route('/verify', methods=['POST'])
def verify():
    name = request.form['name']
    passw = request.form['passw']

    print(f'Nome recebido: {name}')  # Mensagem de depuração para verificar o nome recebido do formulário
    print(f'Senha recebida: {passw}')  # Mensagem de depuração para verificar a senha recebida do formulário

    if name == '' or passw == '':
        return 'Preencha todos os campos' 

    if verify_user(name, passw):
        print('Usuário válido.')  # Mensagem de depuração para verificar se o usuário foi validado com sucesso
        return render_template('index.html', message2='Usuário válido.')
    else:
        print('Não encontrado.')  # Mensagem de depuração para verificar se o usuário foi considerado inválido
        return render_template('index.html', message2='Usuário inválido.')


@app.route('/twofactor', methods=['POST'])
def twofactor():
    number_phone = request.form['number_phone']
    otp_code = request.form['otp_code']

    if not number_phone:
        return render_template('index.html', message='Por favor, insira um número de telefone e um código OTP.')

    client = Client(account_sid, auth_token)
    verification_check = client.verify.v2.services(service_sid) \
        .verifications \
        .create(to=number_phone, channel="sms")
    if not otp_code:
        return "invalido"
    if verification_check.status == 'approved':
        return render_template('index.html', message='Verificação aprovada. Acesso concedido.')
    else:
        return render_template('index.html', message='Verificação falhou. Acesso negado.')


if __name__ == '__main__':
    app.run(debug=True)
