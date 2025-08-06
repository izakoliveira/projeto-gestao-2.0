from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, apenas_admin_izak, carregar_restricoes, salvar_restricoes
from config.database import supabase
import json

# Criar blueprint para administração
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/restricoes', methods=['GET', 'POST'])
@apenas_admin_izak
@login_required
def admin_restricoes():
    """Página de administração de restrições"""
    if request.method == 'POST':
        # Processar formulário de restrições
        restricoes = carregar_restricoes()
        
        # Verificar se é um formulário de visualização de projeto
        if request.form.get('form_tipo') == 'visualizacao_projeto':
            projeto_id = request.form.get('projeto_id')
            usuarios_selecionados = request.form.getlist('usuarios')
            
            if projeto_id and ',' in projeto_id:
                # Múltiplos projetos selecionados
                projeto_ids = projeto_id.split(',')
                for pid in projeto_ids:
                    pid = pid.strip()
                    if pid:
                        # Remover permissões existentes para este projeto
                        try:
                            supabase.table("projetos_usuarios_visiveis").delete().eq("projeto_id", pid).execute()
                        except Exception as e:
                            print(f"[ERRO] Erro ao remover permissões existentes para projeto {pid}: {e}")
                        
                        # Adicionar novas permissões
                        for usuario_id in usuarios_selecionados:
                            try:
                                supabase.table("projetos_usuarios_visiveis").insert({
                                    "projeto_id": pid,
                                    "usuario_id": usuario_id
                                }).execute()
                            except Exception as e:
                                print(f"[ERRO] Erro ao adicionar permissão para projeto {pid}, usuário {usuario_id}: {e}")
                
                flash(f"Permissões de visualização atualizadas para {len(projeto_ids)} projeto(s)!")
            elif projeto_id:
                # Apenas um projeto selecionado
                try:
                    # Remover permissões existentes
                    supabase.table("projetos_usuarios_visiveis").delete().eq("projeto_id", projeto_id).execute()
                    
                    # Adicionar novas permissões
                    for usuario_id in usuarios_selecionados:
                        supabase.table("projetos_usuarios_visiveis").insert({
                            "projeto_id": projeto_id,
                            "usuario_id": usuario_id
                        }).execute()
                    
                    flash("Permissões de visualização atualizadas com sucesso!")
                except Exception as e:
                    flash(f"Erro ao atualizar permissões: {str(e)}")
            
            return redirect(url_for('admin.admin_restricoes'))
        
        # Processar formulário de restrições (código existente)
        usuarios_selecionados = request.form.getlist('usuario_id')
        print(f"[DEBUG] Usuários selecionados no POST: {usuarios_selecionados}")
        
        # Buscar todos os usuários para obter informações
        try:
            usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
            usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
        except Exception as e:
            usuarios = []
            flash(f"Erro ao buscar usuários: {str(e)}")
        
        # Processar restrições apenas para os usuários selecionados
        for usuario_id in usuarios_selecionados:
            # Buscar informações do usuário
            usuario_info = next((u for u in usuarios if str(u['id']) == usuario_id), None)
            
            if usuario_info:
                if usuario_id not in restricoes:
                    restricoes[usuario_id] = {}
                
                # Atualizar restrições baseado no formulário
                restricoes[usuario_id].update({
                    'nome': usuario_info.get('nome', ''),
                    'email': usuario_info.get('email', ''),
                    'restr_criar_projeto': request.form.get('restr_criar_projeto') == 'on',
                    'restr_editar_projeto': request.form.get('restr_editar_projeto') == 'on',
                    'restr_excluir_projeto': request.form.get('restr_excluir_projeto') == 'on',
                    'restr_criar_tarefa': request.form.get('restr_criar_tarefa') == 'on',
                    'restr_editar_tarefa': request.form.get('restr_editar_tarefa') == 'on',
                    'restr_excluir_tarefa': request.form.get('restr_excluir_tarefa') == 'on',
                    'restr_editar_responsavel': request.form.get('restr_editar_responsavel') == 'on',
                    'restr_editar_duracao': request.form.get('restr_editar_duracao') == 'on',
                    'restr_editar_datas': request.form.get('restr_editar_datas') == 'on',
                    'restr_editar_predecessoras': request.form.get('restr_editar_predecessoras') == 'on',
                    'restr_editar_nome_tarefa': request.form.get('restr_editar_nome_tarefa') == 'on'
                })
                
                print(f"[DEBUG] Restrições atualizadas para {usuario_id}: {restricoes[usuario_id]}")
        
        # Salvar restrições
        try:
            salvar_restricoes(restricoes)
            flash("Restrições atualizadas com sucesso!")
        except Exception as e:
            flash(f"Erro ao salvar restrições: {str(e)}")
            print(f"[ERRO] Erro ao salvar restrições: {e}")
        
        return redirect(url_for('admin.admin_restricoes'))
    
    # Buscar todos os usuários
    try:
        usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
        usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    except Exception as e:
        usuarios = []
        flash(f"Erro ao buscar usuários: {str(e)}")
    
    # Buscar todos os projetos
    try:
        projetos_resp = supabase.table("projetos").select("id, nome").order("nome").execute()
        projetos = projetos_resp.data if hasattr(projetos_resp, 'data') else []
        print(f"[DEBUG] Projetos encontrados: {len(projetos)}")
        if projetos:
            print(f"[DEBUG] Primeiros 3 projetos: {[p['nome'] for p in projetos[:3]]}")
    except Exception as e:
        projetos = []
        flash(f"Erro ao buscar projetos: {str(e)}")
        print(f"[ERRO] Erro ao buscar projetos: {e}")
    
    # Buscar usuários visíveis para o projeto selecionado (se houver)
    usuarios_visiveis = []
    projeto_id = request.args.get('projeto_id')
    if projeto_id:
        # Se múltiplos projetos selecionados (separados por vírgula)
        if ',' in projeto_id:
            projeto_ids = projeto_id.split(',')
            todos_usuarios_visiveis = set()
            for pid in projeto_ids:
                try:
                    resp = supabase.table("projetos_usuarios_visiveis").select("usuario_id").eq("projeto_id", pid.strip()).execute()
                    usuarios_ids = [r['usuario_id'] for r in resp.data] if hasattr(resp, 'data') else []
                    todos_usuarios_visiveis.update(usuarios_ids)
                except Exception as e:
                    print(f"[ERRO] Erro ao buscar usuários visíveis para projeto {pid}: {e}")
            usuarios_visiveis = list(todos_usuarios_visiveis)
            print(f"[DEBUG] Usuários visíveis para projetos {projeto_ids}: {usuarios_visiveis}")
        else:
            # Apenas um projeto selecionado
            try:
                resp = supabase.table("projetos_usuarios_visiveis").select("usuario_id").eq("projeto_id", projeto_id).execute()
                usuarios_visiveis = [r['usuario_id'] for r in resp.data] if hasattr(resp, 'data') else []
                print(f"[DEBUG] Usuários visíveis para projeto {projeto_id}: {usuarios_visiveis}")
            except Exception as e:
                print(f"[ERRO] Erro ao buscar usuários visíveis: {e}")
    
    # Carregar restrições atuais
    restricoes = carregar_restricoes()
    
    # Buscar usuários selecionados
    usuario_id = request.args.getlist('usuario_id')
    
    print(f"[DEBUG] Usuários selecionados: {usuario_id}")
    print(f"[DEBUG] Restrições carregadas: {restricoes}")
    
    return render_template('admin_restricoes.html', usuarios=usuarios, restricoes=restricoes, usuario_id=usuario_id, projetos=projetos, usuarios_visiveis=usuarios_visiveis, projeto_id=projeto_id)

@admin_bp.route('/admin/usuarios_visiveis_projeto')
@apenas_admin_izak
@login_required
def usuarios_visiveis_projeto():
    """API para buscar usuários visíveis de um projeto"""
    projeto_id = request.args.get('projeto_id')
    if not projeto_id:
        return jsonify({"erro": "ID do projeto não fornecido"}), 400
    
    try:
        resp = supabase.table("projetos_usuarios_visiveis").select("usuario_id").eq("projeto_id", projeto_id).execute()
        usuarios_ids = [r['usuario_id'] for r in resp.data]
        
        if usuarios_ids:
            usuarios_resp = supabase.table("usuarios").select("id, nome, email").in_("id", usuarios_ids).execute()
            usuarios = usuarios_resp.data
        else:
            usuarios = []
        
        return jsonify({"usuarios": usuarios})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500 