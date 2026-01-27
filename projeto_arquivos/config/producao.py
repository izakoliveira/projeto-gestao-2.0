"""
Configurações para Produção
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

class ConfigProducao:
    """Configurações específicas para produção"""
    SECRET_KEY = os.getenv("SECRET_KEY") or "sua-chave-secreta-producao-123456789"
    DEBUG = False
    TESTING = False
    
    # Configurações do Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Configurações de sessão
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # 8 horas usando timedelta
    SESSION_COOKIE_SECURE = False  # Temporariamente False para debug
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de segurança
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Configurações de banco
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Configurações de aplicação
    MAX_PROJETOS = 100
    MAX_TAREFAS = 200
    
    # Configurações de logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    
    # Configurações de cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Configurações de rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Configurações de compressão
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml',
        'application/json', 'application/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500 