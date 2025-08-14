from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita, apenas_admin_izak, carregar_restricoes
from utils.validators import is_mobile_device, normaliza_opcional, verificar_tarefa_atrasada
from config.database import supabase
import requests
from datetime import datetime

# Criar blueprint para rotas principais
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if 'user_id' in session:
        return redirect('/dashboard')
    else:
        return redirect('/login')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal do usuário"""
    try:
        # Buscar projetos próprios do usuário
        projetos_resp = supabase.table("projetos").select("id").eq("usuario_id", session['user_id']).execute()
        projetos_proprios = projetos_resp.data if hasattr(projetos_resp, 'data') else []
        projetos_proprios_ids = [p['id'] for p in projetos_proprios]
        
        # Buscar projetos compartilhados (permissões de visualização)
        try:
            permissoes_resp = supabase.table("projetos_usuarios_visiveis").select("projeto_id").eq("usuario_id", session['user_id']).execute()
            permissoes = permissoes_resp.data if hasattr(permissoes_resp, 'data') else []
            projetos_compartilhados_ids = [p['projeto_id'] for p in permissoes]
        except Exception as e:
            print(f"Erro ao buscar permissões: {str(e)}")
            projetos_compartilhados_ids = []
        
        # Combinar todos os projetos acessíveis
        todos_projetos_ids = projetos_proprios_ids + projetos_compartilhados_ids
        projetos_count = len(todos_projetos_ids)
        
        # Buscar tarefas do usuário
        tarefas_usuario_resp = supabase.table("tarefas").select("id, status").eq("usuario_id", session['user_id']).execute()
        tarefas_usuario = tarefas_usuario_resp.data if hasattr(tarefas_usuario_resp, 'data') else []
        
        # Buscar tarefas dos projetos acessíveis
        tarefas_projetos = []
        if todos_projetos_ids:
            for projeto_id in todos_projetos_ids:
                tarefas_projeto_resp = supabase.table("tarefas").select("id, status").eq("projeto_id", projeto_id).execute()
                tarefas_projeto = tarefas_projeto_resp.data if hasattr(tarefas_projeto_resp, 'data') else []
                tarefas_projetos.extend(tarefas_projeto)
        
        # Combinar e remover duplicatas
        todas_tarefas = tarefas_usuario + tarefas_projetos
        tarefas_unicas = {t['id']: t for t in todas_tarefas}.values()
        tarefas = list(tarefas_unicas)
        tarefas_count = len(tarefas)
        
        # Contar tarefas por status
        tarefas_concluidas = len([t for t in tarefas if t.get('status') == 'concluída'])
        tarefas_pendentes = len([t for t in tarefas if t.get('status') == 'pendente'])
        tarefas_em_andamento = len([t for t in tarefas if t.get('status') == 'em progresso'])
        
        # Buscar projetos recentes (próprios e compartilhados)
        projetos_recentes = []
        
        # Projetos próprios
        if projetos_proprios_ids:
            projetos_proprios_resp = supabase.table("projetos").select("*").in_("id", projetos_proprios_ids).limit(5).execute()
            projetos_proprios_data = projetos_proprios_resp.data if hasattr(projetos_proprios_resp, 'data') else []
            projetos_recentes.extend(projetos_proprios_data)
        
        # Projetos compartilhados
        if projetos_compartilhados_ids:
            projetos_compartilhados_resp = supabase.table("projetos").select("*").in_("id", projetos_compartilhados_ids).limit(5).execute()
            projetos_compartilhados_data = projetos_compartilhados_resp.data if hasattr(projetos_compartilhados_resp, 'data') else []
            projetos_recentes.extend(projetos_compartilhados_data)
        
        # Limitar a 5 projetos recentes
        projetos_recentes = projetos_recentes[:5]
        
        # Buscar tarefas recentes (do usuário e dos projetos acessíveis)
        tarefas_recentes = []
        
        # Tarefas dos projetos acessíveis
        if todos_projetos_ids:
            for projeto_id in todos_projetos_ids[:5]:  # Limitar a 5 projetos
                tarefas_recente_resp = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).limit(1).execute()
                tarefas_recente = tarefas_recente_resp.data if hasattr(tarefas_recente_resp, 'data') else []
                # Adicionar informações do projeto
                for tarefa in tarefas_recente:
                    projeto_info = next((p for p in projetos_recentes if p['id'] == projeto_id), None)
                    if projeto_info:
                        tarefa['projeto_nome'] = projeto_info['nome']
                    else:
                        # Buscar nome do projeto se não estiver na lista de recentes
                        projeto_nome_resp = supabase.table("projetos").select("nome").eq("id", projeto_id).execute()
                        if hasattr(projeto_nome_resp, 'data') and projeto_nome_resp.data:
                            tarefa['projeto_nome'] = projeto_nome_resp.data[0]['nome']
                        else:
                            tarefa['projeto_nome'] = 'Projeto não encontrado'
                tarefas_recentes.extend(tarefas_recente)
        
        # Adicionar tarefas do usuário
        tarefas_usuario_recente_resp = supabase.table("tarefas").select("*").eq("usuario_id", session['user_id']).limit(5).execute()
        tarefas_usuario_recente = tarefas_usuario_recente_resp.data if hasattr(tarefas_usuario_recente_resp, 'data') else []
        # Adicionar informações do projeto para tarefas do usuário
        for tarefa in tarefas_usuario_recente:
            if tarefa.get('projeto_id'):
                projeto_info = next((p for p in projetos_recentes if p['id'] == tarefa['projeto_id']), None)
                if projeto_info:
                    tarefa['projeto_nome'] = projeto_info['nome']
                else:
                    # Buscar nome do projeto se não estiver na lista de recentes
                    projeto_nome_resp = supabase.table("projetos").select("nome").eq("id", tarefa['projeto_id']).execute()
                    if hasattr(projeto_nome_resp, 'data') and projeto_nome_resp.data:
                        tarefa['projeto_nome'] = projeto_nome_resp.data[0]['nome']
                    else:
                        tarefa['projeto_nome'] = 'Projeto não encontrado'
            else:
                tarefa['projeto_nome'] = 'Sem projeto'
        tarefas_recentes.extend(tarefas_usuario_recente)
        
        # Remover duplicatas das tarefas recentes
        tarefas_recentes_unicas = {t['id']: t for t in tarefas_recentes}.values()
        tarefas_recentes = list(tarefas_recentes_unicas)[:5]  # Limitar a 5
        
        stats = {
            'projetos_count': projetos_count,
            'tarefas_count': tarefas_count,
            'tarefas_concluidas': tarefas_concluidas,
            'tarefas_pendentes': tarefas_pendentes,
            'tarefas_em_andamento': tarefas_em_andamento
        }
        
    except Exception as e:
        flash(f"Erro ao carregar dashboard: {str(e)}")
        stats = {
            'projetos_count': 0,
            'tarefas_count': 0,
            'tarefas_concluidas': 0,
            'tarefas_pendentes': 0,
            'tarefas_em_andamento': 0
        }
        projetos_recentes = []
        tarefas_recentes = []
    
    return render_template('dashboard.html', 
                         stats=stats,
                         projetos_recentes=projetos_recentes,
                         tarefas_recentes=tarefas_recentes)

@main_bp.route('/projetos/<uuid:projeto_id>')
@login_required
def detalhes_projeto(projeto_id):
    """Página de detalhes de um projeto específico"""
    try:
        # Buscar projeto
        projeto_resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
        if not projeto:
            flash("Projeto não encontrado.")
            return redirect('/projetos')
    except Exception as e:
        flash(f"Erro ao buscar projeto: {str(e)}")
        return redirect('/projetos')

    try:
        # Buscar tarefas do projeto
        tarefas_resp = supabase.table("tarefas").select("*").eq("projeto_id", str(projeto_id)).order("ordem").execute()
        tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []
        
        # Preparar datas das tarefas para exibição
        for tarefa in tarefas:
            # Preparar data_inicio_iso
            data_inicio = tarefa.get('data_inicio')
            if data_inicio:
                try:
                    if '/' in data_inicio:
                        data_inicio_iso = datetime.strptime(data_inicio, '%d/%m/%Y').strftime('%Y-%m-%d')
                    elif 'T' in data_inicio:
                        data_inicio_iso = data_inicio.split('T')[0]
                    else:
                        data_inicio_iso = data_inicio
                except Exception:
                    data_inicio_iso = data_inicio
                tarefa['data_inicio_iso'] = data_inicio_iso
            else:
                tarefa['data_inicio_iso'] = ''
            
            # Preparar data_fim_iso
            data_fim = tarefa.get('data_fim')
            if data_fim:
                try:
                    if '/' in data_fim:
                        data_fim_iso = datetime.strptime(data_fim, '%d/%m/%Y').strftime('%Y-%m-%d')
                    elif 'T' in data_fim:
                        data_fim_iso = data_fim.split('T')[0]
                    else:
                        data_fim_iso = data_fim
                except Exception:
                    data_fim_iso = data_fim
                tarefa['data_fim_iso'] = data_fim_iso
            else:
                tarefa['data_fim_iso'] = ''
            
            # Marcar se as datas são calculadas (para exibição visual)
            tarefa['data_inicio_calculada'] = False
            tarefa['data_fim_calculada'] = False
            
            # Verificar se a tarefa está atrasada
            tarefa['atrasada'] = verificar_tarefa_atrasada(tarefa)
    except Exception as e:
        flash(f"Erro ao buscar tarefas: {str(e)}")
        tarefas = []
    
    # Gerar cores para projetos (para o gráfico Gantt)
    import hashlib
    
    # Paleta de cores vivas e bem diferenciadas
    cores = [
        '#FF1744', '#D500F9', '#3D5AFE', '#00BFA5', '#FFC400', '#FF9100', '#FF6D00', '#DD2C00', '#C2185B', '#7B1FA2',
        '#1565C0', '#00695C', '#2E7D32', '#F57F17', '#FF6F00', '#E65100', '#BF360C', '#D84315', '#E64A19', '#FF5722',
        '#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50', '#8BC34A',
        '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800', '#FF5722', '#795548', '#607D8B', '#9E9E9E', '#F44336', '#E91E63',
        '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50', '#8BC34A', '#CDDC39'
    ]
    
    # Função para gerar cor baseada no hash do nome do projeto
    def gerar_cor_projeto(nome_projeto):
        """Gera uma cor consistente baseada no hash do nome do projeto"""
        # Criar hash do nome do projeto
        hash_obj = hashlib.md5(nome_projeto.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        # Usar os primeiros 6 caracteres do hash para gerar índice
        hash_int = int(hash_hex[:6], 16)
        # Retornar cor baseada no hash
        return cores[hash_int % len(cores)]
    
    # Sistema para garantir cores únicas e bem diferenciadas
    projects_colors = {}
    if projeto:
        projeto_nome = projeto.get('nome', 'Projeto sem nome')
        # Usar índice sequencial para garantir cores únicas
        cor_escolhida = cores[0]  # Para um único projeto, usar a primeira cor
        projects_colors[projeto_nome] = cor_escolhida
    
    # Preparar dados para o gráfico Gantt
    gantt_geral_data = []
    for tarefa in tarefas:
        try:
            # Verificar se a tarefa tem as datas necessárias
            data_inicio = tarefa.get('data_inicio') or tarefa.get('data_inicio_tarefa')
            data_fim = tarefa.get('data_fim') or tarefa.get('data_fim_tarefa')
            
            if data_inicio and data_fim:
                # Garantir que todos os campos sejam strings válidas
                gantt_geral_data.append({
                    'id': str(tarefa.get('id', '')),
                    'name': str(tarefa.get('nome', '') or tarefa.get('titulo', '') or 'Tarefa sem nome'),
                    'start': str(data_inicio),
                    'end': str(data_fim),
                    'status': str(tarefa.get('status', 'pendente')),
                    'projeto_nome': str(projeto.get('nome', 'Projeto sem nome')),
                    'projeto_origem': str(projeto.get('nome', 'Projeto sem nome')),
                    'bar_color': str(projects_colors.get(projeto.get('nome', 'Projeto sem nome'), '#4ECDC4')),
                    'ordem': tarefa.get('ordem', 0)  # Adicionar campo ordem para ordenação
                })
        except Exception as e:
            print(f"Erro ao processar tarefa: {e}")
            continue
    
    # Verificar permissões do usuário
    restricoes = carregar_restricoes()
    usuario_id = session.get('user_id')
    restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
    
    # Verificar se é o usuário izak (por email ou por ID)
    is_izak = (session.get('user_email') == 'izak.gomes59@gmail.com' or 
               usuario_id == 'd0d784bd-f2bb-44b2-8096-5c10ec4d57be')
    
    # Se for o usuário izak, dar acesso total
    if is_izak:
        pode_criar_projeto = True
        pode_editar_projeto = True
        pode_excluir_projeto = True
        pode_criar_tarefa = True
        pode_editar_tarefa = True
        pode_excluir_tarefa = True
        pode_editar_responsavel = True
        pode_editar_duracao = True
        pode_editar_data_inicio = True
        pode_editar_data_termino = True
        pode_editar_predecessoras = True
        pode_editar_nome_tarefa = True
    else:
        # Definir permissões baseadas nas restrições para outros usuários
        pode_criar_projeto = not restricoes_usuario.get('restr_criar_projeto', False)
        pode_editar_projeto = not restricoes_usuario.get('restr_editar_projeto', False)
        pode_excluir_projeto = not restricoes_usuario.get('restr_excluir_projeto', False)
        pode_criar_tarefa = not restricoes_usuario.get('restr_criar_tarefa', False)
        pode_editar_tarefa = not restricoes_usuario.get('restr_editar_tarefa', False)
        pode_excluir_tarefa = not restricoes_usuario.get('restr_excluir_tarefa', False)
        pode_editar_responsavel = not restricoes_usuario.get('restr_editar_responsavel', False)
        pode_editar_duracao = not restricoes_usuario.get('restr_editar_duracao', False)
        pode_editar_data_inicio = not restricoes_usuario.get('restr_editar_datas', False)
        pode_editar_data_termino = not restricoes_usuario.get('restr_editar_datas', False)
        pode_editar_predecessoras = not restricoes_usuario.get('restr_editar_predecessoras', False)
        pode_editar_nome_tarefa = not restricoes_usuario.get('restr_editar_nome_tarefa', False)
    
    # Criar dicionário com todas as variáveis para debug
    template_vars = {
        'projeto': projeto,
        'tarefas': tarefas,
        'projects_colors': projects_colors,
        'gantt_geral_data': gantt_geral_data,
        'pode_criar_projeto': pode_criar_projeto,
        'pode_editar_projeto': pode_editar_projeto,
        'pode_excluir_projeto': pode_excluir_projeto,
        'pode_criar_tarefa': pode_criar_tarefa,
        'pode_editar_tarefa': pode_editar_tarefa,
        'pode_excluir_tarefa': pode_excluir_tarefa,
        'pode_editar_responsavel': pode_editar_responsavel,
        'pode_editar_duracao': pode_editar_duracao,
        'pode_editar_data_inicio': pode_editar_data_inicio,
        'pode_editar_data_termino': pode_editar_data_termino,
        'pode_editar_predecessoras': pode_editar_predecessoras,
        'pode_editar_nome_tarefa': pode_editar_nome_tarefa
    }
    
    return render_template('detalhes_projeto.html', **template_vars)

@main_bp.route('/projetos/editar/<uuid:projeto_id>', methods=['GET', 'POST'])
@login_required
@funcionalidade_restrita('restr_editar_projeto')
def editar_projeto(projeto_id):
    """Edita um projeto existente"""
    # Buscar o projeto
    try:
        projeto_resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
        if not projeto:
            flash("Projeto não encontrado.")
            return redirect('/projetos')
    except Exception as e:
        flash(f"Erro ao buscar projeto: {str(e)}")
        return redirect('/projetos')

    if request.method == 'POST':
        nome = request.form['nome']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        descricao = normaliza_opcional(request.form.get('descricao'))
        tipo_id = request.form.get('tipo_id')
        
        # Validação
        if not nome:
            flash("Nome do projeto é obrigatório!")
            return render_template('editar_projeto.html', projeto=projeto, tipos=tipos)
        
        try:
            # Atualizar projeto
            projeto_data = {
                "nome": nome,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "descricao": descricao,
                "tipo_id": tipo_id
            }
            
            resp = supabase.table("projetos").update(projeto_data).eq("id", str(projeto_id)).execute()
            
            if resp.data:
                flash("Projeto atualizado com sucesso!")
                return redirect(f'/projetos/{projeto_id}')
            else:
                flash(f"Erro ao atualizar projeto: {resp}")
        except Exception as e:
            flash(f"Erro ao atualizar projeto: {str(e)}")
            print(f"Erro ao atualizar projeto: {e}")
    
    # Buscar tipos disponíveis (pastas)
    try:
        print(f"[DEBUG] Buscando pastas para usuário: {session['user_id']}")
        tipos_resp = supabase.table("pastas").select("id, nome").eq("usuario_id", session['user_id']).order("nome").execute()
        tipos = tipos_resp.data if hasattr(tipos_resp, 'data') else []
        print(f"[DEBUG] Pastas encontradas: {tipos}")
    except Exception as e:
        print(f"Erro ao buscar pastas: {e}")
        tipos = []
    
    return render_template('editar_projeto.html', projeto=projeto, tipos=tipos)

@main_bp.route('/projetos/excluir/<uuid:projeto_id>', methods=['POST'])
@login_required
@funcionalidade_restrita('restr_excluir_projeto')
def excluir_projeto(projeto_id):
    """Exclui um projeto"""
    # Buscar o projeto para verificar se pertence ao usuário
    try:
        projeto_resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).eq("usuario_id", session['user_id']).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
        if not projeto:
            flash("Projeto não encontrado ou você não tem permissão para excluí-lo.")
            return redirect('/projetos')
    except Exception as e:
        flash(f"Erro ao buscar projeto: {str(e)}")
        return redirect('/projetos')

    try:
        # Excluir tarefas do projeto primeiro
        supabase.table("tarefas").delete().eq("projeto_id", str(projeto_id)).execute()
        
        # Excluir projeto
        resp = supabase.table("projetos").delete().eq("id", str(projeto_id)).execute()
        
        if resp.data:
            flash("Projeto excluído com sucesso!")
        else:
            flash("Erro ao excluir projeto.")
    except Exception as e:
        flash(f"Erro ao excluir projeto: {str(e)}")
    
    return redirect('/projetos') 

@main_bp.route('/notificacoes/<user_id>')
@login_required
def notificacoes(user_id):
    """Rota para buscar notificações do usuário"""
    try:
        # Por enquanto, retornar notificações vazias
        return jsonify({
            'notificacoes': [],
            'total': 0
        })
    except Exception as e:
        return jsonify({
            'notificacoes': [],
            'total': 0,
            'error': str(e)
        }), 500

@main_bp.route('/notificacoes/<notif_id>/ler', methods=['PATCH'])
@login_required
def marcar_notificacao_lida(notif_id):
    """Rota para marcar notificação como lida"""
    try:
        # Por enquanto, apenas retornar sucesso
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/notificacoes/<user_id>/limpar', methods=['DELETE'])
@login_required
def limpar_notificacoes(user_id):
    """Rota para limpar notificações do usuário"""
    try:
        # Por enquanto, apenas retornar sucesso
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 