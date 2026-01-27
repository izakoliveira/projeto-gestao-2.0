-- Script para adicionar um novo usuário ADMIN na tabela usuarios_admin
-- Execute este script no SQL Editor do Supabase

-- 1. PRIMEIRO: Encontre o user_id do usuário que você quer tornar admin
-- Execute esta query para ver todos os usuários disponíveis:
-- SELECT id, email, nome FROM usuarios ORDER BY email;

-- 2. Substitua os valores abaixo:
INSERT INTO usuarios_admin (usuario_id, nivel_acesso, ativo, observacoes, criado_por)
VALUES (
    'COLE_O_USER_ID_AQUI', -- Substitua pelo user_id do novo admin
    'admin', -- Pode ser: 'admin', 'super_admin' ou 'master'
    TRUE,
    'Usuário adicionado manualmente como administrador',
    'd0d784bd-f2bb-44b2-8096-5c10ec4d57be' -- Seu user_id (quem está criando)
)
ON CONFLICT (usuario_id) DO UPDATE
SET 
    nivel_acesso = EXCLUDED.nivel_acesso,
    ativo = TRUE,
    data_atualizacao = NOW(),
    criado_por = EXCLUDED.criado_por;

-- Verificar todos os admins
SELECT 
    ua.nivel_acesso,
    ua.ativo,
    u.email,
    u.nome,
    ua.data_criacao,
    ua.observacoes
FROM usuarios_admin ua
JOIN usuarios u ON ua.usuario_id = u.id
ORDER BY ua.nivel_acesso DESC, u.email;
