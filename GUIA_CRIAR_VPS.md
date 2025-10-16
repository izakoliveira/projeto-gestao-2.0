# 🖥️ Como Criar um VPS - Guia Completo

## 🎯 Melhores Opções de VPS

### **1. 🆓 Oracle Cloud (100% GRATUITO para sempre)**

**✅ Vantagens:**
- **4 CPUs ARM** + **24GB RAM** + **200GB SSD** - GRATUITO
- **1 VM x86** + **1GB RAM** + **50GB SSD** - GRATUITO
- Sem limite de tempo (Always Free)
- Tráfego ilimitado
- IP público gratuito

#### **Passos para criar na Oracle:**

1. **Acesse:** https://cloud.oracle.com
2. **Clique em "Start for free"**
3. **Preencha os dados:**
   - Nome, email, telefone
   - País: Brasil
   - **⚠️ Use cartão real** (não cobram nada, só validação)

4. **Verificação:**
   - SMS no telefone
   - Validação do cartão (R$ 4,00 temporário)

5. **Criar Instância:**
   ```
   Compute > Instances > Create Instance
   
   Name: sistema-gestao
   Image: Ubuntu 22.04
   Shape: VM.Standard.A1.Flex (ARM - 4 cores, 24GB)
   Boot volume: 200 GB
   
   Networking:
   ✅ Assign public IP
   
   SSH Keys:
   ✅ Generate SSH key pair (baixe a chave privada!)
   ```

6. **Configurar Firewall:**
   ```
   Networking > Virtual Cloud Networks > subnet > Security Lists
   
   Adicionar regras:
   - Source: 0.0.0.0/0
   - Port: 80 (HTTP)
   - Port: 443 (HTTPS)
   - Port: 22 (SSH)
   ```

### **2. 💰 DigitalOcean ($5/mês)**

**✅ Vantagens:**
- Interface muito amigável
- Documentação excelente
- $200 créditos gratuitos por 60 dias
- Droplets a partir de $4/mês

#### **Passos para criar na DigitalOcean:**

1. **Acesse:** https://digitalocean.com
2. **Clique em "Get Started for Free"**
3. **Use o link de referral para $200 grátis:**
   - https://m.do.co/c/seu-codigo-referral

4. **Criar Droplet:**
   ```
   Create > Droplets
   
   Image: Ubuntu 22.04 LTS
   Size: Basic ($4-6/mês)
   CPU: Regular (1 vCPU, 1GB RAM, 25GB SSD)
   
   Datacenter: New York 1 (mais próximo do Brasil)
   
   Authentication: SSH keys (recomendado)
   ou Password (mais simples)
   
   Hostname: sistema-gestao
   ```

### **3. 🚀 Vultr ($2.50/mês)**

**✅ Vantagens:**
- Mais barato do mercado
- Servidores no Brasil (São Paulo)
- $100 créditos gratuitos

#### **Passos para criar na Vultr:**

1. **Acesse:** https://vultr.com
2. **Cadastre-se** (use cupom para créditos gratuitos)
3. **Deploy Instance:**
   ```
   Cloud Compute > Deploy Now
   
   Server Type: Cloud Compute
   Location: São Paulo, Brazil
   Server Image: Ubuntu 22.04 LTS
   Server Size: $2.50/mês (512MB RAM, 10GB SSD)
   
   SSH Keys: Adicionar chave pública
   Hostname: sistema-gestao
   ```

### **4. 🌟 AWS Free Tier (12 meses gratuitos)**

**✅ Vantagens:**
- 750 horas/mês gratuitas por 12 meses
- t2.micro (1 vCPU, 1GB RAM)
- 30GB EBS gratuitos

#### **Passos para criar na AWS:**

1. **Acesse:** https://aws.amazon.com/free
2. **Crie conta AWS** (precisa cartão para validação)
3. **Launch EC2 Instance:**
   ```
   EC2 Dashboard > Launch Instance
   
   Name: sistema-gestao
   AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
   Instance type: t2.micro (Free tier eligible)
   
   Key pair: Create new (baixe a chave .pem)
   
   Security Group:
   - SSH (port 22) - Your IP
   - HTTP (port 80) - Anywhere
   - HTTPS (port 443) - Anywhere
   ```

## 🔐 Configuração Inicial do VPS

### **1. Conectar via SSH**

#### **Windows (PowerShell):**
```powershell
# Se usar chave SSH
ssh -i "caminho\para\sua-chave.pem" ubuntu@IP_DO_VPS

# Se usar senha
ssh ubuntu@IP_DO_VPS
```

#### **Alternativa: PuTTY (Windows)**
1. Baixe PuTTY: https://putty.org
2. Configure:
   - Host: IP_DO_VPS
   - Port: 22
   - Connection Type: SSH
   - Auth > Private key: sua-chave.ppk

### **2. Atualizar Sistema**

```bash
# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Instalar essenciais
sudo apt install -y curl wget git htop nano ufw
```

### **3. Configurar Firewall**

```bash
# Configurar UFW
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Verificar status
sudo ufw status
```

### **4. Criar Usuário (Opcional)**

```bash
# Criar novo usuário
sudo adduser gestao

# Adicionar ao grupo sudo
sudo usermod -aG sudo gestao

# Configurar SSH para novo usuário
sudo mkdir -p /home/gestao/.ssh
sudo cp ~/.ssh/authorized_keys /home/gestao/.ssh/
sudo chown -R gestao:gestao /home/gestao/.ssh
sudo chmod 700 /home/gestao/.ssh
sudo chmod 600 /home/gestao/.ssh/authorized_keys
```

## 🐳 Deploy com Docker (Recomendado)

