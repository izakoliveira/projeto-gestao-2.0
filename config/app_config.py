import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Configuração da aplicação Flask
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("FLASK_SECRET_KEY")
    
    if not SECRET_KEY:
        # Em produção, usar uma chave padrão se não estiver definida
        SECRET_KEY = "sua-chave-secreta-producao-padrao-123456789"
    
    # Configurações de sessão
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de debug
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Limites de segurança
    MAX_PROJETOS = 100
    MAX_TAREFAS = 200 