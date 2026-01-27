-- Criar função RPC para gerenciar admins sem RLS
-- Execute no Supabase SQL Editor

CREATE OR REPLACE FUNCTION manage_admin(operation text, user_id uuid DEFAULT NULL, admin_level text DEFAULT NULL)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result json;
BEGIN
    -- Desabilitar RLS temporariamente para esta sessão
    ALTER TABLE usuarios_admin DISABLE ROW LEVEL SECURITY;

    IF operation = 'list' THEN
        SELECT json_agg(
            json_build_object(
                'id', ua.id,
                'usuario_id', ua.usuario_id,
                'nivel_acesso', ua.nivel_acesso,
                'ativo', ua.ativo,
                'email', u.email,
                'nome', u.nome
            )
        ) INTO result
        FROM usuarios_admin ua
        LEFT JOIN usuarios u ON ua.usuario_id = u.id
        WHERE ua.ativo = true;

    ELSIF operation = 'add' AND user_id IS NOT NULL AND admin_level IS NOT NULL THEN
        INSERT INTO usuarios_admin (usuario_id, nivel_acesso, ativo, criado_por)
        VALUES (user_id, admin_level, true, user_id)
        ON CONFLICT (usuario_id) DO UPDATE SET
            nivel_acesso = admin_level,
            ativo = true;
        result := json_build_object('success', true, 'message', 'Admin adicionado/atualizado');

    ELSIF operation = 'remove' AND user_id IS NOT NULL THEN
        UPDATE usuarios_admin SET ativo = false WHERE usuario_id = user_id;
        result := json_build_object('success', true, 'message', 'Admin desativado');

    ELSE
        result := json_build_object('success', false, 'message', 'Operação inválida');
    END IF;

    -- Reabilitar RLS
    ALTER TABLE usuarios_admin ENABLE ROW LEVEL SECURITY;

    RETURN result;
END;
$$;