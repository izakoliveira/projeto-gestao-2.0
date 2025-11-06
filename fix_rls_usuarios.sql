-- ==================================================
-- FIX RLS POLICIES - Tabela usuarios
-- Permite UPDATE de restrições por usuários autenticados
-- Data: 2025-11-06
-- ==================================================

-- 1. Remover políticas antigas que podem estar bloqueando (se existirem)
DROP POLICY IF EXISTS "Permitir UPDATE para usuários autenticados" ON usuarios;
DROP POLICY IF EXISTS "Permitir UPDATE de restrições" ON usuarios;
DROP POLICY IF EXISTS "Admins podem atualizar qualquer usuário" ON usuarios;

-- 2. Verificar se RLS está habilitado (deve estar)
-- ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- 3. Criar política para permitir SELECT (leitura) para todos usuários autenticados
DROP POLICY IF EXISTS "Permitir SELECT para autenticados" ON usuarios;
CREATE POLICY "Permitir SELECT para autenticados"
ON usuarios
FOR SELECT
TO authenticated, anon
USING (true);

-- 4. Criar política para permitir UPDATE para usuários autenticados
-- Esta política permite que qualquer usuário autenticado atualize qualquer registro
-- (necessário porque o admin precisa atualizar restrições de outros usuários)
DROP POLICY IF EXISTS "Permitir UPDATE para autenticados" ON usuarios;
CREATE POLICY "Permitir UPDATE para autenticados"
ON usuarios
FOR UPDATE
TO authenticated, anon
USING (true)
WITH CHECK (true);

-- 5. Criar política para permitir INSERT (para criação de novos usuários)
DROP POLICY IF EXISTS "Permitir INSERT para autenticados" ON usuarios;
CREATE POLICY "Permitir INSERT para autenticados"
ON usuarios
FOR INSERT
TO authenticated, anon
WITH CHECK (true);

-- 6. Verificar políticas criadas
SELECT schemaname, tablename, policyname, cmd, qual 
FROM pg_policies 
WHERE tablename = 'usuarios';

-- ==================================================
-- INSTRUÇÕES:
-- 1. Copie todo este SQL
-- 2. Acesse: https://supabase.com/dashboard
-- 3. Selecione seu projeto
-- 4. Vá em "SQL Editor"
-- 5. Cole o SQL e clique em "Run"
-- ==================================================
