# 🖥️ Deploy em VPS - Sistema de Gestão de Projetos 2.0

## 🎯 Opções de VPS Recomendadas

### **Gratuitas/Baratas:**
- **Oracle Cloud Free Tier** (4 ARM cores, 24GB RAM - GRATUITO para sempre)
- **Google Cloud Platform** ($300 créditos gratuitos)
- **AWS Free Tier** (12 meses gratuitos)
- **DigitalOcean** (a partir de $5/mês)
- **Vultr** (a partir de $2.50/mês)

## 🚀 Deploy com Docker (Recomendado)

### 1. Preparar o Servidor

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clonar o Projeto

```bash
git clone https://github.com/seu-usuario/projeto-gestao-2.0.git
cd projeto-gestao-2.0
```

### 3. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
nano .env
```

```bash
# Conteúdo do .env
SECRET_KEY=sua_chave_secreta_muito_segura_123456789
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
FLASK_ENV=production
```

### 4. Iniciar com Docker Compose

```bash
# Construir e iniciar os containers
docker-compose up -d

# Verificar se está funcionando
curl http://localhost/health
```

### 5. Configurar HTTPS (Opcional)

Para HTTPS gratuito com Let's Encrypt:

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🌐 Configuração de Domínio

### 1. Registrar um Domínio (Opcional)

**Opções gratuitas:**
- **Freenom** (.tk, .ml, .ga, .cf)
- **No-IP** (subdomínio dinâmico)

**Opções pagas:**
- **Namecheap** (~$8-12/ano)
- **GoDaddy** (~$10-15/ano)
- **Cloudflare** (~$8-10/ano)

### 2. Configurar DNS

Aponte o domínio para o IP do seu VPS:

```
Tipo: A
Nome: @
Valor: IP_DO_SEU_VPS
TTL: 3600
```

Para subdomínio:
```
Tipo: A
Nome: app
Valor: IP_DO_SEU_VPS
TTL: 3600
```

## 🔧 Deploy Manual (sem Docker)

### 1. Instalar Python e dependências

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum install python3 python3-pip nginx
```

### 2. Configurar a aplicação

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements_producao.txt

# Configurar Gunicorn como serviço
sudo nano /etc/systemd/system/projeto-gestao.service
```

```ini
[Unit]
Description=Sistema de Gestão de Projetos
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/projeto-gestao-2.0
Environment="PATH=/opt/projeto-gestao-2.0/venv/bin"
ExecStart=/opt/projeto-gestao-2.0/venv/bin/gunicorn --config gunicorn.conf.py app_producao:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/projeto-gestao
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/projeto-gestao-2.0/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/projeto-gestao /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Iniciar aplicação
sudo systemctl enable projeto-gestao
sudo systemctl start projeto-gestao
```

## 📊 Monitoramento

### 1. Logs

```bash
# Logs da aplicação
tail -f logs/app.log

# Logs do sistema
journalctl -f -u projeto-gestao

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. Status do Sistema

```bash
# Status dos serviços
systemctl status projeto-gestao
systemctl status nginx

# Uso de recursos
htop
df -h
free -h
```

## 🛡️ Segurança

### 1. Firewall

```bash
# Ubuntu (UFW)
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# CentOS (Firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. Atualizações Automáticas

```bash
# Ubuntu
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# CentOS
sudo yum install yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

## 🔄 Backup Automático

```bash
# Script de backup
nano backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/projeto-gestao"
APP_DIR="/opt/projeto-gestao-2.0"

mkdir -p $BACKUP_DIR

# Backup da aplicação
tar -czf $BACKUP_DIR/app_$DATE.tar.gz $APP_DIR

# Backup do banco (se local)
# pg_dump database_name > $BACKUP_DIR/db_$DATE.sql

# Limpar backups antigos (manter últimos 7)
find $BACKUP_DIR -name "app_*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

```bash
chmod +x backup.sh

# Agendar no cron (diário às 2h)
crontab -e
# Adicionar: 0 2 * * * /opt/projeto-gestao-2.0/backup.sh
```

---

**✅ Sistema configurado para acesso externo via VPS!**

Acesso: `http://seu-dominio.com` ou `http://IP_DO_VPS`