-- ============================================
-- FIX COMPLETO: Todas as Restrições CASCADE
-- Aplicar em todas as tabelas relacionadas
-- ============================================

-- 1. NOTIFICACOES
ALTER TABLE notificacoes 
DROP CONSTRAINT IF EXISTS notificacoes_usuario_id_fkey;

ALTER TABLE notificacoes 
ADD CONSTRAINT notificacoes_usuario_id_fkey 
FOREIGN KEY (usuario_id) 
REFERENCES usuarios(id) 
ON DELETE CASCADE;

-- 2. PROJETOS (se tiver coluna usuario_id ou criado_por)
ALTER TABLE projetos 
DROP CONSTRAINT IF EXISTS projetos_criado_por_fkey;

ALTER TABLE projetos 
ADD CONSTRAINT projetos_criado_por_fkey 
FOREIGN KEY (criado_por) 
REFERENCES usuarios(id) 
ON DELETE SET NULL;  -- Usa SET NULL para não perder projetos

-- 3. TAREFAS (se tiver coluna responsavel_id)
ALTER TABLE tarefas 
DROP CONSTRAINT IF EXISTS tarefas_responsavel_id_fkey;

ALTER TABLE tarefas 
ADD CONSTRAINT tarefas_responsavel_id_fkey 
FOREIGN KEY (responsavel_id) 
REFERENCES usuarios(id) 
ON DELETE SET NULL;  -- Usa SET NULL para não perder tarefas

-- 4. HISTORICO / LOGS (se existir)
ALTER TABLE historico_atividades 
DROP CONSTRAINT IF EXISTS historico_usuario_id_fkey;

ALTER TABLE historico_atividades 
ADD CONSTRAINT historico_usuario_id_fkey 
FOREIGN KEY (usuario_id) 
REFERENCES usuarios(id) 
ON DELETE CASCADE;  -- Cascade para logs

-- ============================================
-- VERIFICAÇÃO FINAL
-- ============================================

-- Lista todas as foreign keys relacionadas a usuarios
SELECT 
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND ccu.table_name = 'usuarios'
ORDER BY tc.table_name;
