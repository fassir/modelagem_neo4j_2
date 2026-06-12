<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1F9BD4,50:2E75B6,100:16265F&height=200&section=header&text=Sistema%20de%20Recomenda%C3%A7%C3%A3o%20Musical&fontSize=42&fontColor=ffffff&fontAlignY=38&desc=Algoritmo%20H%C3%ADbrido%20Ponderado%20com%20Neo4j%20Graph%20Database&descAlignY=58&descSize=18&animation=fadeIn" />

<br/>

![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Database-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Cypher](https://img.shields.io/badge/Cypher-Query%20Language-4DB33D?style=for-the-badge&logo=neo4j&logoColor=white)

[![iTunes API](https://img.shields.io/badge/iTunes%20API-Dados%20Reais-FC3C44?style=flat-square&logo=apple&logoColor=white)]()
[![Algoritmo](https://img.shields.io/badge/Algoritmo-Híbrido%20Ponderado-blueviolet?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Ativo-brightgreen?style=flat-square)]()
[![Author](https://img.shields.io/badge/Autor-Fabio%20Piassi-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/fabio-piassi)

</div>

---

## 🎵 Sobre o Projeto

**modelagem_neo4j_2** é um sistema completo de **recomendação de músicas** construído sobre um banco de dados de grafos Neo4j. O projeto implementa um **algoritmo híbrido ponderado** que combina filtragem colaborativa e baseada em conteúdo para gerar recomendações personalizadas com alta relevância.

Os dados são reais, coletados da **API pública do iTunes**, garantindo músicas e artistas autênticos no grafo.

> "Grafos são a estrutura natural para recomendações: conexões entre usuários, músicas e artistas revelam padrões impossíveis de ver em tabelas relacionais."

---

## 🗺️ Modelo de Grafo

```
        ┌──────────────────────────────────────────────────────┐
        │                   GRAFO DE MÚSICAS                    │
        └──────────────────────────────────────────────────────┘

         [SEGUE]          [INTERPRETADA_POR]
  Usuario ──────► Artista ◄──────────────── Musica
    │                                          │
    │ [OUVIU(contagem)]                        │ [PERTENCE_A]
    ▼                                          ▼
  Musica                                    Genero
    │
    │ [CURTIU]
    ▼
  Musica

  ┌──────────────────────────────────────────────────────┐
  │  NÓS:          Usuario, Musica, Artista, Genero      │
  │  RELACIONAMENTOS:                                    │
  │    • OUVIU       (Usuario → Musica) — com contagem   │
  │    • CURTIU      (Usuario → Musica)                  │
  │    • SEGUE       (Usuario → Artista)                 │
  │    • INTERPRETADA_POR (Musica → Artista)             │
  │    • PERTENCE_A  (Musica → Genero)                   │
  └──────────────────────────────────────────────────────┘
```

---

## ⚖️ Algoritmo Híbrido Ponderado

O sistema combina múltiplos sinais para calcular um **score de relevância** por música candidata:

<div align="center">

| Sinal | Peso | Descrição |
|:---:|:---:|:---|
| 🎤 Mesmo artista favorito | **+3** | Músicas do artista que o usuário segue |
| 🎼 Mesmo gênero | **+1** | Músicas do gênero preferido |
| 👂 Audição colaborativa | **+1** | Outra pessoa similar também ouviu |
| ❤️ Curtida colaborativa | **+3** | Usuário similar curtiu a música |
| ⭐ Segue o artista | **+5** | Sinal mais forte de preferência |

</div>

```
Score(musica) = Σ pesos dos sinais ativos para o par (usuario, musica)

Exemplo:
  Música X de Artista A (que usuário segue), gênero Pop:
  → +5 (segue artista) + +3 (mesmo artista) + +1 (gênero) = 9 pts
```

---

## 📁 Estrutura do Projeto

```
modelagem_neo4j_2/
├── scripts/
│   ├── generate_real_data.py       # Coleta dados reais da API iTunes
│   ├── import_data.cypher          # Importa CSVs para o Neo4j
│   └── recommendation_queries.cypher  # Queries de recomendação
├── data/
│   ├── artistas.csv                # Artistas reais da API iTunes
│   ├── musicas.csv                 # Músicas com metadados reais
│   ├── usuarios.csv                # Usuários do sistema
│   ├── generos.csv                 # Gêneros musicais
│   ├── audicoes.csv                # Histórico de audições (com contagem)
│   ├── curtidas.csv                # Músicas curtidas por usuário
│   └── seguidores.csv              # Artistas seguidos por usuário
└── README.md
```

---

<div align="center">

## 🛠️ Stack Tecnológico

[![skillicons](https://skillicons.dev/icons?i=python,docker&theme=dark)](https://skillicons.dev)

**+ Neo4j · Cypher · iTunes API**

</div>

---

## 🐍 Coleta de Dados Reais — iTunes API

<details>
<summary>📡 generate_real_data.py — Integração com iTunes</summary>

```python
import requests
import csv

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"

def buscar_musicas_por_genero(genero: str, limit: int = 50) -> list:
    """Busca músicas reais da API pública do iTunes."""
    params = {
        "term": genero,
        "media": "music",
        "entity": "song",
        "limit": limit
    }
    resp = requests.get(ITUNES_SEARCH_URL, params=params)
    resp.raise_for_status()
    return resp.json().get("results", [])

def exportar_artistas(musicas: list, arquivo: str):
    artistas_vistos = set()
    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'nome', 'genero'])
        writer.writeheader()
        for musica in musicas:
            artista_id = musica.get("artistId")
            if artista_id not in artistas_vistos:
                writer.writerow({
                    "id": artista_id,
                    "nome": musica.get("artistName"),
                    "genero": musica.get("primaryGenreName")
                })
                artistas_vistos.add(artista_id)

# Gêneros coletados
GENEROS = ["pop", "rock", "samba", "forró", "mpb", "eletrônico", "jazz"]

for genero in GENEROS:
    musicas = buscar_musicas_por_genero(genero)
    exportar_artistas(musicas, f"data/artistas_{genero}.csv")
    print(f"[OK] {len(musicas)} músicas coletadas para gênero: {genero}")
```

</details>

---

## 🔵 Cypher — Importação e Recomendação

<details>
<summary>📥 import_data.cypher — Carga do Grafo</summary>

```cypher
// Criação de usuários
LOAD CSV WITH HEADERS FROM 'file:///usuarios.csv' AS row
MERGE (u:Usuario {id: toInteger(row.id), nome: row.nome});

// Criação de artistas
LOAD CSV WITH HEADERS FROM 'file:///artistas.csv' AS row
MERGE (a:Artista {id: toInteger(row.id), nome: row.nome});

// Criação de músicas
LOAD CSV WITH HEADERS FROM 'file:///musicas.csv' AS row
MERGE (m:Musica {id: toInteger(row.id), titulo: row.titulo})
  ON CREATE SET m.duracao = toInteger(row.duracao);

// Relacionamento INTERPRETADA_POR
LOAD CSV WITH HEADERS FROM 'file:///musicas.csv' AS row
MATCH (m:Musica {id: toInteger(row.id)})
MATCH (a:Artista {id: toInteger(row.artista_id)})
MERGE (m)-[:INTERPRETADA_POR]->(a);

// Relacionamento OUVIU com contagem
LOAD CSV WITH HEADERS FROM 'file:///audicoes.csv' AS row
MATCH (u:Usuario {id: toInteger(row.usuario_id)})
MATCH (m:Musica {id: toInteger(row.musica_id)})
MERGE (u)-[r:OUVIU]->(m)
  ON CREATE SET r.contagem = toInteger(row.contagem)
  ON MATCH  SET r.contagem = r.contagem + toInteger(row.contagem);
```

</details>

<details>
<summary>🎯 recommendation_queries.cypher — Algoritmo de Recomendação</summary>

```cypher
// QUERY PRINCIPAL: Recomendações híbridas ponderadas para um usuário
MATCH (u:Usuario {id: $usuario_id})

// Músicas já ouvidas (excluir do resultado)
OPTIONAL MATCH (u)-[:OUVIU]->(ouvidas:Musica)
WITH u, collect(ouvidas) AS ja_ouvidas

// Candidatos via artistas seguidos
MATCH (u)-[:SEGUE]->(a:Artista)<-[:INTERPRETADA_POR]-(m:Musica)
WHERE NOT m IN ja_ouvidas
WITH u, m, a, ja_ouvidas,
     5 AS score_segue, 3 AS score_artista  -- pesos base

// Mesmo gênero
OPTIONAL MATCH (u)-[:OUVIU]->(:Musica)-[:PERTENCE_A]->(g:Genero)<-[:PERTENCE_A]-(m)
WITH u, m, score_segue + score_artista + (CASE WHEN g IS NOT NULL THEN 1 ELSE 0 END) AS score_parcial, ja_ouvidas

// Filtragem colaborativa — usuários similares
OPTIONAL MATCH (u)-[:OUVIU]->(comum:Musica)<-[:OUVIU]-(similar:Usuario)-[:CURTIU]->(m)
WHERE similar <> u AND NOT m IN ja_ouvidas
WITH m,
     score_parcial + (CASE WHEN similar IS NOT NULL THEN 3 ELSE 0 END) AS score_total

RETURN DISTINCT m.titulo AS musica, score_total
ORDER BY score_total DESC
LIMIT 10;
```

</details>

---

## ⚙️ Configuração e Execução

### Pré-requisitos

- Python 3.11+
- Neo4j Desktop ou Neo4j Aura (cloud)
- Acesso à internet (API iTunes)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/fassir/modelagem_neo4j_2.git
cd modelagem_neo4j_2

# 2. Instale dependências Python
pip install requests pandas neo4j

# 3. Gere os dados reais via iTunes API
python scripts/generate_real_data.py

# 4. Suba o Neo4j (via Docker)
docker run \
  --name neo4j-musicas \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/senha123 \
  -v $(pwd)/data:/var/lib/neo4j/import \
  neo4j:5-community

# 5. Importe os dados no Neo4j Browser
# Acesse http://localhost:7474
# Execute: :source import_data.cypher

# 6. Execute as queries de recomendação
# scripts/recommendation_queries.cypher
```

---

## 📊 Exemplo de Resultado

```
╔══════════════════════════════════════════════════════╗
║   RECOMENDAÇÕES PARA: Usuario #42 — Ana Silva        ║
╠══════════════════════════════════════════════════════╣
║  #  │ Música                  │ Artista     │ Score  ║
╠═════╪═════════════════════════╪═════════════╪════════╣
║  1  │ Evidências              │ Chitãozinho │  11 pts║
║  2  │ Como Nossos Pais        │ Elis Regina │   9 pts║
║  3  │ País Tropical           │ Jorge Ben   │   8 pts║
║  4  │ Garota de Ipanema       │ Tom Jobim   │   7 pts║
║  5  │ O Leão                  │ Pitty        │   6 pts║
╚═════╧═════════════════════════╧═════════════╧════════╝
```

---

<div align="center">

## 👤 Autor

**Fabio Piassi**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fabio%20Piassi-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/fabio-piassi)
[![GitHub](https://img.shields.io/badge/GitHub-fassir-181717?style=for-the-badge&logo=github)](https://github.com/fassir)

*Engenheiro de Dados | Graph Databases | Machine Learning | Recomendação*

</div>

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:16265F,50:2E75B6,100:1F9BD4&height=120&section=footer" />