### **1. Instalar Docker**

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar para aplicar permissões
sudo reboot
```

### **2. Clonar e Configurar Projeto**

```bash
# Conectar novamente após reboot
ssh ubuntu@IP_DO_VPS

# Clonar projeto
git clone https://github.com/seu-usuario/projeto-gestao-2.0.git
cd projeto-gestao-2.0

# Criar arquivo .env
nano .env
```

**Conteúdo do .env:**
```bash
SECRET_KEY=sua_chave_secreta_muito_segura_123456789
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
FLASK_ENV=production

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASS=sua_senha_de_app
FROM_NAME=Sistema de Gestão
```

### **3. Iniciar Sistema**

```bash
# Construir e iniciar
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Verificar se está funcionando
curl http://localhost/health
```

### **4. Testar Acesso Externo**

```bash
# Do seu computador, teste:
curl http://IP_DO_VPS/health

# Ou abra no navegador:
http://IP_DO_VPS
```

## 🌐 Configurar Domínio (Opcional)

### **1. Registrar Domínio Gratuito**

#### **Freenom (Gratuito):**
1. Acesse: https://freenom.com
2. Pesquise um nome: `meu-sistema.tk`
3. Registre gratuitamente (.tk, .ml, .ga, .cf)

#### **No-IP (Subdomínio Dinâmico):**
1. Acesse: https://noip.com
2. Crie conta gratuita
3. Adicione hostname: `meu-sistema.ddns.net`

### **2. Configurar DNS**

**No painel do domínio:**
```
Tipo: A
Nome: @
Destino: IP_DO_SEU_VPS
TTL: 3600
```

**Para subdomínio:**
```
Tipo: A
Nome: app
Destino: IP_DO_SEU_VPS
TTL: 3600
```

### **3. Configurar HTTPS Gratuito**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Instalar Nginx (se não estiver usando Docker)
sudo apt install nginx

# Obter certificado SSL gratuito
sudo certbot --nginx -d seu-dominio.tk

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🎯 Scripts de Automação

### **Script de Deploy Automático**

```bash
# Criar script deploy.sh
nano deploy.sh
```

```bash
#!/bin/bash
echo "🚀 Iniciando deploy automático..."

# Atualizar código
git pull origin main

# Reconstruir containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verificar saúde
sleep 10
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Deploy realizado com sucesso!"
    echo "🌐 Sistema disponível em: http://$(curl -s ipinfo.io/ip)"
else
    echo "❌ Erro no deploy!"
    docker-compose logs
fi
```

```bash
chmod +x deploy.sh
```

### **Script de Monitoramento**

```bash
# Criar script monitor.sh
nano monitor.sh
```

```bash
#!/bin/bash

# Verificar se o sistema está rodando
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    echo "⚠️  Sistema offline! Reiniciando..."
    docker-compose restart
    
    # Enviar notificação (opcional)
    # curl -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
    #      -d "chat_id=$CHAT_ID&text=Sistema reiniciado automaticamente"
fi

# Log de status
echo "$(date): Sistema verificado" >> /var/log/sistema-monitor.log
```

```bash
chmod +x monitor.sh

# Agendar verificação a cada 5 minutos
crontab -e
# Adicionar: */5 * * * * /home/ubuntu/projeto-gestao-2.0/monitor.sh
```

## 📊 Monitoramento e Manutenção

### **Comandos Úteis**

```bash
# Ver uso de recursos
htop
df -h
free -h

# Ver logs
docker-compose logs -f app
journalctl -f

# Backup do sistema
tar -czf backup-$(date +%Y%m%d).tar.gz projeto-gestao-2.0/

# Limpar Docker (economizar espaço)
docker system prune -a
```

### **Alertas por Email/Telegram**

```bash
# Script de alerta
nano alert.sh
```

```bash
#!/bin/bash

CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
DISK=$(df / | grep -vE '^Filesystem' | awk '{print $5}' | sed 's/%//g')

if [ "$CPU" -gt "80" ] || [ "$DISK" -gt "90" ]; then
    # Enviar email/telegram
    echo "Alto uso de recursos: CPU: ${CPU}%, DISK: ${DISK}%" | \
    mail -s "Alerta VPS" seu-email@gmail.com
fi
```

## 💰 Custos Estimados

| Provedor | Custo Mensal | RAM | CPU | SSD | Tráfego |
|----------|--------------|-----|-----|-----|---------|
| **Oracle** | 🆓 R$ 0 | 24GB | 4 ARM | 200GB | Ilimitado |
| **Vultr** | R$ 15 | 1GB | 1 vCPU | 25GB | 1TB |
| **DigitalOcean** | R$ 30 | 1GB | 1 vCPU | 25GB | 1TB |
| **AWS** | 🆓 12 meses | 1GB | 1 vCPU | 30GB | 15GB |

## 🆘 Troubleshooting

### **Problema: Não consegue conectar via SSH**
```bash
# Verificar se SSH está rodando
sudo systemctl status ssh

# Reiniciar SSH
sudo systemctl restart ssh

# Verificar firewall
sudo ufw status
```

### **Problema: Sistema não inicia**
```bash
# Ver logs detalhados
docker-compose logs app

# Verificar variáveis de ambiente
docker-compose config

# Reiniciar containers
docker-compose restart
```

### **Problema: Falta de espaço**
```bash
# Ver uso de espaço
df -h
du -sh *

# Limpar logs antigos
sudo journalctl --vacuum-time=3d

# Limpar Docker
docker system prune -a
```

---

**🎉 Parabéns! Seu VPS está configurado e rodando!**

**✅ Próximos passos:**
1. Testar todas as funcionalidades
2. Configurar backup automático
3. Monitorar performance
4. Configurar domínio próprio (opcional)