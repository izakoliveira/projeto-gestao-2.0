-- Migração: Adicionar rastreamento de status de email às notificações
-- Data: 22 de janeiro de 2026
-- Descrição: Adiciona campos para rastrear o envio de emails das notificações

-- Adicionar colunas para rastreamento de email
ALTER TABLE notificacoes
ADD COLUMN IF NOT EXISTS email_enviado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS email_enviado_em TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS email_erro TEXT,
ADD COLUMN IF NOT EXISTS email_tentativas INTEGER DEFAULT 0;

-- Comentários nas colunas
COMMENT ON COLUMN notificacoes.email_enviado IS 'Indica se o email foi enviado com sucesso';
COMMENT ON COLUMN notificacoes.email_enviado_em IS 'Data/hora do envio do email';
COMMENT ON COLUMN notificacoes.email_erro IS 'Mensagem de erro caso o envio falhe';
COMMENT ON COLUMN notificacoes.email_tentativas IS 'Número de tentativas de envio';

-- Índice para performance
CREATE INDEX IF NOT EXISTS idx_notificacoes_email_status ON notificacoes(email_enviado, email_enviado_em);

-- Atualizar notificações existentes (marcar como enviadas se foram criadas antes desta migração)
UPDATE notificacoes
SET email_enviado = TRUE, email_enviado_em = data_criacao
WHERE email_enviado IS NULL;