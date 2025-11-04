"""
Configuração Simplificada do Gunicorn para Render
Sistema de Gestão de Projetos v2.0.0
"""

import os

# Configurações básicas - SIMPLIFICADAS PARA RENDER
bind = "0.0.0.0:" + str(os.environ.get('PORT', 5000))
workers = 1  # Render Free tier - apenas 1 worker
worker_class = "sync"
timeout = 120  # Timeout aumentado para Render
keepalive = 2
graceful_timeout = 30

# Configurações de logging simplificadas
accesslog = "-"  # Log para stdout  
errorlog = "-"   # Log para stderr
loglevel = "info"

# Configurações de performance básicas
max_requests = 1000
max_requests_jitter = 50
preload_app = True

def on_starting(server):
    """Callback executado quando o servidor está iniciando"""
    server.log.info("� Iniciando servidor Gunicorn no Render...")
    server.log.info(f"🌐 Porta: {os.environ.get('PORT', '5000')}")

def when_ready(server):
    """Callback executado quando o servidor está pronto"""
    server.log.info("� Servidor Gunicorn pronto no Render!")

def on_exit(server):
    """Callback executado quando o servidor está saindo"""
    server.log.info("👋 Servidor Gunicorn finalizado!") 