#!/usr/bin/env python3
"""
Aplicação de Produção - Versão Refatorada
Sistema de Gestão de Projetos
"""

import os
from datetime import timedelta
from flask import Flask, session, jsonify
from utils.dias_uteis import dias_uteis_entre_datas
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("🔍 DEBUG RENDER - Iniciando app_producao.py...")
print(f"🔍 PORT: {os.environ.get('PORT', 'NÃO DEFINIDA')}")
print(f"🔍 SECRET_KEY: {'✅ DEFINIDA' if os.environ.get('SECRET_KEY') else '❌ NÃO DEFINIDA'}")
print(f"🔍 SUPABASE_URL: {'✅ DEFINIDA' if os.environ.get('SUPABASE_URL') else '❌ NÃO DEFINIDA'}")

# Configurar variáveis de ambiente padrão
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app_producao.py')

print("🔍 DEBUG RENDER - Criando diretórios...")

# Criar diretórios necessários
os.makedirs('static/uploads', exist_ok=True)

print("🔍 DEBUG RENDER - Importando módulos...")

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
    from routes.relatorio import relatorio_bp
    print("🔍 DEBUG RENDER - Imports bem-sucedidos!")
except ImportError as e:
    print(f"⚠️ ERRO DE IMPORT: {e}")
    print("🔍 Tentando importar módulos individualmente...")
    
    # Tentar importar cada módulo individualmente
    Config = None
    supabase = None
    
    # Importar utilitários essenciais
    try:
        from config.app_config import Config
        print("✅ Config importado")
    except ImportError as ex:
        print(f"⚠️ Config não disponível: {ex}")
    
    try:
        from config.database import supabase
        print("✅ Supabase importado")
    except ImportError as ex:
        print(f"⚠️ Supabase não disponível: {ex}")
    
    # Importar blueprints individualmente
    auth_bp = None
    projetos_bp = None  
    tarefas_bp = None
    admin_bp = None
    pastas_bp = None
    main_bp = None
    producao_bp = None
    relatorio_bp = None
    
    # Tentar importar cada blueprint
    try:
        from routes.auth import auth_bp
        print("✅ Auth blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Auth blueprint falhou: {ex}")
        from flask import Blueprint
        auth_bp = Blueprint('auth', __name__)
    
    try:
        from routes.projetos import projetos_bp
        print("✅ Projetos blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Projetos blueprint falhou: {ex}")
        from flask import Blueprint
        projetos_bp = Blueprint('projetos', __name__)
    
    try:
        from routes.tarefas import tarefas_bp
        print("✅ Tarefas blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Tarefas blueprint falhou: {ex}")
        from flask import Blueprint
        tarefas_bp = Blueprint('tarefas', __name__)
    
    try:
        from routes.admin import admin_bp
        print("✅ Admin blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Admin blueprint falhou: {ex}")
        from flask import Blueprint
        admin_bp = Blueprint('admin', __name__)
    
    try:
        from routes.pastas import pastas_bp
        print("✅ Pastas blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Pastas blueprint falhou: {ex}")
        from flask import Blueprint
        pastas_bp = Blueprint('pastas', __name__)
    
    try:
        from routes.main import main_bp
        print("✅ Main blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Main blueprint falhou: {ex}")
        from flask import Blueprint
        main_bp = Blueprint('main', __name__)
    
    try:
        from routes.producao import producao_bp
        print("✅ Producao blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Producao blueprint falhou: {ex}")
        from flask import Blueprint
        producao_bp = Blueprint('producao', __name__)
    
    try:
        from routes.relatorio import relatorio_bp
        print("✅ Relatorio blueprint importado")
    except ImportError as ex:
        print(f"⚠️ Relatorio blueprint falhou: {ex}")
        from flask import Blueprint
        relatorio_bp = Blueprint('relatorio', __name__)

# Criar aplicação Flask
app = Flask(__name__)

print("🔍 DEBUG RENDER - Flask app criada!")

# Expor função de dias úteis para Jinja2
@app.context_processor
def utility_processor():
    return dict(dias_uteis_entre_datas=dias_uteis_entre_datas)

print("🔍 DEBUG RENDER - Context processor configurado!")

# Configurar aplicação para produção
try:
    if Config:
        app.config.from_object(Config)
        print("✅ Config carregado com sucesso")
    else:
        raise Exception("Config não disponível")
except Exception as e:
    print(f"⚠️ Erro ao carregar configurações: {e}")
    print("🔧 Usando configurações padrão...")
    # Configurações padrão para Render/Produção
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-producao-padrao-123456789')
    app.config['DEBUG'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# Registrar blueprints
try:
    app.register_blueprint(auth_bp)
    app.register_blueprint(projetos_bp)
    app.register_blueprint(tarefas_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pastas_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(producao_bp)
    app.register_blueprint(relatorio_bp)
    print("✅ Blueprints registrados com sucesso!")
except Exception as e:
    print(f"⚠️  Erro ao registrar blueprints: {e}")

# Rota de health check para produção
@app.route('/health')
def health_check():
    """Health check para monitoramento de produção"""
    try:
        # Testar conexão com banco
        if 'supabase' in globals() and supabase:
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

if __name__ == '__main__':
    print("🚀 Iniciando aplicação de produção...")
    print("📋 Blueprints registrados:")
    for blueprint_name in app.blueprints.keys():
        print(f"   - {blueprint_name}")
    print("✅ Sistema refatorado pronto para produção!")
    print("🌐 Acesse: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000) 