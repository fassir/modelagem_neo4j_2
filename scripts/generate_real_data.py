import csv
import random
import os
import json
import time
import urllib.request
import urllib.parse
import sys

# Configuração
NUM_USUARIOS = 2000
NUM_AUDICOES = 200000
NUM_CURTIDAS = 50000
NUM_SEGUIDORES = 10000
TARGET_MUSICAS = 50000  # Meta de músicas

# Garante que o caminho seja relativo à localização deste script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_DADOS = os.path.join(BASE_DIR, '..', 'data')
os.makedirs(DIRETORIO_DADOS, exist_ok=True)

# Gêneros para busca (termos em inglês funcionam melhor na API, mas mapearemos para PT)
# Tupla: (Termo de Busca, Nome Exibição)
GENEROS_BUSCA = [
    ('Rock', 'Rock'), ('Pop', 'Pop'), ('Jazz', 'Jazz'), ('Classical', 'Clássica'),
    ('Hip Hop', 'Hip Hop'), ('Electronic', 'Eletrônica'), ('Blues', 'Blues'),
    ('Country', 'Country'), ('Reggae', 'Reggae'), ('Folk', 'Folk'),
    ('R&B', 'R&B'), ('Soul', 'Soul'), ('Punk', 'Punk'), ('Metal', 'Metal'),
    ('Disco', 'Disco'), ('Funk', 'Funk'), ('Gospel', 'Gospel'),
    ('Latin', 'Latina'), ('Ska', 'Ska'), ('Indie', 'Indie'),
    ('Alternative', 'Alternativo'), ('Dance', 'Dance'), ('K-Pop', 'K-Pop'),
    ('Soundtrack', 'Trilha Sonora'), ('Brazilian', 'Brasileira')
]

# Estruturas de dados para armazenamento em memória
generos_map = {} # nome -> id
artistas_map = {} # nome -> id (ou itunes_artist_id -> id)
musicas_list = [] # Lista de dicts
musicas_ids_seen = set() # Para evitar duplicatas de trackId do iTunes

# 1. Preparar Gêneros
print("Preparando gêneros...")
dados_generos = []
for i, (termo, nome_exibicao) in enumerate(GENEROS_BUSCA):
    id_genero = i + 1
    generos_map[termo] = id_genero # Mapeia o termo de busca ao ID
    dados_generos.append({'id': id_genero, 'nome': nome_exibicao})

