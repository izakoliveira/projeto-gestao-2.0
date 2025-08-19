"""
Configurações de email para produção
Este arquivo pode ser usado para configurar o sistema de email
quando as variáveis de ambiente não estão disponíveis
"""

# Configurações padrão para produção
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_user': None,  # Deve ser configurado via variável de ambiente
    'smtp_pass': None,  # Deve ser configurado via variável de ambiente
    'from_name': 'Sistema de Gestão de Projetos',
    'use_tls': True,
    'timeout': 10
}

# Configurações alternativas para outros provedores
ALTERNATIVE_CONFIGS = {
    'outlook': {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'use_tls': True
    },
    'yahoo': {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'use_tls': True
    },
    'protonmail': {
        'smtp_server': 'smtp.protonmail.ch',
        'smtp_port': 587,
        'use_tls': True
    }
}

def get_email_config(provider='gmail'):
    """Retorna configuração de email para o provedor especificado"""
    config = EMAIL_CONFIG.copy()
    
    if provider in ALTERNATIVE_CONFIGS:
        config.update(ALTERNATIVE_CONFIGS[provider])
    
    return config
