# 🚀 **Guia de Deploy - Sistema de Gestão de Projetos**

## 📧 **Configuração de Email para Produção**

### **⚠️ IMPORTANTE: Variáveis de Ambiente**

O sistema de notificações por email **NÃO funcionará** sem as seguintes variáveis de ambiente configuradas no Render:

### **🔧 Configuração no Render:**

1. **Acesse o painel do Render**
2. **Vá em Environment Variables**
3. **Adicione as seguintes variáveis:**

```bash
# Configurações SMTP (OBRIGATÓRIAS)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASS=sua-senha-de-app
FROM_NAME=Sistema de Gestão

# Configurações do Supabase (OBRIGATÓRIAS)
SUPABASE_URL=sua-url-do-supabase
SUPABASE_KEY=sua-chave-do-supabase

# Configuração de Admin (OPCIONAL)
ADMIN_EMAIL=admin@exemplo.com
```

### **📧 Configuração do Gmail:**

1. **Ative a verificação em 2 etapas** na sua conta Google
2. **Gere uma senha de app:**
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "Email" e "Outro (nome personalizado)"
   - Use essa senha no campo `SMTP_PASS`

### **🔍 Verificação:**

Após configurar, o sistema mostrará no log:
```
Sistema de email configurado e habilitado!
Servidor: smtp.gmail.com:587
Usuário: seu-email@gmail.com
De: Sistema de Gestão
```

### **❌ Se não configurar:**

O sistema funcionará normalmente, mas **NÃO enviará emails**. Você verá:
```
Configurações de email não encontradas. Notificações por email desabilitadas.
```

## 🚀 **Deploy no Render:**

1. **Conecte seu repositório GitHub**
2. **Configure as variáveis de ambiente** (acima)
3. **Deploy automático** a cada push para `main`

## 📋 **Checklist de Deploy:**

- [ ] Variáveis de ambiente configuradas no Render
- [ ] Gmail com verificação em 2 etapas ativada
- [ ] Senha de app gerada e configurada
- [ ] Deploy realizado com sucesso
- [ ] Logs mostram "Sistema de email configurado e habilitado!"

## 🆘 **Problemas Comuns:**

### **"SMTP Authentication failed"**
- Verifique se a verificação em 2 etapas está ativada
- Use senha de app, não sua senha normal

### **"Connection refused"**
- Verifique `SMTP_SERVER` e `SMTP_PORT`
- Gmail: `smtp.gmail.com:587`

### **"Not enough authentication scopes"**
- Gere uma nova senha de app
- Verifique se selecionou "Email" como aplicativo 