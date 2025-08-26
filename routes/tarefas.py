from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita, is_admin_session, carregar_restricoes
from utils.validators import normaliza_opcional
from utils.email_notifications import (
    notificar_tarefa_designada, 
    notificar_tarefa_removida, 
    notificar_status_alterado,
    notificar_tarefa_concluida
)
from config.database import supabase, SUPABASE_URL, SUPABASE_KEY
import requests
from datetime import datetime

# Criar blueprint para tarefas
tarefas_bp = Blueprint('tarefas', __name__)

@tarefas_bp.route('/tarefas/criar/<uuid:projeto_id>', methods=['GET', 'POST'])
@login_required
def criar_tarefa(projeto_id):
    """Cria uma nova tarefa"""
    # Buscar projeto para checar dono
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
        duracao = normaliza_opcional(request.form.get('duracao'))
        responsavel = normaliza_opcional(request.form.get('responsavel'))
        status = request.form.get('status', 'pendente')
        colecao = normaliza_opcional(request.form.get('colecao'))
        predecessoras = normaliza_opcional(request.form.get('predecessoras'))
        
        # Validação básica
        if not nome:
            flash("Nome da tarefa é obrigatório!")
            return render_template('criar_tarefa.html', projeto=projeto)
        
        try:
            # Buscar ordem máxima atual
            tarefas_resp = supabase.table("tarefas").select("ordem").eq("projeto_id", str(projeto_id)).order("ordem", desc=True).limit(1).execute()
            nova_ordem = 1
            if tarefas_resp.data:
                nova_ordem = tarefas_resp.data[0]['ordem'] + 1
            
            # Criar tarefa
            tarefa_data = {
                "nome": nome,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "duracao": duracao,
                "responsavel": responsavel,
                "status": status,
                "colecao": colecao,
                "predecessoras": predecessoras,
                "projeto_id": str(projeto_id),
                "usuario_id": session['user_id'],
                "ordem": nova_ordem
            }
            
            resp = supabase.table("tarefas").insert(tarefa_data).execute()
            
            if resp.data:
                flash("Tarefa criada com sucesso!")
                return redirect(f'/projetos/{projeto_id}')
            else:
                flash(f"Erro ao criar tarefa: {resp}")
        except Exception as e:
            flash(f"Erro ao criar tarefa: {str(e)}")
            print(f"Erro ao criar tarefa: {e}")
    
    # Buscar usuários para o select de responsável
    try:
        usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
        usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    except Exception as e:
        usuarios = []
    
    return render_template('criar_tarefa.html', projeto=projeto, usuarios=usuarios)

