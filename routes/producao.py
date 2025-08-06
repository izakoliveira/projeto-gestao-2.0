from flask import Blueprint, render_template, request, jsonify, session
from utils.auth import login_required
import json
import os

producao_bp = Blueprint('producao', __name__)

@producao_bp.route('/producao')
@login_required
def producao_dashboard():
    """Dashboard do sistema de produção"""
    return render_template('producao/dashboard.html')

@producao_bp.route('/producao/calendario')
@login_required
def producao_calendario():
    """Calendário de produção"""
    return render_template('producao/calendario.html')

@producao_bp.route('/producao/colecoes')
@login_required
def producao_colecoes():
    """Gerenciamento de coleções"""
    return render_template('producao/colecoes.html')

@producao_bp.route('/producao/projecoes')
@login_required
def producao_projecoes():
    """Projeções de produção"""
    return render_template('producao/projecoes.html')

@producao_bp.route('/producao/atividades')
@login_required
def producao_atividades():
    """Atividades/cronograma"""
    return render_template('producao/atividades.html')

@producao_bp.route('/producao/feriados')
@login_required
def producao_feriados():
    """Feriados"""
    return render_template('producao/feriados.html')

# API endpoints para o sistema de produção
@producao_bp.route('/api/producao/colecoes', methods=['GET'])
@login_required
def api_colecoes():
    """API para obter coleções"""
    try:
        # Carregar dados do localStorage (simulado)
        colecoes = json.loads(request.args.get('colecoes', '[]'))
        return jsonify(colecoes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producao_bp.route('/api/producao/colecoes', methods=['POST'])
@login_required
def api_criar_colecao():
    """API para criar coleção"""
    try:
        data = request.get_json()
        # Aqui você pode integrar com o banco de dados do projeto
        return jsonify({'success': True, 'message': 'Coleção criada com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producao_bp.route('/api/producao/eventos', methods=['GET'])
@login_required
def api_eventos():
    """API para obter eventos"""
    try:
        eventos = json.loads(request.args.get('eventos', '[]'))
        return jsonify(eventos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producao_bp.route('/api/producao/eventos', methods=['POST'])
@login_required
def api_criar_evento():
    """API para criar evento"""
    try:
        data = request.get_json()
        # Aqui você pode integrar com o banco de dados do projeto
        return jsonify({'success': True, 'message': 'Evento criado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 