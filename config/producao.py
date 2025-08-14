"""
Configurações para Produção
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class ProducaoConfig:
    """Configurações para ambiente de produção"""
    
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sua-chave-secreta-producao')
    DEBUG = False
    TESTING = False
    
    # Configurações de sessão
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
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