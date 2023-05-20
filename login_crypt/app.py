from flask import Flask, render_template, request
import sqlite3
import bcrypt

app = Flask(__name__)


def create_table():
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            passw TEXT
        )
    ''')

    conn.commit()
    conn.close()


def create_password_hash(passw):
    salt = bcrypt.gensalt()
    hash_passw = bcrypt.hashpw(passw.encode('utf-8'), salt)
    return hash_passw.decode('utf-8')


def register_user(name, passw):
    conn = sqlite3.connect('register.db')
    cursor = conn.cursor()

    hash_passw = create_password_hash(passw)

    cursor.execute('INSERT INTO user (name, passw) VALUES (?, ?)', (name, hash_passw))

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

    if name == '' or passw == '':
        return 'Por favor, preencha todos os campos.'

    create_table()
    register_user(name, passw)

    return 'Usuário cadastrado com sucesso.'


@app.route('/verify', methods=['POST'])
def verify():
    name = request.form['name']
    passw = request.form['passw']

    if name == '' or passw == '':
        return 'Por favor, preencha todos os campos.'

    if verifify_user(name, passw):
        return 'Usuário válido.'
    else:
        return 'Usuário inválido.'


if __name__ == '__main__':
    app.run(debug=True)
