from flask import Flask, redirect, request, render_template, jsonify
import json, os, random, string
from datetime import datetime

app = Flask(__name__)
ARQUIVO = 'links.json'

# ── Helpers de armazenamento ──────────────────────────────────────────────────

def carregar():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, 'r') as f:
        return json.load(f)

def salvar(links):
    with open(ARQUIVO, 'w') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)

def gerar_codigo():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# ── Rotas ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', links=carregar())

@app.route('/encurtar', methods=['POST'])
def encurtar():
    data   = request.json
    url    = data.get('url', '').strip()
    codigo = data.get('codigo', '').strip() or gerar_codigo()
    links  = carregar()

    if not url:
        return jsonify({'erro': 'URL obrigatória'}), 400
    if codigo in links:
        return jsonify({'erro': 'Código já existe, escolha outro'}), 400

    links[codigo] = {
        'url'       : url,
        'cliques'   : 0,
        'criado_em' : datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    salvar(links)

    base = request.host_url.rstrip('/')
    return jsonify({'codigo': codigo, 'link_curto': f'{base}/{codigo}'})

@app.route('/<codigo>')
def redirecionar(codigo):
    links = carregar()
    if codigo not in links:
        return 'Link não encontrado 😕', 404
    links[codigo]['cliques'] += 1
    salvar(links)
    return redirect(links[codigo]['url'])

@app.route('/deletar/<codigo>', methods=['DELETE'])
def deletar(codigo):
    links = carregar()
    links.pop(codigo, None)
    salvar(links)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True)