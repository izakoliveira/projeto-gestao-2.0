-- Script para adicionar o primeiro usuário MASTER na tabela usuarios_admin
-- Execute este script APENAS UMA VEZ no SQL Editor do Supabase

-- Substitua 'd0d784bd-f2bb-44b2-8096-5c10ec4d57be' pelo seu user_id real
-- Você pode encontrar seu user_id na tabela auth.users usando: SELECT id, email FROM auth.users;

INSERT INTO usuarios_admin (usuario_id, nivel_acesso, ativo, observacoes, criado_por)
VALUES (
    'd0d784bd-f2bb-44b2-8096-5c10ec4d57be', -- Substitua pelo seu user_id
    'master',
    TRUE,
    'Primeiro usuário master do sistema - Criado manualmente',
    'd0d784bd-f2bb-44b2-8096-5c10ec4d57be' -- Mesmo user_id como criador
)
ON CONFLICT (usuario_id) DO UPDATE
SET 
    nivel_acesso = 'master',
    ativo = TRUE,
    data_atualizacao = NOW();

-- Verificar se foi inserido com sucesso
SELECT ua.*, u.email 
FROM usuarios_admin ua
JOIN usuarios u ON ua.usuario_id = u.id
WHERE ua.nivel_acesso = 'master';
