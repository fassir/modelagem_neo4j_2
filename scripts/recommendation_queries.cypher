// --- Consultas de Recomendação ---

// 1. Filtragem Colaborativa: "Usuários que ouviram isso também ouviram..."
// Entrada: $musicaId (ex: 1)
MATCH (alvo:Musica {id: $musicaId})<-[:OUVIU]-(u:Usuario)-[:OUVIU]->(rec:Musica)
WHERE rec.id <> alvo.id
RETURN rec.titulo, rec.id, count(u) AS ouvintes_comuns
ORDER BY ouvintes_comuns DESC
LIMIT 10;

// 2. Baseado em Conteúdo: Mesmo Artista
MATCH (alvo:Musica {id: $musicaId})-[:INTERPRETADA_POR]->(a:Artista)<-[:INTERPRETADA_POR]-(rec:Musica)
WHERE rec.id <> alvo.id
RETURN rec.titulo, a.nome AS artista
LIMIT 10;

// 3. Baseado em Conteúdo: Mesmo Gênero (Aleatório ou Popular)
MATCH (alvo:Musica {id: $musicaId})-[:PERTENCE_A]->(g:Genero)<-[:PERTENCE_A]-(rec:Musica)
WHERE rec.id <> alvo.id
RETURN rec.titulo, g.nome AS genero
LIMIT 10;

// 4. Recomendação Híbrida Avançada (Pontuação Ponderada)
// Pontuações:
// - Mesmo Artista: 3 pontos
// - Mesmo Gênero: 1 ponto
// - Ouvinte Comum: 1 ponto por ouvinte
// - Curtida Comum: 3 pontos por curtida (Sinal mais forte que ouvir)
// - Usuário Segue Artista: 5 pontos (Impulso se o usuário segue o artista da música candidata)

// Nota: Esta consulta assume recomendação Item-a-Item baseada em similaridade.

MATCH (alvo:Musica {id: $musicaId})
// Encontrar candidatos potenciais (limitar espaço de busca se necessário)
MATCH (candidata:Musica)
WHERE candidata.id <> alvo.id

// Calcular Pontuação de Artista
OPTIONAL MATCH (alvo)-[:INTERPRETADA_POR]->(a:Artista)<-[:INTERPRETADA_POR]-(candidata)
WITH alvo, candidata, CASE WHEN a IS NOT NULL THEN 3 ELSE 0 END AS pontuacao_artista

// Calcular Pontuação de Gênero
OPTIONAL MATCH (alvo)-[:PERTENCE_A]->(g:Genero)<-[:PERTENCE_A]-(candidata)
WITH alvo, candidata, pontuacao_artista, CASE WHEN g IS NOT NULL THEN 1 ELSE 0 END AS pontuacao_genero

// Calcular Pontuação Social (Colaborativa - Audições)
OPTIONAL MATCH (alvo)<-[:OUVIU]-(u:Usuario)-[:OUVIU]->(candidata)
WITH alvo, candidata, pontuacao_artista, pontuacao_genero, count(u) * 1 AS pontuacao_audicao

// Calcular Pontuação Social (Colaborativa - Curtidas)
OPTIONAL MATCH (alvo)<-[:CURTIU]-(u2:Usuario)-[:CURTIU]->(candidata)
WITH alvo, candidata, pontuacao_artista, pontuacao_genero, pontuacao_audicao, count(u2) * 3 AS pontuacao_curtida

WITH candidata, (pontuacao_artista + pontuacao_genero + pontuacao_audicao + pontuacao_curtida) AS pontuacao_total
WHERE pontuacao_total > 0
RETURN candidata.titulo, candidata.id, pontuacao_total
ORDER BY pontuacao_total DESC
LIMIT 10;

// 5. Recomendação Personalizada para um Usuário ($usuarioId)
// Sugerir músicas com base no que seguem e curtem, excluindo o que já ouviram.
MATCH (u:Usuario {id: $usuarioId})
MATCH (candidata:Musica)
WHERE NOT (u)-[:OUVIU]->(candidata)

// Pontuação baseada em artistas seguidos
OPTIONAL MATCH (u)-[:SEGUE]->(a:Artista)<-[:INTERPRETADA_POR]-(candidata)
WITH u, candidata, CASE WHEN a IS NOT NULL THEN 10 ELSE 0 END AS pontuacao_segue

// Pontuação baseada no gênero das músicas que curtiram
OPTIONAL MATCH (u)-[:CURTIU]->(:Musica)-[:PERTENCE_A]->(g:Genero)<-[:PERTENCE_A]-(candidata)
WITH u, candidata, pontuacao_segue, count(g) * 2 AS afinidade_genero

WITH candidata, (pontuacao_segue + afinidade_genero) AS pontuacao_total
WHERE pontuacao_total > 0
RETURN candidata.titulo, pontuacao_total
ORDER BY pontuacao_total DESC
LIMIT 10;
