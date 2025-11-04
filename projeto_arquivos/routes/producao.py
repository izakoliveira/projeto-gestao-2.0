from flask import Blueprint, render_template, request, jsonify, session, flash
from utils.auth import login_required, is_admin_session
from config.database import supabase
from datetime import datetime
import json
import os

producao_bp = Blueprint('producao', __name__)

@producao_bp.route('/producao')
@login_required
def producao_dashboard():
    """Dashboard do sistema de produção"""
    try:
        # Buscar estatísticas dos projetos
        if is_admin_session():
            projetos_resp = supabase.table("projetos").select("*").execute()
            tarefas_resp = supabase.table("tarefas").select("*").execute()
        else:
            usuario_id = session['user_id']
            projetos_resp = supabase.table("projetos").select("*").eq("usuario_id", usuario_id).execute()
            # Buscar tarefas dos projetos do usuário
            if projetos_resp.data:
                projeto_ids = [p['id'] for p in projetos_resp.data]
                tarefas_resp = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute()
            else:
                tarefas_resp = supabase.table("tarefas").select("*").limit(0).execute()
        
        projetos = projetos_resp.data or []
        tarefas = tarefas_resp.data or []
        
        # Calcular estatísticas
        total_projetos = len(projetos)
        total_tarefas = len(tarefas)
        
        # Projetos ativos (sem data fim ou data fim futura)
        hoje = datetime.now().date()
        projetos_ativos = len([p for p in projetos if not p.get('data_fim') or 
                              (p.get('data_fim') and datetime.strptime(p['data_fim'], '%Y-%m-%d').date() >= hoje)])
        
        # Tarefas concluídas
        tarefas_concluidas = len([t for t in tarefas if t.get('status') == 'CONCLUIDA'])
        
        stats = {
            'total_projetos': total_projetos,
            'projetos_ativos': projetos_ativos,
            'total_tarefas': total_tarefas,
            'tarefas_concluidas': tarefas_concluidas
        }
        
        return render_template('producao/dashboard.html', stats=stats, projetos=projetos, tarefas=tarefas)
    except Exception as e:
        flash(f"Erro ao carregar dashboard: {str(e)}", "error")
        return render_template('producao/dashboard.html', stats={}, projetos=[], tarefas=[])

@producao_bp.route('/producao/calendario')
@login_required
def producao_calendario():
    """Calendário de produção"""
    return render_template('producao/calendario.html')

