from urllib.parse import urlparse, quote_plus
import requests
from bs4 import BeautifulSoup
import re
import json

def catalog_search(text):
    catalog = []
    url = 'https://v3.sg.media-imdb.com/suggestion/x/' + quote_plus(text) + '.json?includeVideos=1'
    try:
        data = requests.get(url).json()['d']
        for i in data:
            try:
                poster = i['i']['imageUrl']
                id = i['id']
                title = i['l']
                tp = i['qid']
                if 'series' in tp.lower():
                    tp = 'series'
                y = i['y']
                if 'tt' in id:
                    catalog.append({
                        "id": id,
                        "type": tp,
                        "title": title,
                        "year": int(y),
                        "poster": poster
                    })
            except:
                pass
    except:
        pass
    return catalog

def resolve_stream(url):
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
        if alto:
            stream = alto[-1]
        elif baixo:
            stream = baixo[-1]        
    except:
        pass
    return stream, headers

def search_term(imdb):
    url = 'https://www.imdb.com/pt/title/%s/'%imdb
    keys = []
    try:
        r = requests.get(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0', 'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3'})
        src = r.text
        script = re.findall('json">(.*?)</script>', src, re.DOTALL)[0]
        title = re.findall('<title>(.*?)</title>', src)[0]
        data = json.loads(script)
        name = data.get('name', '')
        name2 = data.get('alternateName', '')
        if name:
            keys.append(name)
        if name2:
            keys.append(name2)
        try:
            year_ = re.findall('Série de TV (.*?)\)', title)
            if not year_:
                year_ = re.findall('\((.*?)\)', title)
            if year_:
                year = year_[0]
                try:
                    year = year.split('–')[0]
                except:
                    pass
        except:
            year = ''       

    except:
        pass
    return keys, year

def opcoes_filmes(url,headers, host):
    dublado = []
    legendado = []         
    try:
        headers.update({'Cookie': 'XCRF%3DXCRF'})
        r = requests.get(url,headers=headers)
        src = r.text
        soup = BeautifulSoup(src,'html.parser')
        player = soup.find('div', {'id': 'player-container'})
        botoes = player.find('ul', {'class': 'player-menu'})
        op = botoes.findAll('li')
        op_list = []
        if op:
            for i in op:
                a = i.find('a')
                id_ = a.get('href', '').replace('#', '')
                op_name = a.text
                try:
                    op_name = op_name.decode('utf-8')
                except:
                    pass
                op_name = op_name.replace(' 1', '').replace(' 2', '').replace(' 3', '').replace(' 4', '').replace(' 5', '')
                op_name = op_name.strip()
                op_name = op_name.upper()
                op_list.append((op_name,id_))
        if op_list:
            for name, id_ in op_list:
                iframe = player.find('div', {'class': 'play-c'}).find('div', {'id': id_}).find('iframe').get('src', '')
                if not 'streamtape' in iframe:
                    link = host + iframe
                else:
                    link = iframe
                if 'dublado' in name.lower() and not 'streamtape' in link:
                    dublado.append(link)                    
                elif 'legendado' in name.lower() and not 'streamtape' in link:
                    legendado.append(link)
    except:
        pass
    if dublado:
        return dublado[-1]
    elif legendado:
        return legendado[-1]
    else:
        return ''


def scrape_search(host,headers,text,year_imdb):
    url = requests.get(host,headers=headers).url
    url_parsed = urlparse(url)
    new_host = url_parsed.scheme + '://' + url_parsed.hostname + '/'
    try:
        keys_search = text.split(' ')
        if len(keys_search) > 2:
            search_ = ' '.join(keys_search[:-1])
        else:
            search_ = text
    except:
        search_ = text    
    url_search = new_host + '?s=' + quote_plus(search_)
    headers.update({'Cookie': 'XCRF%3DXCRF'})
    r = requests.get(url_search,headers=headers)
    src = r.text
    soup = BeautifulSoup(src,'html.parser')
    box = soup.find("div", {"id": "box_movies"})
    movies = box.findAll("div", {"class": "movie"})
    for i in movies:
        name = i.find('h2').text
        try:
            name = name.decode('utf-8')
        except:
            pass
        try:
            keys = name.split(' ')
            name2 = ' '.join(keys[:-1])
        except:
            name2 = ''
        try:
            keys2 = text.split(' ')
            text2 = ' '.join(keys2[:-1])
        except:
            text2 = ''                           
        try:
            year = i.find('span', {'class': 'year'}).text
            year = year.replace('–', '')
        except:
            year = ''
        try:
            text = text.lower()
            text = text.replace(':', '')
        except:
            pass
        try:
            name = name.lower()
            name = name.replace(':', '')
        except:
            pass
        try:
            text2 = text2.lower()
        except:
            pass
        try:
            name2 = name2.lower()
        except:
            pass
        if text in name and str(year_imdb) in str(year) or text2 in name2 and str(year_imdb) in str(year):
            img = i.find('div', {'class': 'imagen'})
            link = img.find('a').get('href', '')
            return link, new_host
    return ''   


def search_link(id):
    stream = ''
    host = 'https://netcinetv.fi/'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/88.0.4324.96 Safari/537.36"}
    headers_ = {}
    try:
        if ':' in id:
            parts = id.split(':')
            imdb = parts[0]
            season = parts[1]
            episode = parts[2]
            search_text, year_imdb = search_term(imdb)
            if search_text and year_imdb:
                text = search_text[-1]
                link, new_host = scrape_search(host,headers,text,year_imdb)
                if '/tvshows/' in link:
                    #### SÉRIES EPISODES
                    r = requests.get(link,headers=headers)
                    src = r.text
                    soup = BeautifulSoup(src,'html.parser')
                    s = soup.find('div', {'id': 'movie'}).find('div', {'class': 'post'}).find('div', {'id': 'cssmenu'}).find('ul').findAll('li', {'class': 'has-sub'})
                    for n, i in enumerate(s):
                        n += 1
                        if int(season) == n:
                            e = i.find('ul').findAll('li')
                            for n, i in enumerate(e):
                                n += 1
                                if int(episode) == n:
                                    e_info = i.find('a')
                                    link = e_info.get('href')
                                    page = opcoes_filmes(link,headers, new_host)
                                    stream, headers_ = resolve_stream(page)
                                    break
                            break   
        else:
            imdb = id
            search_text, year_imdb = search_term(imdb)
            if search_text and year_imdb:
                text = search_text[-1]
                link, new_host = scrape_search(host,headers,text,year_imdb)
                if not '/tvshows/' in link:
                    page = opcoes_filmes(link,headers, new_host)
                    stream, headers_  = resolve_stream(page)
    except:
        pass
    return stream, headers_   

