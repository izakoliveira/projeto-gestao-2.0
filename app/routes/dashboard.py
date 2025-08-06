"""
Rotas do Dashboard
==================
"""

from flask import Blueprint, render_template, session
from app.utils.auth import login_required
from app.config.database import get_supabase

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def index():
    """Dashboard principal"""
    usuario_id = session['user_id']
    usuario_email = session.get('user_email')
    supabase = get_supabase()
    
    # Admin vê todos os projetos
    if usuario_email == 'izak.gomes59@gmail.com':
        projetos_resp = supabase.table("projetos").select("*").execute()
        projetos = projetos_resp.data if hasattr(projetos_resp, 'data') else []
    else:
        # Usuário comum vê apenas projetos autorizados
        resp = supabase.table("projetos_usuarios_visiveis").select("projeto_id").eq("usuario_id", usuario_id).execute()
        projetos_ids_visiveis = [r['projeto_id'] for r in resp.data]
        if projetos_ids_visiveis:
            projetos = supabase.table("projetos").select("*").in_("id", projetos_ids_visiveis).execute().data
        else:
            projetos = []
    
    # Buscar estatísticas das tarefas
    tarefas_resp = supabase.table("tarefas").select("*").execute()
    tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []
    
    # Filtrar tarefas que pertencem aos projetos visíveis
    projeto_ids = [projeto['id'] for projeto in projetos]
    tarefas = [tarefa for tarefa in tarefas if tarefa.get('projeto_id') in projeto_ids]
    
    # Buscar informações dos projetos para as tarefas
    if tarefas:
        projeto_ids_tarefas = list(set([tarefa.get('projeto_id') for tarefa in tarefas if tarefa.get('projeto_id')]))
        if projeto_ids_tarefas:
            projetos_resp_tarefas = supabase.table("projetos").select("id, nome").in_("id", projeto_ids_tarefas).execute()
            projetos_dict = {projeto['id']: projeto for projeto in projetos_resp_tarefas.data}
            for tarefa in tarefas:
                if tarefa.get('projeto_id') and tarefa['projeto_id'] in projetos_dict:
                    tarefa['projetos'] = projetos_dict[tarefa['projeto_id']]
                else:
                    tarefa['projetos'] = None
    
    # Calcular estatísticas
    total_projetos = len(projetos)
    projetos_em_andamento = len([p for p in projetos if p.get('status') == 'em andamento'])
    total_tarefas = len(tarefas)
    tarefas_concluidas = len([t for t in tarefas if t.get('status') == 'concluída'])
    tarefas_pendentes = len([t for t in tarefas if t.get('status') == 'pendente'])
    tarefas_em_progresso = len([t for t in tarefas if t.get('status') == 'em progresso'])
    
    # Calcular percentual de conclusão
    percentual_conclusao = (tarefas_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0
    
    return render_template('dashboard.html',
                         total_projetos=total_projetos,
                         projetos_em_andamento=projetos_em_andamento,
                         total_tarefas=total_tarefas,
                         tarefas_concluidas=tarefas_concluidas,
                         tarefas_pendentes=tarefas_pendentes,
                         tarefas_em_progresso=tarefas_em_progresso,
                         percentual_conclusao=percentual_conclusao) 