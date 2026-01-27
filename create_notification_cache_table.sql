-- Migração: Criar tabela para cache de notificações atrasadas
-- Data: 23 de janeiro de 2026
-- Descrição: Tabela para armazenar cache de notificações de tarefas atrasadas,
--            evitando duplicatas quando o servidor é reiniciado

CREATE TABLE IF NOT EXISTS notification_cache (
    id SERIAL PRIMARY KEY,
    task_id UUID NOT NULL UNIQUE,
    notified_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_notification_cache_task_id ON notification_cache(task_id);
CREATE INDEX IF NOT EXISTS idx_notification_cache_notified_at ON notification_cache(notified_at);

-- Comentários
COMMENT ON TABLE notification_cache IS 'Cache de notificações de tarefas atrasadas para evitar duplicatas';
COMMENT ON COLUMN notification_cache.task_id IS 'ID da tarefa que foi notificada';
COMMENT ON COLUMN notification_cache.notified_at IS 'Data/hora da notificação';
COMMENT ON COLUMN notification_cache.created_at IS 'Data/hora da criação do registro';
COMMENT ON COLUMN notification_cache.updated_at IS 'Data/hora da última atualização';

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_notification_cache_updated_at
    BEFORE UPDATE ON notification_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Política RLS (se estiver habilitado)
-- ALTER TABLE notification_cache ENABLE ROW LEVEL SECURITY;

-- Políticas RLS para permitir operações anônimas (já que usamos service key)
CREATE POLICY "Enable all operations for authenticated users" ON notification_cache
    FOR ALL USING (true) WITH CHECK (true);