@tarefas_bp.route('/tarefas/editar/<uuid:tarefa_id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(tarefa_id):
    """Edita uma tarefa existente"""
    # Buscar a tarefa
    try:
        tarefa_resp = supabase.table("tarefas").select("*").eq("id", str(tarefa_id)).single().execute()
        tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
        if not tarefa:
            flash("Tarefa não encontrada.")
            return redirect('/projetos')
    except Exception as e:
        flash(f"Erro ao buscar tarefa: {str(e)}")
        return redirect('/projetos')

    # Buscar projeto da tarefa
    try:
        projeto_resp = supabase.table("projetos").select("*").eq("id", tarefa['projeto_id']).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
    except Exception as e:
        projeto = None

    if request.method == 'POST':
        # Verificar se é uma requisição JSON
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json() or {}
            print(f"[DEBUG] Dados JSON recebidos: {data}")
            nome = data.get('nome', '')
            data_inicio = data.get('data_inicio', '')
            data_fim = data.get('data_fim', '')
            duracao = normaliza_opcional(data.get('duracao'))
            responsavel = normaliza_opcional(data.get('responsavel'))
            status = data.get('status', 'pendente')
            colecao = normaliza_opcional(data.get('colecao'))
            predecessoras = normaliza_opcional(data.get('predecessoras'))
            usuario_id = normaliza_opcional(data.get('usuario_id'))
        else:
            # Dados de formulário
            nome = request.form.get('nome', '')
            data_inicio = request.form.get('data_inicio', '')
            data_fim = request.form.get('data_fim', '')
            duracao = normaliza_opcional(request.form.get('duracao'))
            responsavel = normaliza_opcional(request.form.get('responsavel'))
            status = request.form.get('status', 'pendente')
            colecao = normaliza_opcional(request.form.get('colecao'))
            predecessoras = normaliza_opcional(request.form.get('predecessoras'))
            usuario_id = normaliza_opcional(request.form.get('usuario_id'))
        
        print(f"[DEBUG] Dados processados: nome={nome}, data_inicio={data_inicio}, data_fim={data_fim}, duracao={duracao}, status={status}")
        
        # Validação básica
        if not nome:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"sucesso": False, "erro": "Nome da tarefa é obrigatório!"}), 400
            else:
                flash("Nome da tarefa é obrigatório!")
                return render_template('editar_tarefa.html', tarefa=tarefa, projeto=projeto)
        
        try:
            # Capturar valores antigos para notificação
            old_usuario_id = tarefa.get('usuario_id') if tarefa else None
            old_status = tarefa.get('status') if tarefa else None
            projeto_id_ref = tarefa.get('projeto_id') if tarefa else None
            nome_tarefa_ref = tarefa.get('nome') if tarefa else ''

            # Verificar permissão para alterar o status: apenas o responsável (ou admin específico) pode
            pode_alterar_status = False
            try:
                tarefa_existente_resp = supabase.table("tarefas").select("usuario_id").eq("id", str(tarefa_id)).single().execute()
                tarefa_existente = tarefa_existente_resp.data if hasattr(tarefa_existente_resp, 'data') else None
            except Exception:
                tarefa_existente = None

            usuario_id_sessao = session.get('user_id')
            if is_admin_session():
                pode_alterar_status = True
            elif tarefa_existente and tarefa_existente.get('usuario_id') and usuario_id_sessao and str(tarefa_existente.get('usuario_id')) == str(usuario_id_sessao):
                pode_alterar_status = True

            # Montar payload base
            tarefa_data = {
                "nome": nome,
            }
            # Só incluir status se houver permissão
            if pode_alterar_status:
                tarefa_data["status"] = status
            
            # Adicionar campos opcionais apenas se não forem None
            if data_inicio:
                tarefa_data["data_inicio"] = data_inicio
            if data_fim:
                tarefa_data["data_fim"] = data_fim
            if duracao:
                tarefa_data["duracao"] = duracao
            if responsavel:
                tarefa_data["responsavel"] = responsavel
            if colecao:
                tarefa_data["colecao"] = colecao
            if predecessoras:
                tarefa_data["predecessoras"] = predecessoras
            # Sempre incluir usuario_id (pode ser None para remover designação)
            tarefa_data["usuario_id"] = usuario_id
            
            print(f"[DEBUG] Dados para atualização: {tarefa_data}")
            
            resp = supabase.table("tarefas").update(tarefa_data).eq("id", str(tarefa_id)).execute()
            
            if resp.data:
                # Notificações: designação/remocao de responsável e alteração de status
                try:
                    # Buscar informações do projeto para as notificações
                    projeto_info = None
                    try:
                        projeto_resp = supabase.table("projetos").select("nome").eq("id", str(projeto_id_ref)).single().execute()
                        projeto_info = projeto_resp.data if hasattr(projeto_resp, 'data') else None
                    except Exception:
                        pass
                    
                    projeto_nome = projeto_info.get('nome', 'Projeto') if projeto_info else 'Projeto'
                    projeto_url = f"http://localhost:5000/projetos/{projeto_id_ref}"  # Ajustar URL base conforme necessário
                    
                    # Responsável alterado (designação ou remoção)
                    if str(usuario_id) != str(old_usuario_id):
                        # Buscar dados do novo usuário
                        try:
                            novo_usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                            novo_usuario = novo_usuario_resp.data if hasattr(novo_usuario_resp, 'data') else None
                            
                            if novo_usuario:
                                # Notificação no sistema
                                supabase.table('notificacoes').insert({
                                    'usuario_id': str(usuario_id),
                                    'mensagem': f"Você foi designado para a tarefa '{nome_tarefa_ref or nome}'",
                                    'tipo': 'designacao',
                                    'projeto_id': str(projeto_id_ref)
                                }).execute()
                                
                                # Email para o novo responsável
                                tarefa_info = {
                                    'nome': nome_tarefa_ref or nome,
                                    'projeto_nome': projeto_nome,
                                    'data_inicio': data_inicio or 'Não definida',
                                    'data_fim': data_fim or 'Não definida',
                                    'duracao': duracao or 'Não definida',
                                    'colecao': colecao or 'Não definida'
                                }
                                notificar_tarefa_designada(
                                    novo_usuario['email'], 
                                    novo_usuario['nome'], 
                                    tarefa_info, 
                                    projeto_url
                                )
                        except Exception as e:
                            print(f"Erro ao notificar novo responsável: {e}")
                        
                        # Notificar usuário anterior se existir (sempre que houver mudança)
                        if old_usuario_id and old_usuario_id != usuario_id:
                            try:
                                antigo_usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(old_usuario_id)).single().execute()
                                antigo_usuario = antigo_usuario_resp.data if hasattr(antigo_usuario_resp, 'data') else None
                                
                                if antigo_usuario:
                                    # Notificação no sistema
                                    supabase.table('notificacoes').insert({
                                        'usuario_id': str(old_usuario_id),
                                        'mensagem': f"Você foi removido da tarefa '{nome_tarefa_ref or nome}'",
                                        'tipo': 'remocao',
                                        'projeto_id': str(projeto_id_ref)
                                    }).execute()
                                    
                                    # Email para o usuário removido
                                    tarefa_info = {
                                        'nome': nome_tarefa_ref or nome,
                                        'projeto_nome': projeto_nome
                                    }
                                    notificar_tarefa_removida(
                                        antigo_usuario['email'], 
                                        antigo_usuario['nome'], 
                                        tarefa_info
                                    )
                            except Exception as e:
                                print(f"Erro ao notificar usuário removido: {e}")
                    
                    # Status alterado
                    if pode_alterar_status and status and status != old_status:
                        destinatario_status = usuario_id or old_usuario_id
                        if destinatario_status:
                            try:
                                # Buscar dados do usuário
                                usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(destinatario_status)).single().execute()
                                usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None
                                
                                if usuario:
                                    # Notificação no sistema
                                    supabase.table('notificacoes').insert({
                                        'usuario_id': str(destinatario_status),
                                        'mensagem': f"Status da tarefa '{nome_tarefa_ref or nome}' atualizado para '{status}'",
                                        'tipo': 'conclusao' if status == 'concluída' else 'status',
                                        'projeto_id': str(projeto_id_ref)
                                    }).execute()
                                    
                                    # Email para o usuário
                                    tarefa_info = {
                                        'nome': nome_tarefa_ref or nome,
                                        'projeto_nome': projeto_nome
                                    }
                                    notificar_status_alterado(
                                        usuario['email'], 
                                        usuario['nome'], 
                                        tarefa_info, 
                                        status, 
                                        old_status, 
                                        projeto_url
                                    )
                            except Exception as e:
                                print(f"Erro ao notificar alteração de status: {e}")
                except Exception as e:
                    print(f"Erro geral nas notificações: {e}")
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"sucesso": True})
                else:
                    flash("Tarefa atualizada com sucesso!")
                    return redirect(f'/projetos/{tarefa["projeto_id"]}')
            else:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"sucesso": False, "erro": f"Erro ao atualizar tarefa: {resp}"}), 400
                else:
                    flash(f"Erro ao atualizar tarefa: {resp}")
        except Exception as e:
            print(f"[ERRO] Exceção ao atualizar tarefa: {e}")
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"sucesso": False, "erro": f"Erro ao atualizar tarefa: {str(e)}"}), 500
            else:
                flash(f"Erro ao atualizar tarefa: {str(e)}")
                print(f"Erro ao atualizar tarefa: {e}")
    
    # Buscar usuários para o select de responsável
    try:
        usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
        usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    except Exception as e:
        usuarios = []
    
    return render_template('editar_tarefa.html', tarefa=tarefa, projeto=projeto, usuarios=usuarios)

