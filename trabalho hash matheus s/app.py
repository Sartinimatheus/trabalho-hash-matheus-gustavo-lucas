# app.py
"""
Aplicação Flask simples para:
 - cadastrar usuário (email + senha)
 - armazenar senha por HASH (password hashing)
 - fazer login comparando hashes
 - mostrar página simples após login

Explicações inline para iniciantes.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from conexao import criar_conexao
from mysql.connector import Error


app = Flask(__name__)
app.secret_key = "troque_essa_chave_por_uma_aleatoria_e_segura"  # necessário para session e flash

# ---------------------
# Rota: página inicial
# ---------------------
@app.route('/')
def index():
    # se o usuário estiver logado (guardamos email na session), mostramos home
    if session.get('user_email'):
        return render_template('home.html', email=session['user_email'])
    # caso contrário, redireciona para login
    return redirect(url_for('login'))

# ---------------------
# Rota: registrar (GET mostra formulário, POST processa)
# ---------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # pega dados do formulário
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        # validações simples (pode melhorar)
        if not email or not senha:
            flash("Preencha email e senha.", "warning")
            return render_template('register.html')

        # faz o hash da senha antes de salvar
        # usar method 'pbkdf2:sha256' ou outro padrão do werkzeug
        hashed = generate_password_hash(senha)  # por padrão usa pbkdf2:sha256

        conexao = criar_conexao()
        if not conexao:
            flash("Erro: não foi possível conectar ao banco.", "danger")
            return render_template('register.html')

        try:
            cursor = conexao.cursor()
            # usamos placeholder (%s) para prevenir SQL injection
            sql = "INSERT INTO user (email, senha) VALUES (%s, %s)"
            cursor.execute(sql, (email, hashed))
            conexao.commit()

            flash("Usuário cadastrado com sucesso! Faça login.", "success")
            return redirect(url_for('login'))

        except Error as e:
            # se email já existir (campo UNIQUE), tratamos o erro
            # aqui mostramos mensagem simples ao usuário
            flash(f"Erro ao cadastrar: {e}", "danger")
            return render_template('register.html')

        finally:
            if cursor:
                cursor.close()
            if conexao.is_connected():
                conexao.close()

    # se GET, apenas renderiza o formulário
    return render_template('register.html')

# ---------------------
# Rota: login (GET mostra formulário, POST processa)
# ---------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        if not email or not senha:
            flash("Preencha email e senha.", "warning")
            return render_template('login.html')

        conexao = criar_conexao()
        if not conexao:
            flash("Erro: não foi possível conectar ao banco.", "danger")
            return render_template('login.html')

        try:
            cursor = conexao.cursor()
            sql = "SELECT id, email, senha FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            resultado = cursor.fetchone()  # pega 1 resultado (ou None)

            if not resultado:
                # usuário não encontrado
                flash("Email não cadastrado.", "danger")
                return render_template('login.html')

            id_user, email_db, senha_hash_db = resultado

            # Verificamos a senha informada comparando com o hash do DB
            if check_password_hash(senha_hash_db, senha):
                # senha correta -> criar sessão simples
                session['user_email'] = email_db
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('index'))
            else:
                flash("Senha incorreta.", "danger")
                return render_template('login.html')

        except Error as e:
            flash(f"Erro ao buscar usuário: {e}", "danger")
            return render_template('login.html')

        finally:
            if cursor:
                cursor.close()
            if conexao.is_connected():
                conexao.close()

    return render_template('login.html')

# ---------------------
# Rota: logout
# ---------------------
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash("Você saiu da conta.", "info")
    return redirect(url_for('login'))

# ---------------------
# Executa app
# ---------------------
if __name__ == '__main__':
    # em ambiente de desenvolvimento: debug=True para recarregar automaticamente
    app.run(host='127.0.0.1', port=5000, debug=True)
