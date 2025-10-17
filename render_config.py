"""
Configuração específica para Render
Sistema de Gestão de Projetos v2.0.0
"""

import os

# Configurações específicas do Render
class RenderConfig:
    # Usar PORT do Render se disponível
    PORT = int(os.environ.get('PORT', 5000))
    
    # Configurações de produção
    DEBUG = False
    TESTING = False
    
    # Chave secreta
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-render-123456789')
    
    # Supabase
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Configurações de sessão
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 28800  # 8 horas em segundos
    
    # Configurações específicas do Render
    HOST = '0.0.0.0'
    RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
    
    @classmethod
    def validate_config(cls):
        """Valida se todas as configurações necessárias estão presentes"""
        required_vars = ['SECRET_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
        missing = []
        
        for var in required_vars:
            if not getattr(cls, var, None):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing)}")
        
        return True