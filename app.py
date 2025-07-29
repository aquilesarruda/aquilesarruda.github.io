from flask import Flask, render_template, request, redirect, flash, url_for
import os
from collections import Counter

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessária para flash()
ARQUIVO = 'dados.txt'


# ----------------------------
# Funções auxiliares
# ----------------------------

def carregar_dados():
    """Carrega os registros do arquivo."""
    if not os.path.exists(ARQUIVO):
        return []

    with open(ARQUIVO, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    registros = []
    for linha in linhas:
        campos = linha.strip().split(',')
        while len(campos) < 4:
            campos.append('')
        registros.append(campos)
    return registros


def salvar_dados(dados):
    """Salva os registros no arquivo."""
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        for registro in dados:
            f.write(','.join(registro) + '\n')


def validar_formulario(form):
    """Valida e retorna os dados do formulário."""
    nome = form.get('nome', '').strip()
    idade = form.get('idade', '').strip()
    bairro = form.get('bairro', '').strip()

    if not nome or not idade or not bairro:
        flash('Todos os campos são obrigatórios.', 'danger')
        return None

    return nome, idade, bairro


# ----------------------------
# Rotas principais
# ----------------------------

@app.route('/')
def index():
    registros = carregar_dados()
    bairros = [r[3] for r in registros if r[3]]
    contagem_bairros = Counter(bairros)

    return render_template('index.html',
                           registros=registros,
                           contagem_bairros=contagem_bairros)


@app.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        resultado = validar_formulario(request.form)
        if not resultado:
            return redirect(request.url)

        nome, idade, bairro = resultado
        dados = carregar_dados()
        novo_id = str(max([int(r[0]) for r in dados], default=0) + 1)

        dados.append([novo_id, nome, idade, bairro])
        salvar_dados(dados)
        flash('Registro criado com sucesso!', 'success')
        return redirect(url_for('index'))

    registro = {'nome': '', 'idade': '', 'bairro': ''}
    return render_template('form.html', acao='Criar', registro=registro)


@app.route('/editar/<id>', methods=['GET', 'POST'])
def editar(id):
    dados = carregar_dados()
    registro = next((r for r in dados if r[0] == id), None)

    if not registro:
        return 'Registro não encontrado.', 404

    if request.method == 'POST':
        resultado = validar_formulario(request.form)
        if not resultado:
            return redirect(request.url)

        nome, idade, bairro = resultado
        registro[1] = nome
        registro[2] = idade
        registro[3] = bairro
        salvar_dados(dados)
        flash('Registro atualizado com sucesso!', 'success')
        return redirect(url_for('index'))

    registro_dict = {'id': registro[0], 'nome': registro[1], 'idade': registro[2], 'bairro': registro[3]}
    return render_template('form.html', acao='Editar', registro=registro_dict)


@app.route('/deletar/<id>')
def deletar(id):
    dados = carregar_dados()
    novos_dados = [r for r in dados if r[0] != id]

    if len(novos_dados) == len(dados):
        flash('Registro não encontrado.', 'warning')
    else:
        salvar_dados(novos_dados)
        flash('Registro deletado com sucesso!', 'success')

    return redirect(url_for('index'))


# ----------------------------
# Execução
# ----------------------------

if __name__ == '__main__':
    app.run(debug=True)
