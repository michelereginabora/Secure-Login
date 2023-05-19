from flask import Flask, render_template, request
import sqlite3
import bcrypt

app = Flask(__name__)


def criar_tabela():
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            senha TEXT
        )
    ''')

    conn.commit()
    conn.close()


def gerar_hash_senha(senha):
    salt = bcrypt.gensalt()
    hash_senha = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hash_senha.decode('utf-8')


def cadastrar_usuario(nome, senha):
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()

    hash_senha = gerar_hash_senha(senha)

    cursor.execute('INSERT INTO usuarios (nome, senha) VALUES (?, ?)', (nome, hash_senha))

    conn.commit()
    conn.close()


def verificar_hash_senha(senha, hash_senha):
    hash_bytes = hash_senha.encode('utf-8')
    return bcrypt.checkpw(senha.encode('utf-8'), hash_bytes)


def verificar_usuario(nome, senha):
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuarios WHERE nome = ?', (nome,))
    usuario = cursor.fetchone()

    if usuario is not None:
        hash_senha = usuario[2]
        if verificar_hash_senha(senha, hash_senha):
            return True

    conn.close()
    return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    senha = request.form['senha']

    if nome == '' or senha == '':
        return 'Por favor, preencha todos os campos.'

    criar_tabela()
    cadastrar_usuario(nome, senha)

    return 'Usuário cadastrado com sucesso.'


@app.route('/verificar', methods=['POST'])
def verificar():
    nome = request.form['nome']
    senha = request.form['senha']

    if nome == '' or senha == '':
        return 'Por favor, preencha todos os campos.'

    if verificar_usuario(nome, senha):
        return 'Usuário válido.'
    else:
        return 'Usuário inválido.'


if __name__ == '__main__':
    app.run(debug=True)