@tarefas_bp.route('/tarefas/excluir/<uuid:tarefa_id>', methods=['POST'])
@login_required
def excluir_tarefa(tarefa_id):
    """Exclui uma tarefa"""
    # Buscar a tarefa para obter o projeto_id
    try:
        tarefa_resp = supabase.table("tarefas").select("projeto_id").eq("id", str(tarefa_id)).single().execute()
        tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
        if not tarefa:
            flash("Tarefa não encontrada.")
            return redirect('/projetos')
    except Exception as e:
        flash(f"Erro ao buscar tarefa: {str(e)}")
        return redirect('/projetos')

    # Excluir tarefa via API REST
    url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(url, headers=headers)
        print("[DEBUG] Status code DELETE tarefa:", response.status_code)
        print("[DEBUG] Resposta DELETE tarefa:", response.text)
        
        if response.status_code in [200, 204]:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"sucesso": True})
            else:
                flash("Tarefa excluída com sucesso!")
                return redirect(f'/projetos/{tarefa["projeto_id"]}')
        else:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"sucesso": False, "erro": f"Erro ao excluir a tarefa: {response.text}"}), 400
            else:
                flash(f"Erro ao excluir a tarefa: {response.text}")
                return redirect(f'/projetos/{tarefa["projeto_id"]}')
    except Exception as e:
        print("[ERRO] Exceção ao tentar excluir tarefa:", e)
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"sucesso": False, "erro": f"Erro ao excluir a tarefa: {str(e)}"}), 500
        else:
            flash(f"Erro ao excluir a tarefa: {str(e)}")
            return redirect(f'/projetos/{tarefa["projeto_id"]}')

