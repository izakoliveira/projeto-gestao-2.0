# 🔀 Túneis e Proxy Reverso - Acesso Temporário

## 🚀 Opções Rápidas para Testes

### **1. Ngrok (Recomendado para testes)**

```bash
# 1. Instalar ngrok
# Baixe de: https://ngrok.com/download

# 2. Registrar conta gratuita em ngrok.com
# 3. Obter authtoken

# 4. Configurar authtoken
ngrok config add-authtoken SEU_AUTHTOKEN

# 5. Iniciar sua aplicação Flask
python app_producao.py

# 6. Em outro terminal, expor a aplicação
ngrok http 5000
```

**Resultado:**
```
ngrok by @inconshreveable

Session Status                online
Account                       seu-email@gmail.com
Update                        available
Version                       3.0.0
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://abc123.ngrok.io -> http://localhost:5000
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

**✅ URL pública:** `https://abc123.ngrok.io`

### **2. Localtunnel (Alternativa gratuita)**

```bash
# Instalar localtunnel
npm install -g localtunnel

# Expor aplicação
lt --port 5000 --subdomain meu-sistema-gestao
```

**Resultado:** `https://meu-sistema-gestao.loca.lt`

### **3. Serveo (SSH Tunnel)**

```bash
# Usando SSH
ssh -R 80:localhost:5000 serveo.net
```

**Resultado:** `https://abc123.serveo.net`

### **4. Cloudflare Tunnel (Gratuito)**

```bash
# 1. Instalar cloudflared
# Windows: Baixe de https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# 2. Login
cloudflared tunnel login

# 3. Criar tunnel
cloudflared tunnel create meu-sistema

# 4. Configurar tunnel
cloudflared tunnel --config tunnel.yml run meu-sistema
```

## ⚖️ Comparação das Opções

| Ferramenta | Gratuito | Domínio Personalizado | HTTPS | Limite |
|------------|----------|----------------------|-------|---------|
| **Ngrok** | ✅ Sim | ❌ Só pago | ✅ Sim | 1 túnel simultâneo |
| **Localtunnel** | ✅ Sim | ✅ Sim | ✅ Sim | Ilimitado |
| **Serveo** | ✅ Sim | ❌ Não | ✅ Sim | Ilimitado |
| **Cloudflare** | ✅ Sim | ✅ Sim | ✅ Sim | Ilimitado |

## 🔧 Script de Inicialização Automática

Crie um script para facilitar o processo:

```bash
# Windows (PowerShell)
# inicio-sistema.ps1

# Iniciar aplicação Flask em background
Start-Process python -ArgumentList "app_producao.py" -WindowStyle Minimized

# Aguardar aplicação iniciar
Start-Sleep 5

# Iniciar ngrok
Start-Process ngrok -ArgumentList "http 5000"

Write-Host "Sistema iniciado! Verifique o terminal do ngrok para obter a URL pública."
```

```bash
# Linux/Mac
# inicio-sistema.sh

#!/bin/bash
echo "🚀 Iniciando Sistema de Gestão de Projetos..."

# Iniciar aplicação Flask em background
python3 app_producao.py &
APP_PID=$!

# Aguardar aplicação iniciar
sleep 5

# Verificar se aplicação está rodando
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Aplicação iniciada com sucesso!"
    
    # Iniciar ngrok
    echo "🌐 Criando túnel público..."
    ngrok http 5000
else
    echo "❌ Erro ao iniciar aplicação!"
    kill $APP_PID
    exit 1
fi
```

## 📱 Configuração para Dispositivos Móveis

### **1. Teste de Responsividade**

Seu sistema já tem templates mobile:
- `templates/detalhes_projeto_mobile.html`
- `templates/novo_projeto_mobile.html` 
- `templates/pastas_mobile.html`
- `templates/projetos_gantt_mobile.html`

### **2. PWA (Progressive Web App)**

Seu sistema já tem configurações PWA:
- `static/manifest.json`
- `static/service-worker.js`

Para instalar no celular:
1. Acesse a URL pelo navegador móvel
2. Clique em "Adicionar à tela inicial"
3. O sistema funcionará como um app nativo

### **3. Otimizações Mobile**

```css
/* Adicionar no static/style.css */

/* Melhor experiência touch */
button, .btn {
    min-height: 44px; /* Padrão Apple para toque */
    padding: 12px 16px;
}

/* Zoom responsivo */
@media (max-width: 768px) {
    .container {
        padding: 0 10px;
    }
    
    .table-responsive {
        overflow-x: auto;
    }
}

/* Melhor legibilidade */
body {
    font-size: 16px; /* Evita zoom automático no iOS */
}

input[type="text"], 
input[type="email"], 
input[type="password"],
textarea {
    font-size: 16px; /* Evita zoom no iOS */
}
```

## 🔒 Segurança para Túneis

### **Autenticação Básica**

```python
# Adicionar no app_producao.py

from functools import wraps
from flask import request, Response

def check_auth(username, password):
    """Verificar credenciais básicas"""
    return username == 'admin' and password == 'senha123'

def authenticate():
    """Enviar resposta 401 com prompt de login"""
    return Response(
        'Login necessário', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Aplicar a todas as rotas (CUIDADO: só para testes!)
@app.before_request
def before_request():
    if request.endpoint and request.endpoint != 'health':
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
```

### **IP Whitelist**

```python
# Restringir acesso a IPs específicos

ALLOWED_IPS = ['127.0.0.1', 'SEU_IP_CASA', 'SEU_IP_TRABALHO']

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)  # Forbidden
```

## 📞 Troubleshooting

### **Problema: Túnel não funciona**
```bash
# Verificar se a aplicação está rodando
curl http://localhost:5000/health

# Verificar portas ocupadas
netstat -tulpn | grep 5000
```

### **Problema: Acesso negado**
```bash
# Verificar firewall (Linux)
sudo ufw status

# Verificar firewall (Windows)
netsh advfirewall show allprofiles
```

### **Problema: Aplicação lenta**
- Use HTTPS sempre que possível
- Túneis gratuitos têm limitações de banda
- Para produção, use deploy em nuvem

---

**⚠️ IMPORTANTE:** Túneis são ideais para **testes e desenvolvimento**. Para uso em produção, prefira deploy em nuvem ou VPS.