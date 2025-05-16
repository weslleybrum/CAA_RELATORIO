from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xlsx'}

# Usuário e senha fixos
USUARIO_VALIDO = 'admin'
SENHA_VALIDA = '123'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    usuario = request.form['usuario']
    senha = request.form['senha']

    if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
        session['usuario'] = usuario
        return redirect(url_for('dashboard'))
    else:
        flash('Usuário ou senha incorretos.')
        return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    flash('Logout realizado.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        flash('Faça login primeiro.')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado.')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash('Arquivo inválido. Apenas .xlsx são permitidos.')
            return redirect(request.url)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        df = pd.read_excel(filepath)
        colunas = df.columns.tolist()
        dados = df.head(10).to_dict(orient='records')

        return render_template('upload.html', colunas=colunas, dados=dados)

    return render_template('upload.html', colunas=None)

if __name__ == '__main__':
    app.run(debug=True)
