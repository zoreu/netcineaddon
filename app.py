from flask import Flask, jsonify, request, make_response, render_template
from netcine import catalog_search, search_link

app = Flask(__name__)

# Função para adicionar headers CORS
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # Permite todos os domínios
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  # Métodos permitidos
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Headers permitidos
    return response


MANIFEST = {
        "id": "com.netcineaddon",
        "version": "1.0.0",
        "name": "NETCINE",
        "description": "Tenha o melhor dos filmes e séries com netcine",
        'logo': 'https://i.imgur.com/GCnr8Nm.png',
        "resources": ["catalog", "stream"],  # Adicione "catalog/search"
        "types": ["movie", "series"],  # Tipos de conteúdo suportados
        "catalogs": [
            {
                "type": "movie",
                "id": "netcine",
                "name": "IMDB",
                "extraSupported": ["search"]
            },
            {
                "type": "series",
                "id": "netcine",
                "name": "IMDB",
                "extraSupported": ["search"]
            }
        ],
        "idPrefixes": ["tt"]
    }

@app.route('/')
def home():
    name = MANIFEST['name']
    types = MANIFEST['types']
    logo = MANIFEST['logo']
    description = MANIFEST['description']
    version = MANIFEST['version']
    return render_template('index.html', name=name, types=types, logo=logo, description=description, version=version)

# Rota para o manifesto do addon
@app.route('/manifest.json')
def manifest():
    response = jsonify(MANIFEST)
    return add_cors_headers(response)

# Rota para o catálogo
@app.route('/catalog/<type>/<id>.json')
def catalog_route(type, id):
    response = jsonify({
        "metas": []
    })
    return add_cors_headers(response)

# Rota para pesquisa
@app.route('/catalog/<type>/netcine/search=<query>.json')
def search(type, query):
    catalog = catalog_search(query)
    if catalog:
        results = [item for item in catalog if item.get('type', '') == type]
    else:
        results = []
    response = jsonify({
        "metas": results
    })
    return add_cors_headers(response)

# Rota para streams (exemplo simples)
@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    try:
        stream_, headers = search_link(id)
        scrape_ = [{
                "url": stream_,
                "name": "NETCINE",
                "description": "NETCINE",
                "behaviorHints": {
                    "notWebReady": True,
                    "proxyHeaders": {
                        "request": {
                            "User-Agent": headers['User-Agent'],
                            "Referer": headers['Referer'],
                            "Cookie": headers['Cookie']
                        }
                    }
                }
            }]
    except:
        scrape_ = []   
    response = jsonify({
        "streams": scrape_
    })
    return add_cors_headers(response)

# Rota para lidar com requisições OPTIONS (necessário para CORS)
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    return add_cors_headers(response)

if __name__ == '__main__':
    # executar server
    app.run(debug=True ,host='0.0.0.0', port=80)
