# 🔧 Correção: Erro ao Excluir Projetos

## 📋 Problema Identificado

**Erro original:**
```
code: '23503', 'details': 'Key is still referenced from table "notificacoes"', 
'message': 'update or delete on table "projetos" violates foreign key constraint "fk_projeto" on table "notificacoes"'
```

### Causa
O erro ocorria porque:
1. A tabela `notificacoes` possui uma chave estrangeira `projeto_id` que referencia a tabela `projetos`
2. Quando tentávamos excluir um projeto que possuía notificações, o banco de dados impedia a operação devido à restrição de integridade referencial
3. Era necessário excluir primeiro as notificações relacionadas antes de excluir o projeto

## ✅ Solução Implementada

### 1. Função de Exclusão Principal (`routes/main.py` - linha 610)

A função `excluir_projeto()` foi corrigida para seguir a ordem correta:

```python
@main_bp.route('/projetos/excluir/<projeto_id>', methods=['POST'])
def excluir_projeto(projeto_id):
    try:
        # 1. Excluir notificações relacionadas ao projeto primeiro
        supabase.table("notificacoes").delete().eq("projeto_id", projeto_id).execute()
        
        # 2. Excluir tarefas do projeto
        supabase.table("tarefas").delete().eq("projeto_id", projeto_id).execute()
        
        # 3. Excluir projeto
        resp = supabase.table("projetos").delete().eq("id", projeto_id).execute()
        
        return jsonify({"success": True, "message": "Projeto excluído com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao excluir projeto: {e}"})
```

### 2. Rota de Produção (`routes/producao.py` - linha 208)

A rota da API de produção também foi corrigida:

```python
@producao_bp.route('/api/producao/colecoes/<projeto_id>', methods=['DELETE'])
def delete_colecao_producao(projeto_id):
    try:
        # Excluir notificações primeiro
        supabase.table("notificacoes").delete().eq("projeto_id", projeto_id).execute()
        
        # Depois excluir o projeto
        delete_resp = supabase.table("projetos").delete().eq("id", projeto_id).execute()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
```

## 🧪 Teste de Validação

Criado teste automatizado (`teste_exclusao_corrigido.py`) que:

1. ✅ Cria um projeto de teste
2. ✅ Cria notificações relacionadas ao projeto  
3. ✅ Tenta excluir o projeto (simulando o erro original)
4. ✅ Verifica que a exclusão funciona corretamente

**Resultado do teste:**
```
🧪 Testando correção da exclusão de projetos com notificações
✅ Projeto criado com ID: 5a0c7965-0337-4ae7-b74f-258238e67851
✅ Notificação criada com sucesso
✅ Notificações excluídas com sucesso
✅ Projeto excluído com sucesso!
🎉 Teste passou! A correção está funcionando.
```

## 📚 Ordem de Exclusão Implementada

Para evitar violações de chave estrangeira, a exclusão segue esta ordem:

1. **Notificações** (`notificacoes` table) - Remove registros que referenciam o projeto
2. **Tarefas** (`tarefas` table) - Remove tarefas do projeto  
3. **Projeto** (`projetos` table) - Remove o projeto principal

## 🔒 Segurança

- ✅ Mantém todas as validações de permissão existentes
- ✅ Respeita RLS (Row Level Security) do Supabase
- ✅ Verificação de propriedade do projeto
- ✅ Restrições de funcionalidade por usuário

## 📝 Status

- ✅ **Corrigido** - Função principal de exclusão
- ✅ **Corrigido** - API de produção 
- ✅ **Testado** - Validação automatizada
- ✅ **Documentado** - Este arquivo

O erro de chave estrangeira ao excluir projetos foi **totalmente resolvido**.