@tarefas_bp.route('/tarefas/concluir/<uuid:tarefa_id>', methods=['POST'])
@login_required
def concluir_tarefa(tarefa_id):
    """Marca uma tarefa como concluída"""
    # Buscar a tarefa para obter o projeto_id
    try:
        tarefa_resp = supabase.table("tarefas").select("projeto_id").eq("id", str(tarefa_id)).single().execute()
        tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
        if not tarefa:
            flash("Tarefa não encontrada.")
            return redirect('/projetos')
    except Exception as e:
        flash(f"Erro ao buscar tarefa: {str(e)}")
        return redirect('/projetos')

    try:
        # Atualizar status da tarefa
        resp = supabase.table("tarefas").update({"status": "concluída"}).eq("id", str(tarefa_id)).execute()
        
        if resp.data:
            flash("Tarefa marcada como concluída!")
        else:
            flash("Erro ao marcar tarefa como concluída.")
    except Exception as e:
        flash(f"Erro ao marcar tarefa como concluída: {str(e)}")
    
    return redirect(f'/projetos/{tarefa["projeto_id"]}')

@tarefas_bp.route('/tarefas/status/<uuid:tarefa_id>/<novo_status>', methods=['POST'])
@login_required
def atualizar_status_tarefa(tarefa_id, novo_status):
    """Atualiza o status de uma tarefa"""
    # Buscar a tarefa para obter o projeto_id, nome, usuario_id
    try:
        tarefa_resp = supabase.table("tarefas").select("projeto_id, nome, usuario_id").eq("id", str(tarefa_id)).single().execute()
        tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
        if not tarefa:
            flash("Tarefa não encontrada.")
            return redirect('/projetos')
    except Exception as e:
        flash(f"Erro ao buscar tarefa: {str(e)}")
        return redirect('/projetos')

    try:
        # Permissão: somente responsável ou admin específico pode alterar
        usuario_id_sessao = session.get('user_id')
        if not is_admin_session():
            if not tarefa.get('usuario_id') or str(tarefa.get('usuario_id')) != str(usuario_id_sessao):
                flash("Você não tem permissão para alterar o status desta tarefa.")
                return redirect(f"/projetos/{tarefa['projeto_id']}")

        # Atualizar status da tarefa
        resp = supabase.table("tarefas").update({"status": novo_status}).eq("id", str(tarefa_id)).execute()
        
        if resp.data:
            flash(f"Status da tarefa atualizado para '{novo_status}'!")
            # Notificação ao responsável
            try:
                responsavel = tarefa.get('usuario_id')
                if responsavel:
                    # Buscar dados do usuário responsável
                    usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(responsavel)).single().execute()
                    usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None
                    
                    if usuario:
                        # Buscar informações do projeto
                        projeto_info = None
                        try:
                            projeto_resp = supabase.table("projetos").select("nome").eq("id", str(tarefa.get('projeto_id'))).single().execute()
                            projeto_info = projeto_resp.data if hasattr(projeto_resp, 'data') else None
                        except Exception:
                            pass
                        
                        projeto_nome = projeto_info.get('nome', 'Projeto') if projeto_info else 'Projeto'
                        projeto_url = f"http://localhost:5000/projetos/{tarefa.get('projeto_id')}"
                        
                        # Notificação no sistema
                        supabase.table('notificacoes').insert({
                            'usuario_id': str(responsavel),
                            'mensagem': f"Status da tarefa '{tarefa.get('nome','')}' atualizado para '{novo_status}'",
                            'tipo': 'conclusao' if novo_status == 'concluída' else 'status',
                            'projeto_id': str(tarefa.get('projeto_id'))
                        }).execute()
                        
                        # Email para o usuário
                        tarefa_info = {
                            'nome': tarefa.get('nome', ''),
                            'projeto_nome': projeto_nome
                        }
                        
                        if novo_status == 'concluída':
                            notificar_tarefa_concluida(
                                usuario['email'], 
                                usuario['nome'], 
                                tarefa_info, 
                                projeto_url
                            )
                        else:
                            notificar_status_alterado(
                                usuario['email'], 
                                usuario['nome'], 
                                tarefa_info, 
                                novo_status, 
                                'pendente',  # Status anterior padrão
                                projeto_url
                            )
            except Exception as e:
                print(f"Erro ao notificar responsável: {e}")
        else:
            flash("Erro ao atualizar status da tarefa.")
    except Exception as e:
        flash(f"Erro ao atualizar status da tarefa: {str(e)}")
    
    return redirect(f'/projetos/{tarefa["projeto_id"]}')

