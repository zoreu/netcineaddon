from flask import Flask, jsonify, request, make_response, render_template
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def resolve_vod(url):
    parsed_url = urlparse(url)
    referer = '%s://%s/'%(parsed_url.scheme,parsed_url.netloc)        
    stream = ''
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/88.0.4324.96 Safari/537.36"}
    headers.update({'Cookie': 'XCRF%3DXCRF', 'Referer': referer})
    try:
        # find player
        r = requests.get(url,headers=headers)
        src = r.text
        soup = BeautifulSoup(src, 'html.parser')
        url = soup.find('div', {'id': 'content'}).find_all('a')[0].get('href', '') 
    except:
        pass        
            
    try:
        r = requests.get(url,headers=headers)
        src = r.text
        regex_pattern = r'<source[^>]*\s+src="([^"]+)"'
        alto = []
        baixo = []
        matches = re.findall(regex_pattern, src)
        for match in matches:
            if 'ALTO' in match:
                alto.append(match)
            if 'alto' in match:
                alto.append(match)
            if 'BAIXO' in match:
                baixo.append(match)
            if 'baixo' in match:
                baixo.append(match)
        # if alto:
        #     stream = alto[-1] + '|User-Agent=' + USER_AGENT + '&Referer=' + headers['Referer'] + '&Cookie=' + headers['Cookie']
        # elif baixo:
        #     stream = baixo[-1] + '|User-Agent=' + USER_AGENT + '&Referer=' + headers['Referer'] + '&Cookie=' + headers['Cookie']   
        if alto:
            stream = alto[-1]
        elif baixo:
            stream = baixo[-1]        
    except:
        pass
    return stream, headers

# Função para adicionar headers CORS
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # Permite todos os domínios
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  # Métodos permitidos
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Headers permitidos
    return response

# Exemplo de catálogo de filmes e séries
catalog = [
    {
        "id": "tt0111161",
        "type": "movie",
        "title": "The Shawshank Redemption",
        "year": 1994,
        "poster": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg"
    },
    {
        "id": "tt0068646",
        "type": "movie",
        "title": "The Godfather",
        "year": 1972,
        "poster": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg"
    },
    {
        "id": "tt0944947",
        "type": "series",
        "title": "Game of Thrones",
        "year": 2011,
        "poster": "https://m.media-amazon.com/images/M/MV5BYTRiNDQwYzAtMzVlZS00NTI5LWJjYjUtMzkwNTUzMWMxZTllXkEyXkFqcGdeQXVyNDIzMzcwNjc@._V1_SX300.jpg"
    }
]

@app.route('/')
def home():
    name = 'Meu Addon de Filmes e Séries'
    types = ["movie", "series"]
    logo = 'https://i.imgur.com/qVgkbYn.png'
    description = "Um addon simples para Stremio que fornece filmes e séries."
    version = "1.0.0"
    return render_template('index.html', name=name, types=types, logo=logo, description=description, version=version)

# Rota para o manifesto do addon
@app.route('/manifest.json')
def manifest():
    response = jsonify({
        "id": "com.example.stremio.addon",
        "version": "1.0.0",
        "name": "Meu Addon de Filmes e Séries",
        "description": "Um addon simples para Stremio que fornece filmes e séries.",
        "resources": ["catalog", "stream", "catalog/search"],  # Adicione "catalog/search"
        "types": ["movie", "series"],  # Tipos de conteúdo suportados
        "catalogs": [
            {
                "type": "movie",
                "id": "movies",
                "name": "Filmes",
                "extraSupported": ["genre", "skip", "search"]
            },
            {
                "type": "series",
                "id": "series",
                "name": "Séries",
                "extraSupported": ["genre", "skip", "search"]
            }
        ],
        "idPrefixes": ["tt"]
    })
    return add_cors_headers(response)

# Rota para o catálogo
@app.route('/catalog/<type>/<id>.json')
def catalog_route(type, id):
    response = jsonify({
        "metas": [item for item in catalog if item["type"] == type]
    })
    return add_cors_headers(response)

# Rota para pesquisa
@app.route('/catalog/movie/<type>/search=<query>.json')
def search(type, query):
    results = [item for item in catalog if query.lower() in item["title"].lower()]
    response = jsonify({
        "metas": results
    })
    return add_cors_headers(response)

# Rota para streams (exemplo simples)
@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    url = 'https://netcinetv.fi/media-player/nv32mono.php?n=OPCHEFAOP1LEG&p=filmes2023/pchefao'
    stream_, headers = resolve_vod(url)
    scrape_ = [{
            "url": stream_,
            "name": "NETCINE",
            "description": "NETCINE",
            "behaviorHints": {
                "notWebReady": True,
                "proxyHeaders": {
                    "request": {
                        "User-Agent": headers['User-Agent'],
                        "Referer": headers['Referer']
                    }
                }
            }
        }]    
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
    app.run(debug=True ,host='0.0.0.0', port=80)
