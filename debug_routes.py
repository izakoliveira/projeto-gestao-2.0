from flask import Blueprint, send_from_directory, jsonify
from config.database import supabase
import os

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/teste-projetos')
def teste_projetos():
    """Serve o arquivo de teste de debug"""
    return send_from_directory('.', 'teste_debug_projetos.html')

@debug_bp.route('/api/projetos')
def api_projetos():
    """API simples para retornar projetos"""
    try:
        projetos_resp = supabase.table('projetos').select('id, nome').order('nome').execute()
        if projetos_resp.data:
            return jsonify(projetos_resp.data)
        else:
            return jsonify([])
    except Exception as e:
        print(f"Erro ao buscar projetos: {e}")
        return jsonify([]), 500