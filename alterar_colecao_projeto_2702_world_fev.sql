-- SQL para alterar a coleção de todas as tarefas do projeto "2702 - WORLD FEV"
-- Execute este script no SQL Editor do Supabase

-- Primeiro, vamos verificar o projeto e suas tarefas
-- SELECT id, nome FROM projetos WHERE nome = '2702 - WORLD FEV';

-- Verificar tarefas atuais do projeto
-- SELECT t.id, t.nome, t.colecao
-- FROM tarefas t
-- JOIN projetos p ON t.projeto_id = p.id
-- WHERE p.nome = '2702 - WORLD FEV';

-- Agora, atualizar todas as tarefas do projeto para ter a coleção "2702 - WORLD FEV"
UPDATE tarefas
SET colecao = '2702 - WORLD FEV'
WHERE projeto_id = (
    SELECT id
    FROM projetos
    WHERE nome = '2702 - WORLD FEV'
);

-- Verificar quantas tarefas foram atualizadas
-- SELECT COUNT(*) as tarefas_atualizadas
-- FROM tarefas
-- WHERE projeto_id = (SELECT id FROM projetos WHERE nome = '2702 - WORLD FEV')
-- AND colecao = '2702 - WORLD FEV';