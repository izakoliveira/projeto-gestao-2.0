"""
Configuração do Gunicorn para Produção
Sistema de Gestão de Projetos v2.0.0
"""

import multiprocessing
import os

# Configurações básicas
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configurações de timeout
timeout = 30
keepalive = 2
graceful_timeout = 30

# Configurações de logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
preload_app = True
worker_tmp_dir = "/dev/shm"
worker_exit_on_app_exit = True

# Configurações de processo
user = os.environ.get('GUNICORN_USER', None)
group = os.environ.get('GUNICORN_GROUP', None)
tmp_upload_dir = None

# Configurações de SSL (se necessário)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

def when_ready(server):
    """Callback executado quando o servidor está pronto"""
    server.log.info("🚀 Servidor Gunicorn iniciado com sucesso!")

def on_starting(server):
    """Callback executado quando o servidor está iniciando"""
    server.log.info("🔄 Iniciando servidor Gunicorn...")

def on_exit(server):
    """Callback executado quando o servidor está saindo"""
    server.log.info("👋 Servidor Gunicorn finalizado!") 