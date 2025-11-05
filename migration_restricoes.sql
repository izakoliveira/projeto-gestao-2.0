-- Migração: Adicionar colunas de restrições na tabela usuarios
-- Execute este script no SQL Editor do Supabase

-- Adicionar colunas de restrições (default false = sem restrição)
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS restr_criar_projeto BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_projeto BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_excluir_projeto BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_criar_tarefa BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_tarefa BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_excluir_tarefa BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_responsavel BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_duracao BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_datas BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_predecessoras BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_nome_tarefa BOOLEAN DEFAULT false;

-- Comentários para documentação
COMMENT ON COLUMN usuarios.restr_criar_projeto IS 'Restringe criação de novos projetos';
COMMENT ON COLUMN usuarios.restr_editar_projeto IS 'Restringe edição de projetos existentes';
COMMENT ON COLUMN usuarios.restr_excluir_projeto IS 'Restringe exclusão de projetos';
COMMENT ON COLUMN usuarios.restr_criar_tarefa IS 'Restringe criação de tarefas';
COMMENT ON COLUMN usuarios.restr_editar_tarefa IS 'Restringe edição de tarefas';
COMMENT ON COLUMN usuarios.restr_excluir_tarefa IS 'Restringe exclusão de tarefas';
COMMENT ON COLUMN usuarios.restr_editar_responsavel IS 'Restringe alteração de responsável da tarefa';
COMMENT ON COLUMN usuarios.restr_editar_duracao IS 'Restringe alteração de duração da tarefa';
COMMENT ON COLUMN usuarios.restr_editar_datas IS 'Restringe alteração de datas da tarefa';
COMMENT ON COLUMN usuarios.restr_editar_predecessoras IS 'Restringe edição de dependências entre tarefas';
COMMENT ON COLUMN usuarios.restr_editar_nome_tarefa IS 'Restringe renomeação de tarefas';
