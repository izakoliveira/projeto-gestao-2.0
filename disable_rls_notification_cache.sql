-- Desabilitar RLS para notification_cache (abordagem mais simples)
-- Data: 23 de janeiro de 2026
-- Descrição: Desabilita RLS para a tabela notification_cache para operações diretas

ALTER TABLE notification_cache DISABLE ROW LEVEL SECURITY;