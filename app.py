from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'  # Troque por uma segura

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado')
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        flash('Nome de arquivo vazio')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Leitura do Excel
        df = pd.read_excel(filepath)

        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['Abertura', 'Auxílio', 'Cidade', 'Ass. Social']
        if not all(coluna in df.columns for coluna in colunas_obrigatorias):
            flash('Arquivo inválido. Colunas obrigatórias ausentes.')
            return redirect(url_for('dashboard'))

        # Converter DataFrame em HTML para exibir (exemplo básico)
        tabela_html = df.to_html(classes='table table-striped', index=False)

        return render_template('dashboard.html', tabela=tabela_html)

    else:
        flash('Formato de arquivo não permitido. Apenas .xlsx')
        return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
