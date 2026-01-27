-- Teste temporário: desabilitar RLS para verificar se funciona
ALTER TABLE usuarios_admin DISABLE ROW LEVEL SECURITY;

-- Agora teste o script

-- Depois reabilitar
-- ALTER TABLE usuarios_admin ENABLE ROW LEVEL SECURITY;