@producao_bp.route('/producao/colecoes')
@login_required
def producao_colecoes():
    """Gerenciamento de coleções - integrado com projetos"""
    try:
        # Buscar projetos do banco de dados
        if is_admin_session():
            # Admin vê todos os projetos
            projetos_resp = supabase.table("projetos").select("*").execute()
        else:
            # Usuário vê apenas seus projetos
            usuario_id = session['user_id']
            projetos_resp = supabase.table("projetos").select("*").eq("usuario_id", usuario_id).execute()
        
        projetos = projetos_resp.data or []
        
        # Buscar tipos (pastas) disponíveis
        try:
            if is_admin_session():
                tipos_resp = supabase.table("pastas").select("*").execute()
            else:
                usuario_id = session['user_id']
                tipos_resp = supabase.table("pastas").select("*").eq("usuario_id", usuario_id).execute()
            tipos = tipos_resp.data or []
        except Exception as e:
            print(f"Erro ao buscar tipos/pastas: {e}")
            # Fallback: criar tipos baseados nos tipo_id únicos dos projetos
            tipos_unicos = list(set([p['tipo_id'] for p in projetos if p.get('tipo_id')]))
            tipos = []
            for i, tipo_id in enumerate(tipos_unicos):
                tipos.append({
                    'id': tipo_id,
                    'nome': f'Tipo {i + 1}'
                })
        
        return render_template('producao/colecoes.html', projetos=projetos, tipos=tipos)
    except Exception as e:
        flash(f"Erro ao carregar coleções: {str(e)}", "error")
        return render_template('producao/colecoes.html', projetos=[], tipos=[])

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
    """API para obter coleções (projetos)"""
    try:
        # Buscar projetos do banco de dados
        if is_admin_session():
            projetos_resp = supabase.table("projetos").select("*").execute()
        else:
            usuario_id = session['user_id']
            projetos_resp = supabase.table("projetos").select("*").eq("usuario_id", usuario_id).execute()
        
        projetos = projetos_resp.data or []
        return jsonify(projetos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producao_bp.route('/api/producao/colecoes', methods=['POST'])
@login_required
def api_criar_colecao():
    """API para criar coleção (projeto)"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('nome'):
            return jsonify({'error': 'Nome da coleção é obrigatório'}), 400
        
        # Preparar dados do projeto
        projeto_data = {
            'nome': data['nome'],
            'data_inicio': data.get('data_inicio') if data.get('data_inicio') else None,
            'data_fim': data.get('data_fim') if data.get('data_fim') else None,
            'tipo_id': data.get('tipo_id') if data.get('tipo_id') else None,
            'usuario_id': session['user_id']
        }
        
        # Criar projeto no banco
        projeto_resp = supabase.table("projetos").insert(projeto_data).execute()
        
        if projeto_resp.data:
            return jsonify({
                'success': True, 
                'message': 'Coleção (projeto) criada com sucesso',
                'projeto': projeto_resp.data[0]
            })
        else:
            return jsonify({'error': 'Erro ao criar coleção no banco de dados'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producao_bp.route('/api/producao/colecoes/<projeto_id>', methods=['PUT'])
@login_required
def api_atualizar_colecao(projeto_id):
    """API para atualizar coleção (projeto)"""
    try:
        data = request.get_json()
        
        # Verificar se o usuário pode editar este projeto
        projeto_resp = supabase.table("projetos").select("*").eq("id", projeto_id).execute()
        if not projeto_resp.data:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        projeto = projeto_resp.data[0]
        if not is_admin_session() and projeto['usuario_id'] != session['user_id']:
            return jsonify({'error': 'Sem permissão para editar este projeto'}), 403
        
        # Preparar dados de atualização
        update_data = {}
        if 'nome' in data:
            update_data['nome'] = data['nome']
        if 'data_inicio' in data:
            update_data['data_inicio'] = data['data_inicio']
        if 'data_fim' in data:
            update_data['data_fim'] = data['data_fim']
        if 'tipo_id' in data:
            update_data['tipo_id'] = data['tipo_id']
        
        # Atualizar projeto
        update_resp = supabase.table("projetos").update(update_data).eq("id", projeto_id).execute()
        
        if update_resp.data:
            return jsonify({
                'success': True, 
                'message': 'Coleção atualizada com sucesso',
                'projeto': update_resp.data[0]
            })
        else:
            return jsonify({'error': 'Erro ao atualizar coleção'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producao_bp.route('/api/producao/colecoes/<projeto_id>', methods=['DELETE'])
@login_required
def api_deletar_colecao(projeto_id):
    """API para deletar coleção (projeto)"""
    try:
        # Verificar se o usuário pode deletar este projeto
        projeto_resp = supabase.table("projetos").select("*").eq("id", projeto_id).execute()
        if not projeto_resp.data:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        projeto = projeto_resp.data[0]
        if not is_admin_session() and projeto['usuario_id'] != session['user_id']:
            return jsonify({'error': 'Sem permissão para deletar este projeto'}), 403
        
        # Verificar se há tarefas associadas
        tarefas_resp = supabase.table("tarefas").select("id").eq("projeto_id", projeto_id).execute()
        if tarefas_resp.data:
            return jsonify({'error': 'Não é possível deletar projeto com tarefas associadas'}), 400
        
        # 1. Deletar notificações relacionadas ao projeto primeiro
        try:
            supabase.table("notificacoes").delete().eq("projeto_id", projeto_id).execute()
        except Exception as e_notif:
            print(f"[PRODUCAO] Erro ao excluir notificações: {e_notif}")
            # Continue mesmo se houver erro
        
        # 2. Deletar projeto
        delete_resp = supabase.table("projetos").delete().eq("id", projeto_id).execute()
        
        if delete_resp.data:
            return jsonify({
                'success': True, 
                'message': 'Coleção deletada com sucesso'
            })
        else:
            return jsonify({'error': 'Erro ao deletar coleção'}), 500
            
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