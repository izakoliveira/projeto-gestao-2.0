-- Tabela de usuários administradores
-- Esta tabela armazena informações adicionais sobre usuários com privilégios de administrador

CREATE TABLE IF NOT EXISTS usuarios_admin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES usuarios(id) ON DELETE CASCADE,
    nivel_acesso VARCHAR(50) DEFAULT 'admin', -- 'admin', 'super_admin', 'master'
    permissoes_especiais JSONB DEFAULT '{}', -- Permissões específicas em formato JSON
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    criado_por UUID REFERENCES usuarios(id),
    data_atualizacao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ativo BOOLEAN DEFAULT TRUE,
    observacoes TEXT
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_usuarios_admin_usuario_id ON usuarios_admin(usuario_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_admin_nivel_acesso ON usuarios_admin(nivel_acesso);
CREATE INDEX IF NOT EXISTS idx_usuarios_admin_ativo ON usuarios_admin(ativo);

-- RLS (Row Level Security) - Apenas admins podem ver e manipular esta tabela
ALTER TABLE usuarios_admin ENABLE ROW LEVEL SECURITY;

-- Policy: Apenas admins podem visualizar
CREATE POLICY "Apenas admins podem visualizar usuarios_admin"
    ON usuarios_admin
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM usuarios 
            WHERE usuarios.id = auth.uid() 
            AND usuarios.is_admin = TRUE
        )
    );

-- Policy: Apenas super_admins podem inserir
CREATE POLICY "Apenas super_admins podem inserir usuarios_admin"
    ON usuarios_admin
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM usuarios_admin 
            WHERE usuarios_admin.usuario_id = auth.uid() 
            AND usuarios_admin.nivel_acesso IN ('super_admin', 'master')
            AND usuarios_admin.ativo = TRUE
        )
    );

-- Policy: Apenas super_admins podem atualizar
CREATE POLICY "Apenas super_admins podem atualizar usuarios_admin"
    ON usuarios_admin
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM usuarios_admin 
            WHERE usuarios_admin.usuario_id = auth.uid() 
            AND usuarios_admin.nivel_acesso IN ('super_admin', 'master')
            AND usuarios_admin.ativo = TRUE
        )
    );

-- Policy: Apenas master pode deletar
CREATE POLICY "Apenas master pode deletar usuarios_admin"
    ON usuarios_admin
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM usuarios_admin 
            WHERE usuarios_admin.usuario_id = auth.uid() 
            AND usuarios_admin.nivel_acesso = 'master'
            AND usuarios_admin.ativo = TRUE
        )
    );

-- Trigger para atualizar data_atualizacao automaticamente
CREATE OR REPLACE FUNCTION update_usuarios_admin_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER usuarios_admin_update_timestamp
    BEFORE UPDATE ON usuarios_admin
    FOR EACH ROW
    EXECUTE FUNCTION update_usuarios_admin_timestamp();

-- Comentários para documentação
COMMENT ON TABLE usuarios_admin IS 'Tabela que armazena informações adicionais sobre usuários administradores do sistema';
COMMENT ON COLUMN usuarios_admin.nivel_acesso IS 'Nível de acesso do administrador: admin, super_admin ou master';
COMMENT ON COLUMN usuarios_admin.permissoes_especiais IS 'JSON com permissões específicas do administrador';
COMMENT ON COLUMN usuarios_admin.ativo IS 'Indica se o registro de admin está ativo';