@tarefas_bp.route('/tarefas/atualizar-campo/<uuid:tarefa_id>', methods=['POST'])
@login_required
def atualizar_campo_tarefa(tarefa_id):
    """Atualiza um campo específico de uma tarefa via AJAX"""
    try:
        # Verificar se é uma requisição AJAX
        if not request.is_json:
            return jsonify({"success": False, "error": "Requisição deve ser JSON"}), 400
        
        data = request.get_json()
        campo = data.get('campo')
        valor = data.get('valor')
        
        if not campo:
            return jsonify({"success": False, "error": "Campo não especificado"}), 400
        
        # Buscar a tarefa para verificar permissões
        tarefa_resp = supabase.table("tarefas").select("projeto_id, usuario_id").eq("id", str(tarefa_id)).single().execute()
        tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
        
        if not tarefa:
            return jsonify({"success": False, "error": "Tarefa não encontrada"}), 404
        
        # Verificar permissões baseadas no campo
        restricoes = carregar_restricoes()
        usuario_id = session.get('user_id')
        restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
        
        # Verificar se é o usuário izak (acesso total)
        is_izak = (session.get('user_email') == 'izak.gomes59@gmail.com' or 
                   usuario_id == 'd0d784bd-f2bb-44b2-8096-5c10ec4d57be')
        
        if not is_izak:
            # Verificar permissões específicas
            if campo == 'nome' and restricoes_usuario.get('restr_editar_nome_tarefa', False):
                return jsonify({"success": False, "error": "Sem permissão para editar nome da tarefa"}), 403
            elif campo in ['data_inicio', 'data_fim'] and restricoes_usuario.get('restr_editar_datas', False):
                return jsonify({"success": False, "error": "Sem permissão para editar datas da tarefa"}), 403
            elif campo == 'duracao' and restricoes_usuario.get('restr_editar_duracao', False):
                return jsonify({"success": False, "error": "Sem permissão para editar duração da tarefa"}), 403
            elif campo == 'responsavel' and restricoes_usuario.get('restr_editar_responsavel', False):
                return jsonify({"success": False, "error": "Sem permissão para editar responsável da tarefa"}), 403
            elif campo == 'predecessoras' and restricoes_usuario.get('restr_editar_predecessoras', False):
                return jsonify({"success": False, "error": "Sem permissão para editar predecessoras da tarefa"}), 403
        
        # Preparar dados para atualização
        dados_atualizacao = {campo: valor}
        
        # Se for campo de data, converter para formato ISO se necessário
        if campo in ['data_inicio', 'data_fim'] and valor:
            try:
                # Se a data estiver no formato dd/mm/yyyy, converter para yyyy-mm-dd
                if '/' in valor:
                    data_obj = datetime.strptime(valor, '%Y-%m-%d')
                    dados_atualizacao[campo] = data_obj.strftime('%d/%m/%Y')
                else:
                    # Se já estiver no formato ISO, converter para dd/mm/yyyy
                    data_obj = datetime.strptime(valor, '%Y-%m-%d')
                    dados_atualizacao[campo] = data_obj.strftime('%d/%m/%Y')
            except ValueError:
                # Se não conseguir converter, usar o valor original
                pass
        
        # Atualizar a tarefa
        resp = supabase.table("tarefas").update(dados_atualizacao).eq("id", str(tarefa_id)).execute()
        
        if resp.data:
            return jsonify({"success": True, "message": f"Campo {campo} atualizado com sucesso"})
        else:
            return jsonify({"success": False, "error": "Erro ao atualizar tarefa"}), 500
            
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar campo da tarefa: {e}")
        return jsonify({"success": False, "error": f"Erro interno: {str(e)}"}), 500

