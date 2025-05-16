from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

dataframe = None

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == '1234':
        session['user'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html', error='Credenciais inválidas.')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload():
    global dataframe
    file = request.files['file']
    if file.filename.endswith('.xlsx'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(filepath)
        dataframe = pd.read_excel(filepath, engine='openpyxl')
        if all(col in dataframe.columns for col in ['Abertura', 'Auxílio', 'Cidade', 'Ass. Social']):
            session['uploaded'] = True
        else:
            return render_template('dashboard.html', error='Arquivo inválido. Verifique os nomes das colunas.')
    return redirect(url_for('graficos'))

@app.route('/visualizar')
def visualizar():
    if 'user' not in session or 'uploaded' not in session:
        return redirect(url_for('home'))
    return render_template('visualizar.html', tables=[dataframe.to_html(classes='table table-bordered', index=False)], titles=dataframe.columns.values)

@app.route('/graficos')
def graficos():
    if 'user' not in session or 'uploaded' not in session:
        return redirect(url_for('home'))

    fig_auxilio = px.pie(dataframe, names='Auxílio', title='Distribuição por Tipo de Auxílio')
    grafico_auxilio = pio.to_html(fig_auxilio, full_html=False)

    fig_cidade = px.bar(dataframe['Cidade'].value_counts().reset_index(),
                        x='index', y='Cidade',
                        labels={'index': 'Cidade', 'Cidade': 'Total'},
                        title='Atendimentos por Cidade')
    grafico_cidade = pio.to_html(fig_cidade, full_html=False)

    return render_template('graficos.html', grafico_auxilio=grafico_auxilio, grafico_cidade=grafico_cidade)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('uploaded', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)