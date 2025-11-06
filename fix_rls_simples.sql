-- ==================================================
-- FIX RLS POLICIES - SOLUÇÃO SIMPLES
-- Remove todas as restrições RLS da tabela usuarios
-- Para permitir operações com chave anon
-- Data: 2025-11-06
-- ==================================================

-- OPÇÃO 1: DESABILITAR RLS COMPLETAMENTE (MAIS SIMPLES)
-- ⚠️ ATENÇÃO: Menos seguro, mas funciona imediatamente com chave anon
ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;

-- Verificar status do RLS
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_habilitado
FROM pg_tables 
WHERE tablename = 'usuarios';

-- ==================================================
-- RESULTADO ESPERADO:
-- rls_habilitado = false
-- ==================================================

-- ==================================================
-- INSTRUÇÕES DE USO:
-- 
-- 1. Acesse: https://supabase.com/dashboard/project/zvdpuxggltqejplybzet
-- 2. Vá em "SQL Editor" (menu lateral esquerdo)
-- 3. Clique em "+ New query"
-- 4. Cole APENAS as linhas 10-11 deste arquivo:
--    ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;
-- 5. Clique em "Run" (ou pressione Ctrl+Enter)
-- 6. Aguarde mensagem de sucesso
-- 7. Teste novamente salvar restrições no sistema
-- 
-- ALTERNATIVA SEGURA:
-- Se preferir manter segurança, use service_role key
-- ao invés de anon key nas operações de admin.
-- ==================================================
