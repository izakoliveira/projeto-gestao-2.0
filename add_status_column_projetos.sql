-- Adiciona coluna status na tabela projetos
ALTER TABLE projetos
ADD COLUMN status VARCHAR(20) DEFAULT 'pendente';

-- Opcional: já atualizar status dos projetos existentes
UPDATE projetos SET status = 'pendente' WHERE status IS NULL;