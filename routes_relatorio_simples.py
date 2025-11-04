# routes/relatorio.py - Versão sem matplotlib para Render
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import json

# Criar blueprint
relatorio_bp = Blueprint('relatorio', __name__)

@relatorio_bp.route('/relatorios')
def listar_relatorios():
    """Página de relatórios (versão simplificada)"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('relatorios/lista.html', 
                         titulo="Relatórios do Sistema")

@relatorio_bp.route('/api/relatorios/projetos')
def relatorio_projetos():
    """API de relatórios de projetos (sem gráficos)"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Dados simulados para evitar erro
    dados = {
        'total_projetos': 0,
        'projetos_ativos': 0, 
        'projetos_concluidos': 0,
        'projetos_atrasados': 0,
        'message': 'Relatórios temporariamente indisponíveis - aguardando correção do matplotlib'
    }
    
    return jsonify(dados)

print("DEBUG: routes/relatorio.py (versão simplificada) carregado com sucesso")