#!/usr/bin/env python3
"""
Teste da rota web de datas conflitantes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes.relatorio import relatorio_bp

# Criar uma aplicação Flask simples para teste
app = Flask(__name__)
app.config['SECRET_KEY'] = 'teste-123'

# Registrar o blueprint
app.register_blueprint(relatorio_bp, url_prefix='/relatorio')

# Função de teste que simula login
@app.before_request
def mock_login():
    from flask import session
    session['user_id'] = 'test-user'
    session['user_email'] = 'test@example.com'

if __name__ == '__main__':
    print("🚀 Iniciando aplicação de teste...")
    print("📍 A funcionalidade estará disponível em: http://localhost:5000/relatorio/datas-conflitantes")
    print("💡 Pressione Ctrl+C para parar")
    
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")