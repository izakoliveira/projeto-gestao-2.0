# Correção do Sistema de Notificações - Verificação de Acesso ao Projeto

## Problema Identificado
O sistema estava enviando notificações para usuários designados como responsáveis de tarefas mesmo quando esses usuários não tinham acesso ao projeto correspondente.

## Solução Implementada

### 1. Função de Verificação de Acesso
Foi criada a função `usuario_tem_acesso_projeto()` no arquivo `routes/tarefas.py` que verifica se um usuário tem acesso a um projeto através de:
- Verificação se o usuário é o dono do projeto
- Verificação se o usuário tem permissão de visualização na tabela `projetos_usuarios_visiveis`

```python
def usuario_tem_acesso_projeto(usuario_id, projeto_id):
    """Verifica se um usuário tem acesso a um projeto (é dono ou tem permissão de visualização)"""
    try:
        # Verificar se é o dono do projeto
        projeto_resp = supabase.table("projetos").select("usuario_id").eq("id", str(projeto_id)).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
        
        if projeto and str(projeto.get('usuario_id')) == str(usuario_id):
            return True
        
        # Verificar se tem permissão de visualização
        permissao_resp = supabase.table("projetos_usuarios_visiveis").select("*").eq("projeto_id", str(projeto_id)).eq("usuario_id", str(usuario_id)).execute()
        if permissao_resp.data:
            return True
        
        return False
    except Exception as e:
        print(f"Erro ao verificar acesso do usuário ao projeto: {e}")
        return False
```

### 2. Pontos de Notificação Corrigidos

#### 2.1. Designação de Novo Responsável (Edição de Tarefa)
- **Localização**: `routes/tarefas.py` - função `editar_tarefa()`
- **Mudança**: Adicionada verificação antes de enviar notificação ao novo responsável
- **Comportamento**: Só envia notificação se o usuário tiver acesso ao projeto

#### 2.2. Remoção de Responsável (Edição de Tarefa)
- **Localização**: `routes/tarefas.py` - função `editar_tarefa()`
- **Mudança**: Adicionada verificação antes de enviar notificação ao responsável removido
- **Comportamento**: Só envia notificação se o usuário tinha acesso ao projeto

#### 2.3. Alteração de Status (Edição de Tarefa)
- **Localização**: `routes/tarefas.py` - função `editar_tarefa()`
- **Mudança**: Adicionada verificação antes de enviar notificação de mudança de status
- **Comportamento**: Só envia notificação se o usuário tiver acesso ao projeto

#### 2.4. Atualização de Status (Rota Específica)
- **Localização**: `routes/tarefas.py` - função `atualizar_status_tarefa()`
- **Mudança**: Adicionada verificação antes de enviar notificação de status/conclusão
- **Comportamento**: Só envia notificação se o usuário tiver acesso ao projeto

### 3. Mensagens de Log
Foram adicionadas mensagens informativas quando uma notificação NÃO é enviada por falta de acesso:
```python
print(f"[INFO] Notificação NÃO enviada: usuário {usuario_id} não tem acesso ao projeto {projeto_id}")
```

## Tipos de Notificação Protegidas
✅ Notificação de designação de tarefa (email + sistema)
✅ Notificação de remoção de tarefa (email + sistema)
✅ Notificação de alteração de status (email + sistema)
✅ Notificação de conclusão de tarefa (email + sistema)

## Teste
Foi criado o script `teste_verificacao_acesso_notificacoes.py` para testar a função de verificação de acesso.

## Como Usar o Teste
```bash
python teste_verificacao_acesso_notificacoes.py
```

## Fluxo de Verificação
```
Usuário designado para tarefa
    ↓
Verificar se é dono do projeto?
    ↓ Não
Verificar se tem permissão de visualização?
    ↓ Não
❌ Notificação NÃO enviada
```

## Benefícios
1. **Segurança**: Usuários sem acesso ao projeto não recebem notificações sobre tarefas desse projeto
2. **Privacidade**: Informações do projeto não são vazadas para usuários não autorizados
3. **Organização**: Apenas usuários relevantes recebem notificações
4. **Rastreabilidade**: Logs informam quando notificações são bloqueadas

## Nova Funcionalidade: Notificação ao Liberar Acesso

### Comportamento
Quando um administrador libera o acesso de um usuário a um projeto (adicionando-o em "Usuários autorizados" na página de administração), o sistema agora:

1. **Verifica** se o usuário já está designado como responsável de alguma tarefa naquele projeto
2. **Envia notificações** (email + sistema) para cada tarefa onde o usuário é responsável
3. **Registra** no log quantas notificações foram enviadas

### Exemplo de Fluxo
```
1. Admin designa usuário como responsável de tarefas no projeto X
   → Notificação NÃO enviada (usuário sem acesso)

2. Admin libera acesso do usuário ao projeto X
   → Sistema busca tarefas onde usuário é responsável
   → Envia notificações sobre TODAS as tarefas pendentes
   → Usuário recebe email e notificações no sistema

3. Futuras designações
   → Notificações enviadas normalmente (usuário tem acesso)
```

### Implementação
Função `notificar_tarefas_pendentes_ao_liberar_acesso()` em `routes/admin.py`:
- Busca todas as tarefas do projeto onde o usuário é responsável
- Envia notificação no sistema e por email para cada tarefa
- Registra logs informativos sobre o processo

## Arquivos Modificados
- `routes/tarefas.py` - Adicionada função de verificação e proteção em 4 pontos de notificação
- `routes/admin.py` - Adicionada função para notificar usuários sobre tarefas pendentes ao liberar acesso

## Arquivos Criados
- `teste_verificacao_acesso_notificacoes.py` - Script de teste da correção
- `CORRECAO_NOTIFICACOES_ACESSO_PROJETO.md` - Documentação (este arquivo)

## Data da Correção
23 de dezembro de 2025