@tarefas_bp.route('/tarefas/atualizar_ordem', methods=['POST'])
@login_required
def atualizar_ordem_tarefas():
    """Atualiza a ordem das tarefas via AJAX"""
    try:
        # Verificar se é uma requisição AJAX
        if not request.is_json:
            return jsonify({"success": False, "error": "Requisição deve ser JSON"}), 400
        
        data = request.get_json()
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({"success": False, "error": "Lista de IDs não fornecida"}), 400
        
        # Verificar se o usuário tem permissão para editar tarefas
        restricoes = carregar_restricoes()
        usuario_id = session.get('user_id')
        restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
        
        # Verificar se é o usuário izak (acesso total)
        is_izak = (session.get('user_email') == 'izak.gomes59@gmail.com' or 
                   usuario_id == 'd0d784bd-f2bb-44b2-8096-5c10ec4d57be')
        
        if not is_izak and restricoes_usuario.get('restr_editar_tarefa', False):
            return jsonify({"success": False, "error": "Sem permissão para editar tarefas"}), 403
        
        # Atualizar a ordem de cada tarefa
        for idx, tarefa_id in enumerate(ids):
            try:
                # Verificar se a tarefa pertence a um projeto do usuário ou se tem permissão
                tarefa_resp = supabase.table("tarefas").select("projeto_id, usuario_id").eq("id", str(tarefa_id)).single().execute()
                tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
                
                if not tarefa:
                    continue
                
                # Verificar permissões
                projeto_id = tarefa.get('projeto_id')
                if projeto_id:
                    # Verificar se é dono do projeto
                    projeto_resp = supabase.table("projetos").select("usuario_id").eq("id", str(projeto_id)).single().execute()
                    projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
                    
                    if projeto and str(projeto.get('usuario_id')) == str(usuario_id):
                        # É dono do projeto, pode editar
                        pass
                    else:
                        # Verificar se tem permissão de visualização
                        try:
                            permissao_resp = supabase.table("projetos_usuarios_visiveis").select("*").eq("projeto_id", str(projeto_id)).eq("usuario_id", str(usuario_id)).execute()
                            if not permissao_resp.data:
                                continue  # Pular esta tarefa se não tiver permissão
                        except Exception:
                            continue  # Pular esta tarefa se não tiver permissão
                
                # Atualizar a ordem da tarefa
                nova_ordem = idx + 1
                supabase.table("tarefas").update({"ordem": nova_ordem}).eq("id", str(tarefa_id)).execute()
                
            except Exception as e:
                print(f"Erro ao atualizar ordem da tarefa {tarefa_id}: {e}")
                continue
        
        return jsonify({"success": True, "message": "Ordem das tarefas atualizada com sucesso"})
        
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar ordem das tarefas: {e}")
        return jsonify({"success": False, "error": f"Erro interno: {str(e)}"}), 500

