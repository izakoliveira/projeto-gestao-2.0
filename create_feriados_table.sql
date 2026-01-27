-- Criar tabela de feriados
CREATE TABLE IF NOT EXISTS feriados (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) DEFAULT 'nacional', -- nacional, estadual, municipal
    uf VARCHAR(2), -- estado (para feriados estaduais)
    cidade VARCHAR(100), -- cidade (para feriados municipais)
    ano INTEGER NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(data, tipo, uf, cidade)
);

-- Índice para busca rápida por data
CREATE INDEX IF NOT EXISTS idx_feriados_data ON feriados(data);
CREATE INDEX IF NOT EXISTS idx_feriados_ano ON feriados(ano);

-- Políticas RLS (se necessário)
ALTER TABLE feriados ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura para todos os usuários autenticados
CREATE POLICY "feriados_select_policy" ON feriados
    FOR SELECT USING (auth.role() = 'authenticated');

-- Política para permitir inserção apenas para admins (se houver controle)
CREATE POLICY "feriados_insert_policy" ON feriados
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');