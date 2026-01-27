# 📧 Guia de Configuração de Email - Sistema de Gestão de Projetos

## ⚠️ Problema Identificado
Você está vendo o aviso: "Configurações de email não encontradas. Notificações por email desabilitadas."

Isso significa que o sistema não consegue enviar notificações por email porque as credenciais não estão configuradas.

## ✅ Solução Rápida

### Passo 1: Edite o arquivo `.env`
O arquivo `.env` foi criado na raiz do projeto. Abra-o com um editor de texto e configure as seguintes variáveis:

```bash
# Credenciais do email remetente
SMTP_USER=seu_email@gmail.com
SMTP_PASS=sua_senha_de_app
```

### 2. **Configure seu Zimbra**

#### 🔵 **ZIMBRA (Email Corporativo)**
1. **Descubra as configurações** com seu administrador de TI ou no webmail do Zimbra
2. **Configure no `.env`**:
   ```bash
   SMTP_SERVER=mail.suaempresa.com.br
   SMTP_PORT=587
   SMTP_USER=seu_email@suaempresa.com.br
   SMTP_PASS=sua_senha_zimbra
   ```

**Exemplos de servidores Zimbra:**
- `mail.empresa.com.br`
- `smtp.empresa.com.br`
- `zimbra.empresa.com.br`

**Portas comuns:**
- `587` (TLS - mais comum)
- `465` (SSL)
- `25` (SMTP puro - menos seguro)

#### 🔴 **GMAIL (se preferir)**
1. **Acesse**: https://myaccount.google.com/security
2. **Ative**: "Verificação em duas etapas" (se não estiver ativa)
3. **Vá para**: "Senhas de app"
4. **Selecione**: "Sistema de Gestão de Projetos" ou crie um novo
5. **Copie a senha** gerada (16 caracteres, sem espaços)
6. **Configure no `.env`**:
   ```bash
   SMTP_USER=seu_email@gmail.com
   SMTP_PASS=abcd-efgh-ijkl-mnop  # A senha de app gerada
   ```

#### 🟡 **OUTLOOK/HOTMAIL**
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu_email@outlook.com
SMTP_PASS=sua_senha_normal
```

### Passo 3: Reinicie o sistema
Após configurar, reinicie o sistema para carregar as novas configurações.

### Passo 4: Verifique se funcionou
No log de inicialização, você deve ver:
```
✅ Sistema de email configurado e habilitado!
Servidor: smtp.gmail.com:587
Usuário: seu_email@gmail.com
```

## 📧 Notificações por Email Disponíveis

### 1. **Nova Tarefa Designada** 🔔
- **Quando**: Quando uma tarefa é atribuída a um usuário
- **Conteúdo**: Nome da tarefa, projeto, datas, duração, coleção

### 2. **Tarefa Removida** ❌
- **Quando**: Quando um usuário é removido de uma tarefa
- **Conteúdo**: Nome da tarefa e projeto

### 3. **Status da Tarefa Alterado** 🔄
- **Quando**: Quando o status de uma tarefa muda
- **Conteúdo**: Nome da tarefa, projeto, status novo e anterior

### 4. **Tarefa Concluída** 🎉
- **Quando**: Quando uma tarefa é marcada como concluída
- **Conteúdo**: Nome da tarefa e projeto

### 5. **Acesso Liberado - Tarefas Pendentes** 🎯
- **Quando**: Quando um projeto é liberado para um usuário que já tem tarefas atribuídas
- **Conteúdo**: Lista completa de **todas as tarefas** do usuário no projeto em um único email
- **Vantagem**: Evita múltiplos emails, agrupando todas as notificações em uma
- **Inclui**: Todas as tarefas atribuídas ao usuário, independente do status

## 🔧 Configurações Avançadas

### Variáveis de ambiente completas:
```bash
# Servidor SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Credenciais
SMTP_USER=seu_email@gmail.com
SMTP_PASS=sua_senha_de_app

# Nome do remetente
FROM_NAME=Sistema de Gestão de Projetos
```

### Outros provedores suportados:
- **ProtonMail**: `smtp.protonmail.ch:587`
- **Zoho Mail**: `smtp.zoho.com:587`
- **Mailgun**: `smtp.mailgun.org:587`

## 🔧 **Configurações Específicas para Zimbra**

### Servidores comuns:
- `mail.empresa.com.br`
- `smtp.empresa.com.br`
- `zimbra.empresa.com.br`
- `webmail.empresa.com.br`

### Portas Zimbra:
- **587**: TLS (mais comum)
- **465**: SSL
- **25**: SMTP puro (pode ser bloqueado)

### Exemplo de configuração completa:
```bash
SMTP_SERVER=mail.suaempresa.com.br
SMTP_PORT=587
SMTP_USER=joao.silva@empresa.com.br
SMTP_PASS=minha_senha_zimbra
FROM_NAME=Sistema de Gestão de Projetos
```

### Dicas para Zimbra corporativo:
- **Pergunte ao TI**: As configurações exatas variam por empresa
- **Teste primeiro**: Use um cliente de email (Outlook/Thunderbird) para testar
- **Firewall**: Verifique se a porta não está bloqueada na rede corporativa

## ⚡ Otimizações de Performance

### Processamento Assíncrono
As notificações por email são processadas **em background** para não bloquear a interface do usuário:

- ✅ **Resposta imediata**: A API responde instantaneamente após salvar a tarefa
- ✅ **Processamento paralelo**: Emails são enviados em threads separadas
- ✅ **Sem travamentos**: Mudanças de responsável/status são instantâneas
- ✅ **Confiabilidade**: Mesmo se o email falhar, a operação principal é bem-sucedida

### Quando as Notificações São Enviadas

1. **Alteração de responsável**: Novo usuário recebe email de designação
2. **Remoção de responsável**: Usuário anterior recebe email de remoção  
3. **Mudança de status**: Responsável recebe email sobre alteração
4. **Conclusão de tarefa**: Responsável recebe email de parabéns
5. **Liberação de projeto**: Usuário recebe email com todas as tarefas pendentes

### Benefícios da Otimização

- 🚀 **Performance**: Operações são 3-5x mais rápidas
- 👥 **UX**: Usuários não esperam pelo envio de emails
- 🔄 **Confiabilidade**: Sistema continua funcionando mesmo com problemas de email
- 📊 **Escalabilidade**: Suporta mais usuários simultâneos

## 🔧 Configurações Técnicas Corretas

### Portas SMTP e Seus Usos

**Porta 465 (SSL Direto)**:
- ✅ Recomendado para Zimbra e servidores corporativos
- 🔒 Conexão criptografada desde o início
- 🚫 Não usa STARTTLS
- 📧 Exemplo: `webmail.dipaula.com.br:465`

**Porta 587 (STARTTLS)**:
- ✅ Padrão para Gmail e Outlook
- 🔄 Inicia em texto plano, depois criptografa
- 📧 Exemplo: `smtp.gmail.com:587`

**Porta 25 (SMTP Puro)**:
- ⚠️ Não recomendado (não criptografado)
- 🚫 Geralmente bloqueado por provedores
- 🔓 Inseguro para uso em produção

### Ainda não funciona?
- Verifique se o arquivo `.env` está na raiz do projeto
- Certifique-se de que não há espaços extras nas variáveis
- Reinicie completamente o sistema (feche e reabra)

## 📞 Suporte

Se ainda tiver problemas:
1. Verifique o log de erros no console
2. Abra uma issue no GitHub com o erro específico
3. Inclua qual provedor de email está usando

---
**Arquivo criado automaticamente em**: Janeiro 2026