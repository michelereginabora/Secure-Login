from flask import Flask, render_template, request
import sqlite3
import bcrypt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth


app = Flask(__name__)


def create_table():
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            passw TEXT,
            telephone VARCHAR
        )
    ''')

    conn.commit()
    conn.close()


def create_password_hash(passw):
    salt = bcrypt.gensalt()
    hash_passw = bcrypt.hashpw(passw.encode('utf-8'), salt)
    return hash_passw.decode('utf-8')


def register_user(name, passw, telephone):
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    hash_passw = create_password_hash(passw)

    cursor.execute('INSERT INTO user (name, passw, telephone) VALUES (?, ?, ?)', (name, hash_passw, telephone))

    conn.commit()
    conn.close()


def verifify_hash_passw(passw, hash_passw):
    hash_bytes = hash_passw.encode('utf-8')
    return bcrypt.checkpw(passw.encode('utf-8'), hash_bytes)


def verifify_user(name, passw):
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM user WHERE name = ?', (name,))
    user = cursor.fetchone()

    if user is not None:
        hash_passw = user[2]
        if verifify_hash_passw(passw, hash_passw):
            return True

    conn.close()
    return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    passw = request.form['passw']
    telephone = request.form["telephone"]

    if name == '' or passw == '' or telephone == "":
        return 'Por favor, preencha todos os campos.'

    create_table()
    register_user(name, passw, telephone)

    return render_template('index.html', message1='Usuário cadastrado com sucesso.')


@app.route('/verify', methods=['POST'])
def verify():
    name = request.form['name']
    passw = request.form['passw']

    if name == '' or passw == '':
        return 'Por favor, preencha todos os campos.'

    if verifify_user(name, passw):
        return render_template('index.html', message2='Usuário válido.')
    else:
        return render_template('index.html', message2='Usuário inválido.')


@app.route('/verify_sms', methods=['POST'])
def verify_sms():
    cred = credentials.Certificate("loginseguroapp-firebase-adminsdk-ouo6b-f7a7db78cc.json")
    firebase_admin.initialize_app(cred)
    return render_template('verify_sms.html')


if __name__ == '__main__':
    app.run(debug=True)
