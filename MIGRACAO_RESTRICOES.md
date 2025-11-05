# Migração de Restrições para Banco de Dados

## 📋 Objetivo
Migrar o sistema de restrições de funcionalidades do arquivo local `restricoes.json` para o banco de dados Supabase, garantindo sincronização entre todas as instalações.

## 🔧 Passos para Execução

### 1. Executar Script SQL no Supabase

1. Acesse o painel do Supabase: https://app.supabase.com
2. Selecione seu projeto
3. Vá em **SQL Editor**
4. Copie e execute o conteúdo de `migration_restricoes.sql`

```sql
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS restr_criar_projeto BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS restr_editar_projeto BOOLEAN DEFAULT false,
-- ... (todas as colunas)
```

### 2. Executar Script de Migração de Dados

No terminal, na pasta do projeto:

```bash
python migrar_restricoes_para_banco.py
```

Este script irá:
- Ler o arquivo `restricoes.json`
- Atualizar cada usuário no banco com suas restrições
- Exibir relatório de sucesso/erros

### 3. Verificar Migração

Acesse o Supabase:
1. Vá em **Table Editor**
2. Selecione a tabela `usuarios`
3. Verifique se as novas colunas `restr_*` foram criadas
4. Confirme se os valores foram migrados corretamente

### 4. Recompilar Instalador

```bash
pyinstaller --clean Instalador_Sistema_Gestao.spec
```

## ✅ Benefícios da Migração

| Antes | Depois |
|-------|--------|
| Arquivo local `restricoes.json` | Banco de dados centralizado |
| Cada instalação tem restrições diferentes | Todas instalações sincronizadas |
| Difícil gerenciar múltiplos usuários | Gerenciamento centralizado |
| Sem backup automático | Backup automático no Supabase |

## 🔄 Como Funciona Agora

### Carregar Restrições
```python
restricoes = carregar_restricoes()
# Busca do banco → fallback para JSON se banco indisponível
```

### Salvar Restrições
```python
salvar_restricoes(restricoes)
# Salva no banco → backup em JSON local
```

## 📝 Campos de Restrição

Todos os campos são booleanos (true = restrito, false = liberado):

- `restr_criar_projeto` - Criar novos projetos
- `restr_editar_projeto` - Editar projetos existentes
- `restr_excluir_projeto` - Deletar projetos
- `restr_criar_tarefa` - Criar tarefas
- `restr_editar_tarefa` - Editar tarefas
- `restr_excluir_tarefa` - Deletar tarefas
- `restr_editar_responsavel` - Alterar responsável da tarefa
- `restr_editar_duracao` - Alterar duração da tarefa
- `restr_editar_datas` - Alterar datas da tarefa
- `restr_editar_predecessoras` - Editar dependências entre tarefas
- `restr_editar_nome_tarefa` - Renomear tarefas

## 🚨 Importante

- O arquivo `restricoes.json` agora é usado apenas como **backup/cache**
- A fonte de verdade é o **banco de dados**
- Se o banco estiver indisponível, usa o JSON local temporariamente
- Sempre que salvar restrições, atualiza banco E arquivo JSON

## 🐛 Troubleshooting

### Erro ao conectar com banco
```
Erro ao carregar restrições do banco: ...
```
**Solução**: Sistema automaticamente usa `restricoes.json` como fallback

### Usuário não encontrado na migração
```
✗ Usuário não encontrado no banco: xxx-xxx-xxx
```
**Solução**: Usuário foi deletado do banco mas existe no JSON - pode ignorar

### Campos não aparecem no banco
**Solução**: Execute novamente o script SQL `migration_restricoes.sql`
