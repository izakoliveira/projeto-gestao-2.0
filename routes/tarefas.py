from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita
from utils.validators import normaliza_opcional
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
            # Atualizar tarefa
            tarefa_data = {
                "nome": nome,
                "status": status
            }
            
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
            if usuario_id:
                tarefa_data["usuario_id"] = usuario_id
            
            print(f"[DEBUG] Dados para atualização: {tarefa_data}")
            
            resp = supabase.table("tarefas").update(tarefa_data).eq("id", str(tarefa_id)).execute()
            
            if resp.data:
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
        # Atualizar status da tarefa
        resp = supabase.table("tarefas").update({"status": novo_status}).eq("id", str(tarefa_id)).execute()
        
        if resp.data:
            flash(f"Status da tarefa atualizado para '{novo_status}'!")
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