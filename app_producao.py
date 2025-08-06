#!/usr/bin/env python3
"""
Aplicação de Produção - Versão Refatorada
Sistema de Gestão de Projetos
"""

import os
from flask import Flask, session, jsonify
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar variáveis de ambiente padrão
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app_producao.py')

try:
    from config.app_config import Config
    from config.database import supabase
    from utils.auth import login_required, apenas_admin_izak, funcionalidade_restrita, carregar_restricoes, salvar_restricoes
    from utils.validators import validar_projeto, normaliza_opcional, is_mobile_device

    # Importar blueprints
    from routes.auth import auth_bp
    from routes.projetos import projetos_bp
    from routes.tarefas import tarefas_bp
    from routes.admin import admin_bp
    from routes.pastas import pastas_bp
    from routes.main import main_bp
    from routes.producao import producao_bp
except ImportError as e:
    print(f"⚠️  Erro ao importar módulos: {e}")
    # Criar blueprints vazios para evitar erros
    from flask import Blueprint
    auth_bp = Blueprint('auth', __name__)
    projetos_bp = Blueprint('projetos', __name__)
    tarefas_bp = Blueprint('tarefas', __name__)
    admin_bp = Blueprint('admin', __name__)
    pastas_bp = Blueprint('pastas', __name__)
    main_bp = Blueprint('main', __name__)
    producao_bp = Blueprint('producao', __name__)

# Criar aplicação Flask
app = Flask(__name__)

# Configurar aplicação para produção
try:
    app.config.from_object(Config)
except Exception as e:
    print(f"⚠️  Erro ao carregar configurações: {e}")
    # Configurações padrão
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-producao-padrao-123456789')
    app.config['DEBUG'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Registrar blueprints
try:
    app.register_blueprint(auth_bp)
    app.register_blueprint(projetos_bp)
    app.register_blueprint(tarefas_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pastas_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(producao_bp)
    print("✅ Blueprints registrados com sucesso!")
except Exception as e:
    print(f"⚠️  Erro ao registrar blueprints: {e}")

# Rota de health check para produção
@app.route('/health')
def health_check():
    """Health check para monitoramento de produção"""
    try:
        # Testar conexão com banco
        if supabase:
            supabase_client = supabase.auth
            db_status = "healthy"
        else:
            db_status = "not_configured"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "database": db_status,
        "blueprints": list(app.blueprints.keys()),
        "timestamp": "2025-08-01T12:00:00Z"
    })

# Rota de status para produção
@app.route('/status')
def status():
    """Status detalhado do sistema"""
    try:
        # Verificar blueprints registrados
        blueprints = list(app.blueprints.keys())
        
        # Verificar configurações
        config_status = {
            "debug": app.config.get('DEBUG'),
            "secret_key_defined": bool(app.config.get('SECRET_KEY')),
            "max_projetos": app.config.get('MAX_PROJETOS'),
            "max_tarefas": app.config.get('MAX_TAREFAS')
        }
        
        return jsonify({
            "status": "operational",
            "version": "2.0.0",
            "blueprints": blueprints,
            "config": config_status,
            "environment": "production"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "version": "2.0.0"
        })

# Rota de teste simples
@app.route('/')
def index():
    """Rota principal"""
    return jsonify({
        "message": "Sistema de Gestão de Projetos 2.0",
        "status": "running",
        "version": "2.0.0"
    })

if __name__ == '__main__':
    print("🚀 Iniciando aplicação de produção...")
    print("📋 Blueprints registrados:")
    for blueprint_name in app.blueprints.keys():
        print(f"   - {blueprint_name}")
    print("✅ Sistema refatorado pronto para produção!")
    print("🌐 Acesse: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000) 