// Arquivo renomeado para evitar conflito de importação. Usar apenas o admin.py da pasta routes/ principal.
from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, apenas_admin_izak, carregar_restricoes, salvar_restricoes
from config.database import supabase, SUPABASE_URL, SUPABASE_KEY
from supabase_client import create_simple_user
from utils.email_notifications import notificar_tarefa_designada
import json
import requests
import bcrypt

# Headers para requisições Supabase
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Criar blueprint para administração
admin_bp = Blueprint('admin', __name__)

def notificar_tarefas_pendentes_ao_liberar_acesso(usuario_id, projeto_id):
    """
    Notifica o usuário sobre tarefas onde ele é responsável quando o acesso ao projeto é liberado.
    Envia notificações apenas para tarefas onde ele já era responsável mas não tinha acesso ao projeto.
    """
    try:
        # Buscar dados do usuário
        usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
        usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None
        
        if not usuario:
            print(f"[INFO] Usuário {usuario_id} não encontrado para notificação")
            return
        
        # Buscar informações do projeto
        projeto_resp = supabase.table("projetos").select("nome").eq("id", str(projeto_id)).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
        
        if not projeto:
            print(f"[INFO] Projeto {projeto_id} não encontrado para notificação")
            return
        
        projeto_nome = projeto.get('nome', 'Projeto')
        projeto_url = f"http://localhost:5000/projetos/{projeto_id}"
        
        # Buscar tarefas onde o usuário é responsável neste projeto
        tarefas_resp = supabase.table("tarefas").select("*").eq("projeto_id", str(projeto_id)).eq("usuario_id", str(usuario_id)).execute()
        tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []
        
        if not tarefas:
            print(f"[INFO] Nenhuma tarefa pendente para notificar o usuário {usuario_id} no projeto {projeto_id}")
            return
        
        # Enviar notificação para cada tarefa
        tarefas_notificadas = 0
        for tarefa in tarefas:
            try:
                # Notificação no sistema
                supabase.table('notificacoes').insert({
                    'usuario_id': str(usuario_id),
                    'mensagem': f"Você foi designado para a tarefa '{tarefa.get('nome', '')}' no projeto '{projeto_nome}'",
                    'tipo': 'designacao',
                    'projeto_id': str(projeto_id)
                }).execute()
                
                # Email de notificação
                tarefa_info = {
                    'nome': tarefa.get('nome', ''),
                    'projeto_nome': projeto_nome,
                    'data_inicio': tarefa.get('data_inicio') or 'Não definida',
                    'data_fim': tarefa.get('data_fim') or 'Não definida',
                    'duracao': tarefa.get('duracao') or 'Não definida',
                    'colecao': tarefa.get('colecao') or 'Não definida'
                }
                
                notificar_tarefa_designada(
                    usuario['email'],
                    usuario['nome'],
                    tarefa_info,
                    projeto_url
                )
                
                tarefas_notificadas += 1
            except Exception as e:
                print(f"[ERRO] Erro ao notificar tarefa {tarefa.get('id')}: {e}")
        
        if tarefas_notificadas > 0:
            print(f"[INFO] {tarefas_notificadas} notificação(ões) enviada(s) ao usuário {usuario_id} sobre tarefas no projeto {projeto_id}")
    
    except Exception as e:
        print(f"[ERRO] Erro ao processar notificações pendentes: {e}")

@admin_bp.route('/admin/restricoes', methods=['GET', 'POST'])
@apenas_admin_izak
@login_required
def admin_restricoes():
    """Página de administração de restrições"""
    # Verificar se é uma requisição AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
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
                                
                                # Notificar usuário sobre tarefas pendentes no projeto
                                notificar_tarefas_pendentes_ao_liberar_acesso(usuario_id, pid)
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
                        
                        # Notificar usuário sobre tarefas pendentes no projeto
                        notificar_tarefas_pendentes_ao_liberar_acesso(usuario_id, projeto_id)
                    
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