@tarefas_bp.route('/tarefas/atualizar_ordem_individual', methods=['POST'])
@login_required
def atualizar_ordem_individual():
    """Atualiza a ordem de uma tarefa individual via AJAX"""
    try:
        # Verificar se é uma requisição AJAX
        if not request.is_json:
            return jsonify({"sucesso": False, "erro": "Requisição deve ser JSON"}), 400
        
        data = request.get_json()
        tarefa_id = data.get('tarefa_id')
        nova_ordem = data.get('nova_ordem')
        
        if not tarefa_id or nova_ordem is None:
            return jsonify({"sucesso": False, "erro": "ID da tarefa e nova ordem são obrigatórios"}), 400
        
        # Validar que a nova ordem é um número positivo
        try:
            nova_ordem = int(nova_ordem)
            if nova_ordem < 1:
                return jsonify({"sucesso": False, "erro": "A ordem deve ser um número positivo"}), 400
        except (ValueError, TypeError):
            return jsonify({"sucesso": False, "erro": "A ordem deve ser um número válido"}), 400
        
        # Verificar se o usuário tem permissão para editar tarefas
        restricoes = carregar_restricoes()
        usuario_id = session.get('user_id')
        restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
        
        # Verificar se é o usuário izak (acesso total)
        is_izak = (session.get('user_email') == 'izak.gomes59@gmail.com' or 
                   usuario_id == 'd0d784bd-f2bb-44b2-8096-5c10ec4d57be')
        
        if not is_izak and restricoes_usuario.get('restr_editar_tarefa', False):
            return jsonify({"sucesso": False, "erro": "Sem permissão para editar tarefas"}), 403
        
        # Verificar se a tarefa existe e se o usuário tem permissão
        tarefa_resp = supabase.table("tarefas").select("projeto_id, usuario_id").eq("id", str(tarefa_id)).single().execute()
        tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
        
        if not tarefa:
            return jsonify({"sucesso": False, "erro": "Tarefa não encontrada"}), 404
        
        # Verificar permissões
        projeto_id = tarefa.get('projeto_id')
        if projeto_id:
            # Verificar se é dono do projeto
            projeto_resp = supabase.table("projetos").select("usuario_id").eq("id", str(projeto_id)).single().execute()
            projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
            
            if projeto and str(projeto.get('usuario_id')) == str(usuario_id):
                # É dono do projeto, pode editar
                pass
            else:
                # Verificar se tem permissão de visualização
                try:
                    permissao_resp = supabase.table("projetos_usuarios_visiveis").select("*").eq("projeto_id", str(projeto_id)).eq("usuario_id", str(usuario_id)).execute()
                    if not permissao_resp.data:
                        return jsonify({"sucesso": False, "erro": "Sem permissão para editar esta tarefa"}), 403
                except Exception:
                    return jsonify({"sucesso": False, "erro": "Sem permissão para editar esta tarefa"}), 403
        
        # Atualizar a ordem da tarefa
        resp = supabase.table("tarefas").update({"ordem": nova_ordem}).eq("id", str(tarefa_id)).execute()
        
        if resp.data:
            return jsonify({"sucesso": True, "message": "Ordem da tarefa atualizada com sucesso"})
        else:
            return jsonify({"sucesso": False, "erro": "Erro ao atualizar ordem da tarefa"}), 500
        
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar ordem individual da tarefa: {e}")
        return jsonify({"sucesso": False, "erro": f"Erro interno: {str(e)}"}), 500