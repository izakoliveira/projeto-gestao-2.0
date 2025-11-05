-- ============================================
-- CRIAR COLUNA is_admin NA TABELA USUARIOS
-- Para gerenciar administradores pelo banco
-- ============================================

-- 1. ADICIONAR coluna is_admin
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- 2. DEFINIR o primeiro administrador (seu usuário)
UPDATE usuarios 
SET is_admin = TRUE 
WHERE email = 'izak.gomes59@gmail.com';

-- Ou por ID (caso o email esteja diferente):
-- UPDATE usuarios 
-- SET is_admin = TRUE 
-- WHERE id = 'd0d784bd-f2bb-44b2-8096-5c10ec4d57be';

-- 3. VERIFICAR administradores
SELECT id, nome, email, is_admin 
FROM usuarios 
WHERE is_admin = TRUE;

-- 4. (OPCIONAL) Criar índice para melhor performance
CREATE INDEX IF NOT EXISTS idx_usuarios_is_admin 
ON usuarios(is_admin) 
WHERE is_admin = TRUE;

-- ============================================
-- COMANDOS ÚTEIS
-- ============================================

-- Tornar alguém admin:
-- UPDATE usuarios SET is_admin = TRUE WHERE email = 'email@exemplo.com';

-- Remover admin:
-- UPDATE usuarios SET is_admin = FALSE WHERE email = 'email@exemplo.com';

-- Listar todos admins:
-- SELECT nome, email FROM usuarios WHERE is_admin = TRUE;
