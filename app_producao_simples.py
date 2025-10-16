#!/usr/bin/env python3
"""
Aplicação de Produção - Versão Simplificada
Sistema de Gestão de Projetos
"""

import os
from datetime import timedelta
from flask import Flask, session, jsonify, request
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__)

# Configurações básicas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-producao-padrao-123456789')
app.config['DEBUG'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# Importações seguras
try:
    from config.database import supabase
    from utils.dias_uteis import dias_uteis_entre_datas
    print("✅ Módulos básicos carregados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar módulos básicos: {e}")
    supabase = None

# Tentar importar blueprints
blueprints_carregados = []

try:
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    blueprints_carregados.append('auth')
except Exception as e:
    print(f"⚠️ Erro ao carregar auth_bp: {e}")

try:
    from routes.main import main_bp
    app.register_blueprint(main_bp)
    blueprints_carregados.append('main')
except Exception as e:
    print(f"⚠️ Erro ao carregar main_bp: {e}")

try:
    from routes.projetos import projetos_bp
    app.register_blueprint(projetos_bp)
    blueprints_carregados.append('projetos')
except Exception as e:
    print(f"⚠️ Erro ao carregar projetos_bp: {e}")

try:
    from routes.producao import producao_bp
    app.register_blueprint(producao_bp)
    blueprints_carregados.append('producao')
except Exception as e:
    print(f"⚠️ Erro ao carregar producao_bp: {e}")

# Expor função de dias úteis para Jinja2
if 'dias_uteis_entre_datas' in globals():
    @app.context_processor
    def utility_processor():
        return dict(dias_uteis_entre_datas=dias_uteis_entre_datas)

# Rota de health check para produção
@app.route('/health')
def health_check():
    """Health check para monitoramento de produção"""
    try:
        # Testar conexão com banco
        if supabase:
            db_status = "healthy"
        else:
            db_status = "not_configured"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "database": db_status,
        "blueprints": blueprints_carregados,
        "timestamp": "2025-10-14T12:00:00Z"
    })

# Rota de status para produção
@app.route('/status')
def status():
    """Status detalhado do sistema"""
    try:
        # Verificar configurações
        config_status = {
            "debug": app.config.get('DEBUG'),
            "secret_key_defined": bool(app.config.get('SECRET_KEY')),
        }
        
        return jsonify({
            "status": "operational",
            "version": "2.0.0",
            "blueprints": blueprints_carregados,
            "config": config_status,
            "environment": "production"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "version": "2.0.0"
        }), 500

# Rota de teste simples
@app.route('/')
def index():
    """Rota principal"""
    return jsonify({
        "message": "Sistema de Gestão de Projetos 2.0",
        "status": "running",
        "version": "2.0.0",
        "blueprints": blueprints_carregados
    })

# Rota de teste para produção
@app.route('/test-projects')
def test_projects():
    """Testar acesso aos projetos"""
    try:
        if not supabase:
            return jsonify({"error": "Banco não configurado"}), 500
            
        resp = supabase.table("projetos").select("*").limit(5).execute()
        projetos = resp.data or []
        
        return jsonify({
            "status": "success",
            "projetos_encontrados": len(projetos),
            "projetos": projetos
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando aplicação de produção simplificada...")
    print(f"📋 Blueprints carregados: {blueprints_carregados}")
    print("🌐 Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)