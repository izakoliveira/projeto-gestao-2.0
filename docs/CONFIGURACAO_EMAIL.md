# 📧 Configuração do Sistema de Notificações por Email

## 🚀 Visão Geral

O sistema agora inclui notificações automáticas por email para:
- **Designação de tarefas** - Quando um usuário é designado para uma tarefa
- **Remoção de tarefas** - Quando um usuário é removido de uma tarefa
- **Alteração de status** - Quando o status de uma tarefa é alterado
- **Conclusão de tarefas** - Quando uma tarefa é marcada como concluída

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```bash
# Configurações de Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASS=sua_senha_de_app
FROM_NAME=Sistema de Gestão de Projetos
ADMIN_EMAIL=admin@exemplo.com
```

### 2. Configuração do Gmail

Para usar o Gmail como servidor SMTP:

1. **Ativar autenticação de 2 fatores** na sua conta Google
2. **Gerar uma senha de app**:
   - Vá para [Conta Google](https://myaccount.google.com/)
   - Segurança → Verificação em duas etapas
   - Senhas de app → Gerar senha para "Email"
3. **Usar a senha gerada** no campo `SMTP_PASS`

### 3. Outros Servidores SMTP

#### Outlook/Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### Yahoo
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

#### Servidor Corporativo
```bash
SMTP_SERVER=smtp.empresa.com
SMTP_PORT=587
SMTP_USER=usuario@empresa.com
SMTP_PASS=senha_corporativa
```

## 🔧 Funcionalidades

### Notificações Automáticas

| Evento | Email Enviado Para | Conteúdo |
|--------|-------------------|----------|
| **Tarefa Designada** | Novo responsável | ✅ Nova tarefa designada com detalhes completos |
| **Tarefa Removida** | Usuário removido | ❌ Notificação de remoção da tarefa |
| **Status Alterado** | Responsável da tarefa | 🔄 Mudança de status com detalhes |
| **Tarefa Concluída** | Responsável da tarefa | 🎉 Parabéns pela conclusão |

### Templates de Email

Os emails são enviados em **HTML responsivo** com:
- 🎨 Design moderno e profissional
- 📱 Layout responsivo para mobile
- 🔗 Links diretos para o projeto
- 📊 Informações detalhadas da tarefa
- 🏷️ Badges coloridos por tipo de notificação

## 🧪 Testando o Sistema

### 1. Verificar Configuração

```python
from utils.email_notifications import email_notifier

# Verificar se o email está habilitado
print(f"Email habilitado: {email_notifier.email_enabled}")

# Verificar configurações
print(f"Servidor: {email_notifier.smtp_server}")
print(f"Porta: {email_notifier.smtp_port}")
print(f"Usuário: {email_notifier.smtp_user}")
```

### 2. Teste Manual

```python
from utils.email_notifications import notificar_tarefa_designada

# Teste de envio
tarefa_info = {
    'nome': 'Tarefa de Teste',
    'projeto_nome': 'Projeto Teste',
    'data_inicio': '01/01/2025',
    'data_fim': '31/01/2025',
    'duracao': '30 dias',
    'colecao': 'Teste'
}

sucesso = notificar_tarefa_designada(
    'teste@exemplo.com',
    'Usuário Teste',
    tarefa_info,
    'http://localhost:5000/projetos/123'
)

print(f"Email enviado: {sucesso}")
```

## 🚨 Solução de Problemas

### Erro: "SMTP Authentication failed"

**Causa**: Senha incorreta ou autenticação de 2 fatores não configurada
**Solução**: 
1. Verificar se a senha de app está correta
2. Confirmar que a autenticação de 2 fatores está ativa

### Erro: "Connection refused"

**Causa**: Porta SMTP bloqueada ou servidor incorreto
**Solução**:
1. Verificar se a porta 587 não está bloqueada pelo firewall
2. Confirmar o endereço do servidor SMTP

### Erro: "SSL/TLS required"

**Causa**: Servidor requer conexão segura
**Solução**: Usar porta 465 com SSL ou 587 com STARTTLS

### Emails não sendo enviados

**Verificar**:
1. Logs do sistema para erros
2. Configurações de variáveis de ambiente
3. Conexão com servidor SMTP
4. Permissões de envio da conta

## 📋 Logs e Monitoramento

O sistema registra todas as tentativas de envio:

```python
import logging

# Configurar nível de log
logging.basicConfig(level=logging.INFO)

# Ver logs de email
logger = logging.getLogger('utils.email_notifications')
```

### Exemplos de Logs

```
INFO:utils.email_notifications:Email enviado com sucesso para usuario@exemplo.com
WARNING:utils.email_notifications:Configurações de email não encontradas. Notificações por email desabilitadas.
ERROR:utils.email_notifications:Erro ao enviar email para usuario@exemplo.com: SMTP Authentication failed
```

## 🔒 Segurança

### Boas Práticas

1. **Nunca commitar** senhas no código
2. **Usar variáveis de ambiente** para credenciais
3. **Implementar rate limiting** para evitar spam
4. **Validar endereços de email** antes do envio
5. **Logs sem informações sensíveis**

### Configuração de Produção

```bash
# Produção - usar variáveis de ambiente do servidor
export SMTP_USER=notificacoes@sistema.com
export SMTP_PASS=senha_segura_producao
export SMTP_SERVER=smtp.provedor.com
export SMTP_PORT=587
```

## 📱 Personalização

### Modificar Templates

Os templates estão em `utils/email_notifications.py`:

```python
# Adicionar novo tipo de notificação
'tarefa_atrasada': """
    <h2 style="color: #dc3545;">⚠️ Tarefa Atrasada</h2>
    <p>Olá {usuario_nome}, sua tarefa está atrasada!</p>
    ...
"""
```

### Cores e Estilos

```css
/* Personalizar cores dos badges */
.status-pendente { background: #fff3cd; color: #856404; }
.status-em-progresso { background: #d1ecf1; color: #0c5460; }
.status-concluida { background: #d4edda; color: #155724; }
```

## 🎯 Próximos Passos

1. **Configurar variáveis de ambiente**
2. **Testar com uma conta de email válida**
3. **Personalizar templates conforme necessário**
4. **Implementar filas de email** para produção
5. **Adicionar relatórios de entrega**

---

**📞 Suporte**: Em caso de dúvidas, consulte os logs do sistema ou entre em contato com o administrador.
