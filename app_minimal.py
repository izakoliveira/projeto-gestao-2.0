#!/usr/bin/env python3
"""
App Mínimo para Teste no Render
Sistema de Gestão de Projetos v2.0.0
"""

import os
from flask import Flask, jsonify

print("🔍 RENDER TEST - Iniciando app mínimo...")
print(f"🔍 PORT: {os.environ.get('PORT', 'NÃO DEFINIDA')}")
print(f"🔍 SECRET_KEY: {'✅ DEFINIDA' if os.environ.get('SECRET_KEY') else '❌ NÃO DEFINIDA'}")

# Criar aplicação Flask mínima
app = Flask(__name__)

# Configuração básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'test-secret-key-123')

print("🔍 RENDER TEST - App criada!")

@app.route('/')
def home():
    """Página inicial básica"""
    print("🔍 RENDER TEST - Rota / acessada!")
    return jsonify({
        "status": "ok", 
        "message": "App mínimo funcionando no Render!",
        "version": "minimal-1.0",
        "port": os.environ.get('PORT', '5000')
    })

@app.route('/health')  
def health():
    """Health check básico"""
    print("🔍 RENDER TEST - Health check acessado!")
    return jsonify({
        "status": "healthy",
        "port": os.environ.get('PORT', '5000'),
        "secret_key_defined": bool(os.environ.get('SECRET_KEY')),
        "app": "minimal"
    })

@app.route('/test')
def test():
    """Rota de teste"""
    return jsonify({
        "message": "Rota de teste funcionando!",
        "env_vars": {
            "PORT": os.environ.get('PORT', 'NÃO DEFINIDA'),
            "FLASK_ENV": os.environ.get('FLASK_ENV', 'NÃO DEFINIDA'),
            "SECRET_KEY_EXISTS": bool(os.environ.get('SECRET_KEY'))
        }
    })

print("🔍 RENDER TEST - Rotas definidas!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🔍 RENDER TEST - Iniciando na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)