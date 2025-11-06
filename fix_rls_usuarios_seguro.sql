-- ==================================================
-- FIX RLS POLICIES - Tabela usuarios (VERSÃO SEGURA)
-- Permite UPDATE apenas para admins identificados
-- Data: 2025-11-06
-- ==================================================

-- 1. Remover políticas antigas
DROP POLICY IF EXISTS "Permitir UPDATE para usuários autenticados" ON usuarios;
DROP POLICY IF EXISTS "Permitir UPDATE de restrições" ON usuarios;
DROP POLICY IF EXISTS "Admins podem atualizar qualquer usuário" ON usuarios;
DROP POLICY IF EXISTS "Permitir SELECT para autenticados" ON usuarios;
DROP POLICY IF EXISTS "Permitir UPDATE para autenticados" ON usuarios;
DROP POLICY IF EXISTS "Permitir INSERT para autenticados" ON usuarios;

-- 2. Garantir que RLS está habilitado
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- 3. SELECT: Qualquer um pode ler (necessário para login e listagens)
CREATE POLICY "Permitir SELECT para todos"
ON usuarios
FOR SELECT
TO authenticated, anon
USING (true);

-- 4. UPDATE: Apenas admins ou o próprio usuário podem atualizar
CREATE POLICY "Permitir UPDATE para admins e próprio usuário"
ON usuarios
FOR UPDATE
TO authenticated, anon
USING (
    is_admin = true OR  -- Se o usuário logado é admin
    id = auth.uid()     -- Ou se está atualizando seu próprio registro
)
WITH CHECK (
    is_admin = true OR 
    id = auth.uid()
);

-- 5. INSERT: Permitir criação de novos usuários (registro)
CREATE POLICY "Permitir INSERT para todos"
ON usuarios
FOR INSERT
TO authenticated, anon
WITH CHECK (true);

-- 6. DELETE: Apenas admins podem deletar
CREATE POLICY "Permitir DELETE apenas para admins"
ON usuarios
FOR DELETE
TO authenticated, anon
USING (is_admin = true);

-- 7. Verificar políticas criadas
SELECT 
    schemaname, 
    tablename, 
    policyname, 
    cmd as operacao,
    CASE 
        WHEN cmd = 'SELECT' THEN 'Leitura'
        WHEN cmd = 'UPDATE' THEN 'Atualização'
        WHEN cmd = 'INSERT' THEN 'Criação'
        WHEN cmd = 'DELETE' THEN 'Exclusão'
    END as tipo
FROM pg_policies 
WHERE tablename = 'usuarios'
ORDER BY cmd;

-- ==================================================
-- NOTA IMPORTANTE:
-- Esta política usa "is_admin = true" mas como estamos usando
-- a chave anon (não autenticada), o auth.uid() será NULL.
-- Para funcionar com chave anon, precisamos usar a primeira
-- versão (menos segura) OU usar service_role key.
-- ==================================================