# Função para buscar no iTunes
def buscar_itunes(termo, entidade='song', limite=200, offset=0):
    base_url = "https://itunes.apple.com/search"
    params = {
        'term': termo,
        'entity': entidade,
        'limit': limite,
        'offset': offset
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Erro ao buscar '{termo}': {e}")
        return None
    return None

# 2. Coletar Músicas e Artistas Reais
print(f"Iniciando coleta de dados reais (Meta: {TARGET_MUSICAS} músicas)...")
print("Isso pode levar alguns minutos. Por favor, aguarde.")

contador_musicas = 0
contador_artistas = 0

# Estratégia: Buscar por Gênero + Ano para obter mais resultados
anos = range(2023, 1980, -1) # De 2023 até 1980

for termo_genero, nome_exibicao in GENEROS_BUSCA:
    if contador_musicas >= TARGET_MUSICAS:
        break
    
    print(f"Buscando músicas de: {nome_exibicao} ({termo_genero})...")
    
    # Tenta buscar por ano para aprofundar
    for ano in anos:
        if contador_musicas >= TARGET_MUSICAS:
            break
            
        termo_busca = f"{termo_genero} {ano}"
        resultado = buscar_itunes(termo_busca)
        
        if resultado and 'results' in resultado:
            items = resultado['results']
            if not items:
                continue
                
            for item in items:
                # Validar se é música
                if item.get('kind') != 'song':
                    continue
                
                itunes_track_id = item.get('trackId')
                if itunes_track_id in musicas_ids_seen:
                    continue
                
                musicas_ids_seen.add(itunes_track_id)
                
                # Processar Artista
                nome_artista = item.get('artistName', 'Desconhecido')
                if nome_artista not in artistas_map:
                    contador_artistas += 1
                    artistas_map[nome_artista] = contador_artistas
                
                id_artista = artistas_map[nome_artista]
                id_genero = generos_map[termo_genero]
                
                # Processar Música
                contador_musicas += 1
                musica = {
                    'id': contador_musicas,
                    'titulo': item.get('trackName', 'Sem Título'),
                    'duracao': int(item.get('trackTimeMillis', 0) / 1000), # ms para s
                    'ano': int(item.get('releaseDate', f'{ano}-01-01')[:4]),
                    'artista_id': id_artista,
                    'genero_id': id_genero
                }
                musicas_list.append(musica)
        
        # Pequeno delay para não bloquear a API
        time.sleep(0.2)
        sys.stdout.write(f"\rMúsicas coletadas: {contador_musicas}/{TARGET_MUSICAS}")
        sys.stdout.flush()

    print(f"\nConcluído gênero {nome_exibicao}.")

print(f"\nColeta finalizada!")
print(f"Total Músicas: {len(musicas_list)}")
print(f"Total Artistas: {len(artistas_map)}")

# 3. Salvar Arquivos CSV

# Gêneros
print("Salvando generos.csv...")
with open(os.path.join(DIRETORIO_DADOS, 'generos.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['id', 'nome'])
    escritor.writeheader()
    escritor.writerows(dados_generos)

# Artistas
print("Salvando artistas.csv...")
dados_artistas = [{'id': id_a, 'nome': nome} for nome, id_a in artistas_map.items()]
with open(os.path.join(DIRETORIO_DADOS, 'artistas.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['id', 'nome'])
    escritor.writeheader()
    escritor.writerows(dados_artistas)

# Músicas
print("Salvando musicas.csv...")
with open(os.path.join(DIRETORIO_DADOS, 'musicas.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['id', 'titulo', 'duracao', 'ano', 'artista_id', 'genero_id'])
    escritor.writeheader()
    escritor.writerows(musicas_list)

# Músicas IDs (Helper)
print("Salvando musicas_ids.csv...")
with open(os.path.join(DIRETORIO_DADOS, 'musicas_ids.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['id', 'titulo'])
    escritor.writeheader()
    dados_ids = [{'id': m['id'], 'titulo': m['titulo']} for m in musicas_list]
    escritor.writerows(dados_ids)

# 4. Gerar Dados Sintéticos (Usuários e Interações)
# Como não temos usuários reais, geramos sintéticos e conectamos às músicas reais

print(f"Gerando {NUM_USUARIOS} usuários sintéticos...")
dados_usuarios = []
for i in range(NUM_USUARIOS):
    dados_usuarios.append({
        'id': i + 1,
        'nome': f"Usuario_{i+1}",
        'idade': random.randint(18, 70)
    })

with open(os.path.join(DIRETORIO_DADOS, 'usuarios.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['id', 'nome', 'idade'])
    escritor.writeheader()
    escritor.writerows(dados_usuarios)

# Interações: OUVIU
print(f"Gerando {NUM_AUDICOES} audições...")
dados_audicoes = []
ids_musicas_disponiveis = [m['id'] for m in musicas_list]
ids_artistas_disponiveis = [a['id'] for a in dados_artistas]

if not ids_musicas_disponiveis:
    print("ERRO: Nenhuma música coletada. Verifique sua conexão com a internet.")
    sys.exit(1)

for _ in range(NUM_AUDICOES):
    dados_audicoes.append({
        'usuario_id': random.randint(1, NUM_USUARIOS),
        'musica_id': random.choice(ids_musicas_disponiveis),
        'contagem': random.randint(1, 100)
    })

with open(os.path.join(DIRETORIO_DADOS, 'audicoes.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['usuario_id', 'musica_id', 'contagem'])
    escritor.writeheader()
    escritor.writerows(dados_audicoes)

# Interações: CURTIU
print(f"Gerando {NUM_CURTIDAS} curtidas...")
dados_curtidas = []
for _ in range(NUM_CURTIDAS):
    dados_curtidas.append({
        'usuario_id': random.randint(1, NUM_USUARIOS),
        'musica_id': random.choice(ids_musicas_disponiveis)
    })

with open(os.path.join(DIRETORIO_DADOS, 'curtidas.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['usuario_id', 'musica_id'])
    escritor.writeheader()
    escritor.writerows(dados_curtidas)

# Interações: SEGUE
print(f"Gerando {NUM_SEGUIDORES} seguidores...")
dados_seguidores = []
for _ in range(NUM_SEGUIDORES):
    dados_seguidores.append({
        'usuario_id': random.randint(1, NUM_USUARIOS),
        'artista_id': random.choice(ids_artistas_disponiveis)
    })

with open(os.path.join(DIRETORIO_DADOS, 'seguidores.csv'), 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=['usuario_id', 'artista_id'])
    escritor.writeheader()
    escritor.writerows(dados_seguidores)

print("Geração de dados reais concluída com sucesso!")
