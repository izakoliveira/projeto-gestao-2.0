-- ============================================
-- FIX: Restrição de Chave Estrangeira
-- Tabela: notificacoes
-- Problema: Não permite excluir usuários
-- Solução: Adicionar CASCADE DELETE
-- ============================================

-- 1. REMOVER a restrição antiga
ALTER TABLE notificacoes 
DROP CONSTRAINT IF EXISTS notificacoes_usuario_id_fkey;

-- 2. ADICIONAR a nova restrição com ON DELETE CASCADE
ALTER TABLE notificacoes 
ADD CONSTRAINT notificacoes_usuario_id_fkey 
FOREIGN KEY (usuario_id) 
REFERENCES usuarios(id) 
ON DELETE CASCADE;

-- 3. VERIFICAR se a restrição foi aplicada corretamente
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'notificacoes'
    AND kcu.column_name = 'usuario_id';

-- Resultado esperado:
-- delete_rule = 'CASCADE'
