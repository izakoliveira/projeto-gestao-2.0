from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita, carregar_restricoes, is_admin_session
from utils.validators import normaliza_opcional, is_mobile_device
from config.database import supabase
from datetime import datetime

# Criar blueprint para pastas
pastas_bp = Blueprint('pastas', __name__)

@pastas_bp.route('/pastas', methods=['GET', 'POST'])
@login_required
def listar_pastas():
    """Lista todas as pastas do usuário"""
    # Detectar se é mobile
    is_mobile = is_mobile_device(request.headers.get('User-Agent', ''))
    
    try:
        # Buscar pastas do usuário (tabela tipos_projeto)
        pastas_resp = supabase.table("tipos_projeto").select("*").order("nome").execute()
        pastas = pastas_resp.data if hasattr(pastas_resp, 'data') else []
        print(f"[DEBUG] Pastas encontradas: {pastas}")
    except Exception as e:
        flash(f"Erro ao buscar pastas: {str(e)}")
        pastas = []
        print(f"[ERRO] Erro ao buscar pastas: {e}")
    
    # Buscar projetos sem pasta
    try:
        projetos_sem_pasta_resp = supabase.table("projetos").select("*").eq("usuario_id", session['user_id']).is_("tipo_id", "null").execute()
        projetos_sem_pasta = projetos_sem_pasta_resp.data if hasattr(projetos_sem_pasta_resp, 'data') else []
    except Exception as e:
        projetos_sem_pasta = []
        print(f"[ERRO] Erro ao buscar projetos sem pasta: {e}")
    
    # Buscar projetos por pasta
    projetos_por_pasta = {}
    try:
        for pasta in pastas:
            projetos_resp = supabase.table("projetos").select("*").eq("usuario_id", session['user_id']).eq("tipo_id", pasta['id']).execute()
            projetos_por_pasta[pasta['id']] = projetos_resp.data if hasattr(projetos_resp, 'data') else []
    except Exception as e:
        print(f"[ERRO] Erro ao buscar projetos por pasta: {e}")
    
    # Verificar permissões
    restricoes = carregar_restricoes()
    usuario_id = session.get('user_id')
    restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
    
    # Admin tem acesso total
    if is_admin_session():
        pode_editar_projeto = True
        pode_excluir_projeto = True
    else:
        pode_editar_projeto = not restricoes_usuario.get('restr_editar_projeto', False)
        pode_excluir_projeto = not restricoes_usuario.get('restr_excluir_projeto', False)
    
    if is_mobile:
        return render_template('pastas_mobile.html', 
                             pastas=pastas, 
                             projetos_sem_pasta=projetos_sem_pasta,
                             projetos_por_pasta=projetos_por_pasta,
                             pode_editar_projeto=pode_editar_projeto,
                             pode_excluir_projeto=pode_excluir_projeto)
    else:
        return render_template('pastas.html', 
                             tipos=pastas, 
                             projetos_sem_pasta=projetos_sem_pasta,
                             projetos_por_pasta=projetos_por_pasta,
                             pode_editar_projeto=pode_editar_projeto,
                             pode_excluir_projeto=pode_excluir_projeto)

@pastas_bp.route('/pastas/criar', methods=['GET', 'POST'])
@login_required
def criar_pasta():
    """Cria uma nova pasta"""
    if request.method == 'POST':
        nome = request.form['nome']
        
        if not nome:
            flash("Nome da pasta é obrigatório!")
            return render_template('criar_pasta.html')
        
        try:
            pasta_data = {
                "nome": nome
            }
            
            resp = supabase.table("tipos_projeto").insert(pasta_data).execute()
            
            if resp.data:
                flash("Pasta criada com sucesso!")
                return redirect(url_for('pastas.listar_pastas'))
            else:
                flash(f"Erro ao criar pasta: {resp}")
        except Exception as e:
            flash(f"Erro ao criar pasta: {str(e)}")
            print(f"Erro ao criar pasta: {e}")
    
    return render_template('criar_pasta.html')

@pastas_bp.route('/pastas/editar/<uuid:pasta_id>', methods=['GET', 'POST'])
@login_required
def editar_pasta(pasta_id):
    """Edita uma pasta existente"""
    # Buscar a pasta
    try:
        pasta_resp = supabase.table("tipos_projeto").select("*").eq("id", str(pasta_id)).single().execute()
        pasta = pasta_resp.data if hasattr(pasta_resp, 'data') else None
        if not pasta:
            flash("Pasta não encontrada.")
            return redirect(url_for('pastas.listar_pastas'))
    except Exception as e:
        flash(f"Erro ao buscar pasta: {str(e)}")
        return redirect(url_for('pastas.listar_pastas'))

    if request.method == 'POST':
        nome = request.form['nome']
        
        if not nome:
            flash("Nome da pasta é obrigatório!")
            return render_template('editar_pasta.html', pasta=pasta)
        
        try:
            pasta_data = {
                "nome": nome
            }
            
            resp = supabase.table("tipos_projeto").update(pasta_data).eq("id", str(pasta_id)).execute()
            
            if resp.data:
                flash("Pasta atualizada com sucesso!")
                return redirect(url_for('pastas.listar_pastas'))
            else:
                flash(f"Erro ao atualizar pasta: {resp}")
        except Exception as e:
            flash(f"Erro ao atualizar pasta: {str(e)}")
            print(f"Erro ao atualizar pasta: {e}")
    
    return render_template('editar_pasta.html', pasta=pasta)

@pastas_bp.route('/pastas/excluir/<uuid:pasta_id>', methods=['POST'])
@login_required
def excluir_pasta(pasta_id):
    """Exclui uma pasta"""
    # Buscar a pasta para verificar se pertence ao usuário
    try:
        pasta_resp = supabase.table("tipos_projeto").select("*").eq("id", str(pasta_id)).single().execute()
        pasta = pasta_resp.data if hasattr(pasta_resp, 'data') else None
        if not pasta:
            flash("Pasta não encontrada ou você não tem permissão para excluí-la.")
            return redirect(url_for('pastas.listar_pastas'))
    except Exception as e:
        flash(f"Erro ao buscar pasta: {str(e)}")
        return redirect(url_for('pastas.listar_pastas'))

    try:
        # Excluir pasta
        resp = supabase.table("tipos_projeto").delete().eq("id", str(pasta_id)).execute()
        
        if resp.data:
            flash("Pasta excluída com sucesso!")
        else:
            flash("Erro ao excluir pasta.")
    except Exception as e:
        flash(f"Erro ao excluir pasta: {str(e)}")
    
    return redirect(url_for('pastas.listar_pastas')) 