"""
Aplicação de Gestão de Projetos com Gantt
==========================================

Sistema web para gestão de projetos com visualização de tarefas em gráfico de Gantt,
desenvolvido em Flask e integrado ao Supabase.
"""

from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    """Factory function para criar a aplicação Flask"""
    # Carrega as variáveis do .env
    load_dotenv()
    
    # Inicializa Flask
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Carregar a chave secreta do arquivo .env
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    
    # Verifica se a chave secreta foi carregada corretamente
    if not app.secret_key:
        raise Exception("FLASK_SECRET_KEY não definida no arquivo .env")
    
    # Configurar extensões e blueprints
    from app.config.database import init_supabase
    from app.routes import auth, dashboard
    
    # Inicializar Supabase
    init_supabase()
    
    # Registrar blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    
    return app 