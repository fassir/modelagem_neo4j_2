// 1. Criar Restrições e Índices (Execute primeiro)
CREATE CONSTRAINT usuario_id IF NOT EXISTS FOR (u:Usuario) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT musica_id IF NOT EXISTS FOR (m:Musica) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT artista_id IF NOT EXISTS FOR (a:Artista) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT genero_id IF NOT EXISTS FOR (g:Genero) REQUIRE g.id IS UNIQUE;

// 2. Importar Gêneros
LOAD CSV WITH HEADERS FROM 'file:///generos.csv' AS linha
MERGE (g:Genero {id: toInteger(linha.id)})
SET g.nome = linha.nome;

// 3. Importar Artistas
LOAD CSV WITH HEADERS FROM 'file:///artistas.csv' AS linha
MERGE (a:Artista {id: toInteger(linha.id)})
SET a.nome = linha.nome;

// 4. Importar Músicas e conectar a Artista/Gênero
:auto LOAD CSV WITH HEADERS FROM 'file:///musicas.csv' AS linha
CALL {
    WITH linha
    MERGE (m:Musica {id: toInteger(linha.id)})
    SET m.titulo = linha.titulo,
        m.duracao = toInteger(linha.duracao),
        m.ano = toInteger(linha.ano)
    
    WITH m, linha
    MATCH (a:Artista {id: toInteger(linha.artista_id)})
    MERGE (m)-[:INTERPRETADA_POR]->(a)
    
    WITH m, linha
    MATCH (g:Genero {id: toInteger(linha.genero_id)})
    MERGE (m)-[:PERTENCE_A]->(g)
} IN TRANSACTIONS OF 1000 ROWS;

// 5. Importar Usuários
LOAD CSV WITH HEADERS FROM 'file:///usuarios.csv' AS linha
MERGE (u:Usuario {id: toInteger(linha.id)})
SET u.nome = linha.nome,
    u.idade = toInteger(linha.idade);

// 6. Importar Audições (Interações)
:auto LOAD CSV WITH HEADERS FROM 'file:///audicoes.csv' AS linha
CALL {
    WITH linha
    MATCH (u:Usuario {id: toInteger(linha.usuario_id)})
    MATCH (m:Musica {id: toInteger(linha.musica_id)})
    MERGE (u)-[r:OUVIU]->(m)
    SET r.contagem = toInteger(linha.contagem)
} IN TRANSACTIONS OF 5000 ROWS;

// 7. Importar Curtidas (Usuário CURTIU Música)
:auto LOAD CSV WITH HEADERS FROM 'file:///curtidas.csv' AS linha
CALL {
    WITH linha
    MATCH (u:Usuario {id: toInteger(linha.usuario_id)})
    MATCH (m:Musica {id: toInteger(linha.musica_id)})
    MERGE (u)-[:CURTIU]->(m)
} IN TRANSACTIONS OF 5000 ROWS;

// 8. Importar Seguidores (Usuário SEGUE Artista)
:auto LOAD CSV WITH HEADERS FROM 'file:///seguidores.csv' AS linha
CALL {
    WITH linha
    MATCH (u:Usuario {id: toInteger(linha.usuario_id)})
    MATCH (a:Artista {id: toInteger(linha.artista_id)})
    MERGE (u)-[:SEGUE]->(a)
} IN TRANSACTIONS OF 5000 ROWS;