@admin_bp.route('/admin/usuarios_simples', methods=['GET', 'POST'])
@apenas_admin_izak
@login_required
def gerenciar_usuarios_simples():
    """Gerenciar usuários simples (apenas nome, para designar tarefas)"""
    
    if request.method == 'POST':
        acao = request.form.get('acao')
        
        if acao == 'criar':
            nome = request.form.get('nome', '').strip()
            if not nome:
                flash('Nome é obrigatório para criar um usuário simples.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            # Verificar se já existe um usuário com este nome
            try:
                usuarios_resp = supabase.table("usuarios").select("id, nome").ilike("nome", f"{nome}").execute()
                if usuarios_resp.data:
                    flash('Já existe um usuário com este nome.')
                    return redirect(url_for('admin.gerenciar_usuarios_simples'))
            except Exception as e:
                print(f"Erro ao verificar usuário existente: {e}")
            
            # Criar usuário simples
            try:
                novo_usuario = create_simple_user(nome)
                if novo_usuario:
                    flash(f'Usuário simples "{nome}" criado com sucesso!')
                    
                    # Adicionar restrições padrão para o novo usuário (se tiver ID)
                    if novo_usuario.get('id'):
                        try:
                            restricoes = carregar_restricoes()
                            restricoes_padrao = {
                                'nome': nome,
                                'email': None,
                                'restr_criar_projeto': True,  # Usuários simples não podem criar projetos
                                'restr_editar_projeto': True,  # Usuários simples não podem editar projetos
                                'restr_excluir_projeto': True,  # Usuários simples não podem excluir projetos
                                'restr_criar_tarefa': True,  # Usuários simples não podem criar tarefas
                                'restr_editar_tarefa': True,  # Usuários simples não podem editar tarefas
                                'restr_excluir_tarefa': True,  # Usuários simples não podem excluir tarefas
                                'restr_editar_responsavel': True,  # Usuários simples não podem alterar responsáveis
                                'restr_editar_duracao': True,  # Usuários simples não podem alterar duração
                                'restr_editar_datas': True,  # Usuários simples não podem alterar datas
                                'restr_editar_predecessoras': True,  # Usuários simples não podem alterar predecessoras
                                'restr_editar_nome_tarefa': True  # Usuários simples não podem alterar nomes de tarefas
                            }
                            restricoes[str(novo_usuario['id'])] = restricoes_padrao
                            salvar_restricoes(restricoes)
                        except Exception as e:
                            print(f"Erro ao salvar restrições: {e}")
                else:
                    flash('Erro ao criar usuário simples.')
            except Exception as e:
                print(f"Erro ao criar usuário simples: {e}")
                flash(f'Erro ao criar usuário: {str(e)}')
        
        elif acao == 'converter':
            usuario_id = request.form.get('usuario_id')
            email = request.form.get('email', '').strip()
            senha = request.form.get('senha', '').strip()
            confirmar_senha = request.form.get('confirmar_senha', '').strip()
            
            # Validações
            if not usuario_id or not email or not senha:
                flash('Todos os campos são obrigatórios.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            if senha != confirmar_senha:
                flash('As senhas não coincidem.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            if len(senha) < 6:
                flash('A senha deve ter no mínimo 6 caracteres.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            # Validar formato de email
            import re
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                flash('Email inválido.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            # Verificar se o email já está em uso
            try:
                usuarios_resp = supabase.table("usuarios").select("id").eq("email", email).execute()
                if usuarios_resp.data:
                    flash('Este email já está em uso por outro usuário.')
                    return redirect(url_for('admin.gerenciar_usuarios_simples'))
            except Exception as e:
                print(f"Erro ao verificar email: {e}")
            
            # Converter usuário
            try:
                # Gerar hash da senha usando o mesmo método do cadastro (Werkzeug/scrypt)
                from werkzeug.security import generate_password_hash
                senha_hash = generate_password_hash(senha)
                
                # Atualizar usuário no banco
                url = f"{SUPABASE_URL}/rest/v1/usuarios?id=eq.{usuario_id}"
                dados_update = {
                    'email': email,
                    'senha_hash': senha_hash
                }
                
                response = requests.patch(url, json=dados_update, headers=headers)
                
                if response.status_code in [200, 204]:
                    flash(f'Usuário convertido com sucesso! Email: {email}')
                    print(f"✓ Usuário {usuario_id} convertido para email: {email}")
                else:
                    flash(f'Erro ao converter usuário: {response.status_code}')
                    print(f"✗ Erro ao converter usuário: {response.text}")
            except Exception as e:
                flash(f'Erro ao converter usuário: {str(e)}')
                print(f"Exceção ao converter usuário: {e}")
        
        elif acao == 'redefinir_senha':
            usuario_id = request.form.get('usuario_id')
            nova_senha = request.form.get('nova_senha', '').strip()
            confirmar_nova_senha = request.form.get('confirmar_nova_senha', '').strip()
            
            # Validações
            if not usuario_id or not nova_senha:
                flash('Todos os campos são obrigatórios.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            if nova_senha != confirmar_nova_senha:
                flash('As senhas não coincidem.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            if len(nova_senha) < 6:
                flash('A senha deve ter no mínimo 6 caracteres.')
                return redirect(url_for('admin.gerenciar_usuarios_simples'))
            
            # Redefinir senha
            try:
                # Gerar hash da nova senha usando Werkzeug/scrypt
                from werkzeug.security import generate_password_hash
                nova_senha_hash = generate_password_hash(nova_senha)
                
                # Atualizar senha no banco
                url = f"{SUPABASE_URL}/rest/v1/usuarios?id=eq.{usuario_id}"
                dados_update = {
                    'senha_hash': nova_senha_hash
                }
                
                response = requests.patch(url, json=dados_update, headers=headers)
                
                if response.status_code in [200, 204]:
                    # Buscar nome do usuário para mensagem
                    usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", usuario_id).execute()
                    nome_usuario = usuario_resp.data[0]['nome'] if usuario_resp.data else 'Usuário'
                    
                    flash(f'Senha de "{nome_usuario}" redefinida com sucesso!')
                    print(f"✓ Senha do usuário {usuario_id} redefinida")
                else:
                    flash(f'Erro ao redefinir senha: {response.status_code}')
                    print(f"✗ Erro ao redefinir senha: {response.text}")
            except Exception as e:
                flash(f'Erro ao redefinir senha: {str(e)}')
                print(f"Exceção ao redefinir senha: {e}")
        
        elif acao == 'excluir':
            usuario_id = request.form.get('usuario_id')
            if usuario_id:
                try:
                    # Verificar se o usuário tem tarefas atribuídas
                    tarefas_resp = supabase.table("tarefas").select("id").eq("usuario_id", usuario_id).execute()
                    if tarefas_resp.data:
                        flash('Não é possível excluir usuário que possui tarefas atribuídas.')
                        return redirect(url_for('admin.gerenciar_usuarios_simples'))
                    
                    # Excluir usuário
                    resp = supabase.table("usuarios").delete().eq("id", usuario_id).execute()
                    
                    # Remover restrições do usuário
                    restricoes = carregar_restricoes()
                    if usuario_id in restricoes:
                        del restricoes[usuario_id]
                        salvar_restricoes(restricoes)
                    
                    flash('Usuário simples excluído com sucesso!')
                except Exception as e:
                    flash(f'Erro ao excluir usuário: {str(e)}')
        
        return redirect(url_for('admin.gerenciar_usuarios_simples'))
    
    # Buscar todos os usuários simples (incluindo os convertidos)
    try:
        # Buscar todos os usuários e filtrar os que não são admins
        usuarios_resp = supabase.table("usuarios").select("id, nome, email").order("nome").execute()
        todos_usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
        
        # Buscar lista de admins para excluir da listagem
        try:
            admins_resp = supabase.table("usuarios_admin").select("usuario_id").execute()
            admin_ids = [a['usuario_id'] for a in admins_resp.data] if admins_resp.data else []
        except:
            admin_ids = []
        
        # Filtrar: mostrar usuários simples E usuários convertidos (que não são admins)
        # Excluir apenas admins da listagem
        usuarios_simples = [u for u in todos_usuarios if u.get('id') not in admin_ids]
    except Exception as e:
        usuarios_simples = []
        flash(f"Erro ao buscar usuários: {str(e)}")
        print(f"Erro detalhado: {e}")
    
    return render_template('admin_usuarios_simples.html', usuarios_simples=usuarios_simples)