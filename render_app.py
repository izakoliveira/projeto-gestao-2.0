#!/usr/bin/env python3
"""
Script de inicialização para Render
Sistema de Gestão de Projetos v2.0.0
"""

import os
import sys
from datetime import timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar variáveis de ambiente padrão
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'render_app.py')

# Criar diretórios necessários
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('logs', exist_ok=True)

def create_app():
    """Criar aplicação Flask para Render"""
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'render-secret-key-123456789')
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Configurações de sessão
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    
    # Importar e registrar blueprints de forma segura
    try:
        from routes.main import main_bp
        app.register_blueprint(main_bp)
        print("✅ Blueprint main registrado")
    except ImportError as e:
        print(f"⚠️ Erro ao importar main blueprint: {e}")
    
    try:
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp)
        print("✅ Blueprint auth registrado")
    except ImportError as e:
        print(f"⚠️ Erro ao importar auth blueprint: {e}")
    
    try:
        from routes.projetos import projetos_bp
        app.register_blueprint(projetos_bp)
        print("✅ Blueprint projetos registrado")
    except ImportError as e:
        print(f"⚠️ Erro ao importar projetos blueprint: {e}")
    
    try:
        from routes.tarefas import tarefas_bp
        app.register_blueprint(tarefas_bp)
        print("✅ Blueprint tarefas registrado")
    except ImportError as e:
        print(f"⚠️ Erro ao importar tarefas blueprint: {e}")
    
    # Rotas básicas para funcionamento
    @app.route('/')
    def index():
        """Página inicial"""
        return jsonify({
            "message": "Sistema de Gestão de Projetos 2.0 - Render",
            "status": "running",
            "version": "2.0.0",
            "platform": "render"
        })
    
    @app.route('/health')
    def health_check():
        """Health check para Render"""
        try:
            # Verificar variáveis de ambiente
            supabase_status = "configured" if os.environ.get('SUPABASE_URL') else "not_configured"
            
            return jsonify({
                "status": "healthy",
                "version": "2.0.0",
                "platform": "render",
                "supabase": supabase_status,
                "blueprints": list(app.blueprints.keys()),
                "port": os.environ.get('PORT', '5000')
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e),
                "version": "2.0.0"
            }), 500
    
    @app.route('/status')
    def status():
        """Status detalhado"""
        return jsonify({
            "status": "operational",
            "version": "2.0.0",
            "platform": "render",
            "environment": "production",
            "blueprints": list(app.blueprints.keys()),
            "config": {
                "debug": app.config.get('DEBUG'),
                "testing": app.config.get('TESTING'),
                "secret_key_configured": bool(app.config.get('SECRET_KEY'))
            }
        })
    
    # Função de contexto para templates
    try:
        from utils.dias_uteis import dias_uteis_entre_datas
        @app.context_processor
        def utility_processor():
            return dict(dias_uteis_entre_datas=dias_uteis_entre_datas)
    except ImportError:
        print("⚠️ Utilitários de dias úteis não disponíveis")
    
    return app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando aplicação no Render na porta {port}")
    print(f"🌐 Blueprints disponíveis: {list(app.blueprints.keys())}")
    app.run(debug=False, host='0.0.0.0', port=port)