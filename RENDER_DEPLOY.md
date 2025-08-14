# 🚀 Deploy no Render - Sistema de Gestão de Projetos 2.0

## 📋 Pré-requisitos

1. **Conta no Render**: [render.com](https://render.com)
2. **Repositório no GitHub**: Seu projeto deve estar no GitHub
3. **Variáveis de Ambiente**: Configuradas no Render

## 🔧 Configuração no Render

### 1. Criar Novo Web Service

1. Acesse o [dashboard do Render](https://dashboard.render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Selecione o repositório `projeto-gestao-2.0`

### 2. Configurações do Serviço

```yaml
Name: projeto-gestao-2-0
Environment: Python 3
Region: Frankfurt (EU Central)
Branch: main
Root Directory: ./
Build Command: pip install -r requirements_producao.txt
Start Command: gunicorn --config gunicorn.conf.py app_producao:app
```

### 3. Variáveis de Ambiente

Configure as seguintes variáveis no Render:

```bash
# Obrigatórias
SECRET_KEY=sua_chave_secreta_muito_segura_aqui_123456789
SUPABASE_URL=https://zvdpuxggltqejplybzet.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI

# Opcionais
FLASK_ENV=production
FLASK_APP=app_producao.py
PYTHON_VERSION=3.11.0
```

### 4. Configurações Avançadas

- **Auto-Deploy**: Enabled
- **Health Check Path**: `/health`
- **Health Check Timeout**: 180 seconds

## 🚀 Deploy

### Opção 1: Deploy Automático

1. Após configurar, clique em "Create Web Service"
2. O Render irá automaticamente:
   - Clonar o repositório
   - Instalar dependências
   - Construir a aplicação
   - Iniciar o serviço

### Opção 2: Deploy Manual

Se preferir usar o `render.yaml`:

1. Certifique-se de que o arquivo `render.yaml` está no repositório
2. No Render, selecione "Use render.yaml"
3. O Render usará as configurações do arquivo

## 🔍 Verificação do Deploy

### 1. Health Check

Após o deploy, verifique se a aplicação está funcionando:

```bash
curl https://seu-app.onrender.com/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "healthy",
  "blueprints": ["auth", "projetos", "tarefas", "admin", "pastas", "main", "producao"],
  "timestamp": "2025-08-01T12:00:00Z"
}
```

### 2. Status da Aplicação

```bash
curl https://seu-app.onrender.com/status
```

### 3. Página Principal

```bash
curl https://seu-app.onrender.com/
```

## 🐛 Troubleshooting

### Problema 1: Build Failed

**Sintomas**: Erro durante a instalação de dependências

**Solução**:
1. Verifique se `requirements_producao.txt` existe
2. Certifique-se de que todas as dependências estão listadas
3. Verifique se há conflitos de versão

### Problema 2: Application Crashed

**Sintomas**: Aplicação para de funcionar após iniciar

**Solução**:
1. Verifique os logs no Render
2. Certifique-se de que as variáveis de ambiente estão configuradas
3. Verifique se o `SECRET_KEY` está definido

### Problema 3: Database Connection Error

**Sintomas**: Erro de conexão com Supabase

**Solução**:
1. Verifique se `SUPABASE_URL` e `SUPABASE_KEY` estão corretos
2. Certifique-se de que as credenciais do Supabase são válidas
3. Verifique se o projeto Supabase está ativo

### Problema 4: Health Check Failed

**Sintomas**: Render mostra que o health check falhou

**Solução**:
1. Verifique se a rota `/health` está funcionando
2. Aumente o timeout do health check para 180s
3. Verifique se a aplicação está respondendo na porta correta

## 📊 Monitoramento

### Logs

Acesse os logs no dashboard do Render:
1. Vá para seu serviço
2. Clique em "Logs"
3. Monitore os logs em tempo real

### Métricas

O Render fornece métricas básicas:
- CPU Usage
- Memory Usage
- Request Count
- Response Time

## 🔄 Atualizações

### Deploy de Atualização

1. Faça push para o branch `main` no GitHub
2. O Render detectará automaticamente as mudanças
3. Iniciará um novo deploy automaticamente

### Rollback

1. Vá para "Deploys" no dashboard
2. Selecione um deploy anterior
3. Clique em "Rollback"

## 🛡️ Segurança

### Variáveis Sensíveis

- Nunca commite variáveis sensíveis no código
- Use sempre as variáveis de ambiente do Render
- Rotacione as chaves regularmente

### HTTPS

- O Render fornece HTTPS automaticamente
- Não é necessário configurar certificados SSL

## 📞 Suporte

### Logs Úteis

```bash
# Verificar logs da aplicação
tail -f logs/app.log

# Verificar logs de erro
tail -f logs/error.log

# Verificar logs de acesso
tail -f logs/access.log
```

### Comandos de Debug

```bash
# Testar conexão com Supabase
python -c "from config.database import supabase; print('OK' if supabase else 'ERRO')"

# Testar configurações
python -c "from config.app_config import Config; print('Config OK')"

# Testar blueprints
python -c "from app_producao import app; print('Blueprints:', list(app.blueprints.keys()))"
```

## 🎯 Próximos Passos

1. **Configurar domínio personalizado** (opcional)
2. **Configurar monitoramento avançado** (opcional)
3. **Configurar backup automático** (opcional)
4. **Configurar CI/CD** (opcional)

---

**✅ Deploy concluído com sucesso!**

Seu sistema estará disponível em: `https://seu-app.onrender.com` 