#!/usr/bin/env python3
"""
Teste simples do sistema de produção
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Sistema funcionando", "status": "ok"})

@app.route('/test-producao')
def test_producao():
    try:
        from config.database import supabase
        
        # Testar conexão
        resp = supabase.table("projetos").select("*").limit(2).execute()
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
    print("🧪 Testando sistema de produção...")
    app.run(debug=True, host='0.0.0.0', port=5001)