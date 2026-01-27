-- Correção RLS para tabela notification_cache
-- Data: 23 de janeiro de 2026
-- Descrição: Adiciona política RLS para permitir operações na tabela notification_cache

-- Verificar se a política já existe e criar se necessário
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'notification_cache'
        AND policyname = 'Enable all operations for authenticated users'
    ) THEN
        CREATE POLICY "Enable all operations for authenticated users" ON notification_cache
            FOR ALL USING (true) WITH CHECK (true);
    END IF;
END
$$;