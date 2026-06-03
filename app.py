from flask import Flask, redirect, request, render_template, jsonify
import requests as req
import random, string
from datetime import datetime

app = Flask(__name__)

BIN_ID     = "6a1f8d38da38895dfe7e9a19"
MASTER_KEY = "$2a$10$2Gc8IOu1qvXQpCKD6Fq7F.qbu7VRu9XlQ4o0faWJYHQDJrhjiCUlm"
BASE_URL   = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS    = {"X-Master-Key": MASTER_KEY, "Content-Type": "application/json"}

def carregar():
    r = req.get(BASE_URL + "/latest", headers=HEADERS)
    return r.json()["record"].get("links", {})

def salvar(links):
    req.put(BASE_URL, json={"links": links}, headers=HEADERS)

def gerar_codigo():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

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
        return jsonify({'erro': 'Código já existe'}), 400

    links[codigo] = {
        'url'      : url,
        'cliques'  : 0,
        'criado_em': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    salvar(links)

    base = request.host_url.rstrip('/')
    return jsonify({'codigo': codigo, 'link_curto': f'{base}/{codigo}'})

@app.route('/<codigo>')
def redirecionar(codigo):
    links = carregar()
    if codigo not in links:
        return 'Link não encontrado', 404
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
