from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita, is_admin_session, carregar_restricoes
from utils.validators import normaliza_opcional
from utils.email_notifications import (
    notificar_tarefa_designada, 
    notificar_tarefa_removida, 
    notificar_status_alterado,
    notificar_tarefa_concluida,
    notificar_tarefa_concluida_admin,
    notificar_tarefa_progresso_admin
)
from config.database import supabase, SUPABASE_URL, SUPABASE_KEY
import threading
import time
import requests
from datetime import datetime

# Criar blueprint para tarefas
tarefas_bp = Blueprint('tarefas', __name__)

def atualizar_status_notificacao_email(usuario_id, tipo, sucesso, erro_msg=None):
    """
    Atualiza o status de envio de email de uma notificação no banco de dados
    """
    try:
        update_data = {
            'email_tentativas': 1,  # Simplificado - sempre incrementa
        }

        if sucesso:
            update_data['email_enviado'] = True
            update_data['email_enviado_em'] = 'now()'
            update_data['email_erro'] = None
        else:
            update_data['email_enviado'] = False
            update_data['email_erro'] = erro_msg or 'Erro desconhecido'


        # Buscar a notificação mais recente do usuário com esse tipo
        notif_resp = supabase.table('notificacoes') \
            .select('id') \
            .eq('usuario_id', str(usuario_id)) \
            .eq('tipo', tipo) \
            .order('data_criacao', desc=True) \
            .limit(1) \
            .execute()

        if notif_resp.data and len(notif_resp.data) > 0:
            notif_id = notif_resp.data[0]['id']
            supabase.table('notificacoes').update(update_data).eq('id', notif_id).execute()
        else:
            print(f"[ERRO-STATUS] Nenhuma notificação encontrada para atualizar status do email (usuario_id={usuario_id}, tipo={tipo})")

    except Exception as e:
        print(f"[ERRO-STATUS] Falha ao atualizar status da notificação {tipo} para usuário {usuario_id}: {e}")

def processar_notificacoes_background(notificacoes_data):
    """
    Processa notificações em background para não bloquear a resposta da API
    Inclui logs detalhados para rastreamento de status
    """
    def _processar():
        try:
            # CARREGAR .ENV NO CONTEXTO DA THREAD E FORÇAR VARIÁVEIS
            try:
                from dotenv import load_dotenv
                import os
                load_dotenv(override=True)
                print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] .env carregado na thread")
                
                # FORÇAR DEFINIÇÃO DAS VARIÁVEIS DE AMBIENTE NA THREAD
                os.environ['SMTP_SERVER'] = 'webmail.dipaula.com.br'
                os.environ['SMTP_PORT'] = '465'
                os.environ['SMTP_USER'] = 'izak.oliveira@dipaula.com.br'
                os.environ['SMTP_PASS'] = 'Oli@2115'
                os.environ['FROM_NAME'] = 'Sistema de Gestão de Projetos'
                
                print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] Variáveis SMTP forçadas na thread")
                
                # RECRIAR INSTÂNCIA DO EMAIL NOTIFIER COM AS NOVAS VARIÁVEIS
                from utils.email_notifications import EmailNotifier
                global email_notifier
                email_notifier = EmailNotifier()
                print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] EmailNotifier recriado com variáveis forçadas")
                
            except Exception as e:
                print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] Erro ao configurar email: {e}")
                print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] Erro ao carregar .env: {e}")

            time.sleep(0.1)  # Pequena pausa para garantir que a transação principal foi commitada

            print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] Iniciando processamento de {len(notificacoes_data)} notificação(ões)")

            for i, notificacao in enumerate(notificacoes_data, 1):
                tipo = notificacao.get('tipo')
                usuario_id = notificacao.get('usuario_id')

                print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] Processando {i}/{len(notificacoes_data)}: {tipo} para usuário {usuario_id}")

                try:
                    if tipo == 'designacao':
                        # Notificação de nova tarefa designada
                        tarefa_info = notificacao.get('tarefa_info')
                        projeto_url = notificacao.get('projeto_url')

                        # Buscar dados do usuário
                        usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                        usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None

                        if usuario:
                            sucesso = notificar_tarefa_designada(
                                usuario['email'],
                                usuario['nome'],
                                tarefa_info,
                                projeto_url
                            )
                            atualizar_status_notificacao_email(usuario_id, 'designacao', sucesso)
                            if sucesso:
                                print(f"[BACKGROUND-✅] Email de designação enviado com sucesso para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                            else:
                                print(f"[BACKGROUND-❌] Falha ao enviar email de designação para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                        else:
                            print(f"[BACKGROUND-⚠️] Usuário {usuario_id} não encontrado para notificação de designação")

                    elif tipo == 'remocao':
                        # Notificação de tarefa removida
                        tarefa_info = notificacao.get('tarefa_info')

                        # Buscar dados do usuário
                        usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                        usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None

                        if usuario:
                            sucesso = notificar_tarefa_removida(
                                usuario['email'],
                                usuario['nome'],
                                tarefa_info
                            )
                            atualizar_status_notificacao_email(usuario_id, 'remocao', sucesso)
                            if sucesso:
                                print(f"[BACKGROUND-✅] Email de remoção enviado com sucesso para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                            else:
                                print(f"[BACKGROUND-❌] Falha ao enviar email de remoção para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                        else:
                            print(f"[BACKGROUND-⚠️] Usuário {usuario_id} não encontrado para notificação de remoção")

                    elif tipo == 'status_alterado':
                        # Notificação de status alterado
                        tarefa_info = notificacao.get('tarefa_info')
                        novo_status = notificacao.get('novo_status')
                        status_anterior = notificacao.get('status_anterior')
                        projeto_url = notificacao.get('projeto_url')

                        # Buscar dados do usuário
                        usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                        usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None

                        if usuario:
                            sucesso = notificar_status_alterado(
                                usuario['email'],
                                usuario['nome'],
                                tarefa_info,
                                novo_status,
                                status_anterior,
                                projeto_url
                            )
                            atualizar_status_notificacao_email(usuario_id, 'status_alterado', sucesso)
                            if sucesso:
                                print(f"[BACKGROUND-✅] Email de status alterado enviado com sucesso para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')} ({status_anterior} → {novo_status})")
                            else:
                                print(f"[BACKGROUND-❌] Falha ao enviar email de status alterado para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                        else:
                            print(f"[BACKGROUND-⚠️] Usuário {usuario_id} não encontrado para notificação de status alterado")

                    elif tipo == 'conclusao':
                        # Notificação de tarefa concluída
                        tarefa_info = notificacao.get('tarefa_info')
                        projeto_url = notificacao.get('projeto_url')

                        # Buscar dados do usuário
                        usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                        usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None

                        if usuario:
                            sucesso = notificar_tarefa_concluida(
                                usuario['email'],
                                usuario['nome'],
                                tarefa_info,
                                projeto_url
                            )
                            atualizar_status_notificacao_email(usuario_id, 'conclusao', sucesso)
                            if sucesso:
                                print(f"[BACKGROUND-✅] Email de conclusão enviado com sucesso para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                            else:
                                print(f"[BACKGROUND-❌] Falha ao enviar email de conclusão para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                        else:
                            print(f"[BACKGROUND-⚠️] Usuário {usuario_id} não encontrado para notificação de conclusão")

                    elif tipo == 'conclusao_admin':
                        # Notificação de tarefa concluída para administradores
                        tarefa_info = notificacao.get('tarefa_info')
                        usuario_alteracao = notificacao.get('usuario_alteracao', 'Sistema')
                        projeto_url = notificacao.get('projeto_url')

                        # Buscar dados do admin
                        usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                        usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None

                        if usuario:
                            # Usar template específico para admins com informação de quem concluiu
                            sucesso = notificar_tarefa_concluida_admin(
                                usuario['email'],
                                usuario['nome'],
                                tarefa_info,
                                usuario_alteracao,
                                projeto_url
                            )
                            atualizar_status_notificacao_email(usuario_id, 'conclusao_admin', sucesso)
                            if sucesso:
                                print(f"[BACKGROUND-✅] Email de conclusão (admin) enviado com sucesso para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')} (concluída por {usuario_alteracao})")
                            else:
                                print(f"[BACKGROUND-❌] Falha ao enviar email de conclusão (admin) para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                        else:
                            print(f"[BACKGROUND-⚠️] Admin {usuario_id} não encontrado para notificação de conclusão")

                    elif tipo == 'progresso_admin':
                        # Notificação de tarefa em progresso para administradores
                        tarefa_info = notificacao.get('tarefa_info')
                        usuario_alteracao = notificacao.get('usuario_alteracao', 'Sistema')
                        projeto_url = notificacao.get('projeto_url')

                        # Buscar dados do admin
                        usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                        usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None

                        if usuario:
                            # Usar template específico para admins com informação de quem iniciou o progresso
                            sucesso = notificar_tarefa_progresso_admin(
                                usuario['email'],
                                usuario['nome'],
                                tarefa_info,
                                usuario_alteracao,
                                projeto_url
                            )
                            atualizar_status_notificacao_email(usuario_id, 'progresso_admin', sucesso)
                            if sucesso:
                                print(f"[BACKGROUND-✅] Email de progresso (admin) enviado com sucesso para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')} (iniciada por {usuario_alteracao})")
                            else:
                                print(f"[BACKGROUND-❌] Falha ao enviar email de progresso (admin) para {usuario['email']} - Tarefa: {tarefa_info.get('nome', 'N/A')}")
                        else:
                            print(f"[BACKGROUND-⚠️] Admin {usuario_id} não encontrado para notificação de progresso")

                except Exception as e:
                    print(f"[BACKGROUND-💥] Erro ao processar notificação {tipo} para usuário {usuario_id}: {e}")

            print(f"[BACKGROUND-{time.strftime('%H:%M:%S')}] Processamento concluído - {len(notificacoes_data)} notificação(ões) processada(s)")

        except Exception as e:
            print(f"[BACKGROUND-💥] Erro geral no processamento de notificações em background: {e}")

    # Iniciar thread em background
    thread = threading.Thread(target=_processar, daemon=True)
    thread.start()

def usuario_tem_acesso_projeto(usuario_id, projeto_id):
    """Verifica se um usuário tem acesso a um projeto (é dono ou tem permissão de visualização)"""
    try:
        # Verificar se é o dono do projeto
        projeto_resp = supabase.table("projetos").select("usuario_id").eq("id", str(projeto_id)).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
        
        if projeto and str(projeto.get('usuario_id')) == str(usuario_id):
            return True
        
        # Verificar se tem permissão de visualização
        permissao_resp = supabase.table("projetos_usuarios_visiveis").select("*").eq("projeto_id", str(projeto_id)).eq("usuario_id", str(usuario_id)).execute()
        if permissao_resp.data:
            return True
        
        return False
    except Exception as e:
        print(f"Erro ao verificar acesso do usuário ao projeto: {e}")
        return False

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
        usuario_id = normaliza_opcional(request.form.get('usuario_id'))
        status = request.form.get('status', 'pendente')
        colecao = normaliza_opcional(request.form.get('colecao'))
        # Se coleção não foi fornecida, usar o nome do projeto como padrão
        if not colecao:
            colecao = projeto.get('nome', '')
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

    # Carregar restrições do usuário
    restricoes = carregar_restricoes()
    usuario_id_sessao = session.get('user_id')
    restricoes_usuario = restricoes.get(str(usuario_id_sessao), {}) if usuario_id_sessao else {}

    if request.method == 'POST':
        # Verificar se é uma requisição JSON
        is_json_request = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_json_request:
            data = request.get_json() or {}
            print(f"[DEBUG] Dados JSON recebidos: {data}")
            nome = data.get('nome', '')
            data_inicio = data.get('data_inicio', '')
            data_fim = data.get('data_fim', '')
            duracao = normaliza_opcional(data.get('duracao'))
            usuario_id = normaliza_opcional(data.get('usuario_id'))
            status = data.get('status', 'pendente')
            colecao = normaliza_opcional(data.get('colecao'))
            predecessoras = normaliza_opcional(data.get('predecessoras'))
            # Para JSON, se o campo não foi enviado, preservar o valor existente
            if 'colecao' not in data:
                colecao = tarefa.get('colecao') if tarefa else None
            if 'predecessoras' not in data:
                predecessoras = tarefa.get('predecessoras') if tarefa else None
            if 'duracao' not in data:
                duracao = tarefa.get('duracao') if tarefa else None
            if 'usuario_id' not in data:
                usuario_id = tarefa.get('usuario_id') if tarefa else None
        else:
            # Dados de formulário - preservar valores existentes se campos vierem vazios
            nome = request.form.get('nome', '')
            data_inicio = request.form.get('data_inicio', '')
            data_fim = request.form.get('data_fim', '')
            duracao = normaliza_opcional(request.form.get('duracao'))
            usuario_id = normaliza_opcional(request.form.get('usuario_id'))
            status = request.form.get('status', 'pendente')
            # Para colecao, preservar valor existente se vier vazio
            colecao_form = request.form.get('colecao', '').strip()
            colecao = colecao_form if colecao_form else (tarefa.get('colecao') if tarefa else None)
            predecessoras = normaliza_opcional(request.form.get('predecessoras'))
        
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

            # Verificar permissão para alterar o status baseado nas restrições
            pode_alterar_status = False
            try:
                tarefa_existente_resp = supabase.table("tarefas").select("usuario_id").eq("id", str(tarefa_id)).single().execute()
                tarefa_existente = tarefa_existente_resp.data if hasattr(tarefa_existente_resp, 'data') else None
            except Exception:
                tarefa_existente = None

            usuario_id_sessao = session.get('user_id')
            if is_admin_session():
                pode_alterar_status = True
            else:
                restrito_status = restricoes_usuario.get('restr_editar_status_tarefa', False)
                if restrito_status:
                    # Apenas tarefas próprias
                    if tarefa_existente and tarefa_existente.get('usuario_id') and usuario_id_sessao and str(tarefa_existente.get('usuario_id')) == str(usuario_id_sessao):
                        pode_alterar_status = True
                else:
                    # Pode alterar status de qualquer tarefa
                    pode_alterar_status = True

            # Montar payload base
            tarefa_data = {
                "nome": nome,
            }
            # Só incluir status se houver permissão
            if pode_alterar_status:
                tarefa_data["status"] = status
            
            # Sempre incluir todos os campos, mesmo que vazios (para permitir limpeza)
            tarefa_data["data_inicio"] = data_inicio if data_inicio else None
            tarefa_data["data_fim"] = data_fim if data_fim else None
            tarefa_data["duracao"] = duracao if duracao else None
            tarefa_data["usuario_id"] = usuario_id if usuario_id else None
            tarefa_data["colecao"] = colecao if colecao else None
            tarefa_data["predecessoras"] = predecessoras if predecessoras else None
            
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
                        # Preparar dados para notificações em background
                        notificacoes_background = []
                        
                        # Novo responsável
                        if usuario_id:
                            try:
                                novo_usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                                novo_usuario = novo_usuario_resp.data if hasattr(novo_usuario_resp, 'data') else None
                                
                                if novo_usuario:
                                    # Verificar se o usuário tem acesso ao projeto antes de notificar
                                    if usuario_tem_acesso_projeto(usuario_id, projeto_id_ref):
                                        # Notificação no sistema (síncrona)
                                        supabase.table('notificacoes').insert({
                                            'usuario_id': str(usuario_id),
                                            'mensagem': f"Você foi designado para a tarefa '{nome_tarefa_ref or nome}'",
                                            'tipo': 'designacao',
                                            'projeto_id': str(projeto_id_ref)
                                        }).execute()
                                        
                                        # Preparar notificação por email para background
                                        tarefa_info = {
                                            'nome': nome_tarefa_ref or nome,
                                            'projeto_nome': projeto_nome,
                                            'data_inicio': data_inicio or 'Não definida',
                                            'data_fim': data_fim or 'Não definida',
                                            'duracao': duracao or 'Não definida',
                                            'colecao': colecao or 'Não definida'
                                        }
                                        
                                        notificacoes_background.append({
                                            'tipo': 'designacao',
                                            'usuario_id': usuario_id,
                                            'tarefa_info': tarefa_info,
                                            'projeto_url': projeto_url
                                        })
                                    else:
                                        print(f"[INFO] Notificação NÃO enviada: usuário {usuario_id} não tem acesso ao projeto {projeto_id_ref}")
                            except Exception as e:
                                print(f"Erro ao preparar notificação para novo responsável: {e}")
                        
                        # Usuário anterior (sempre que houver mudança)
                        if old_usuario_id and old_usuario_id != usuario_id:
                            try:
                                antigo_usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(old_usuario_id)).single().execute()
                                antigo_usuario = antigo_usuario_resp.data if hasattr(antigo_usuario_resp, 'data') else None
                                
                                if antigo_usuario:
                                    # Verificar se o usuário tinha acesso ao projeto antes de notificar
                                    if usuario_tem_acesso_projeto(old_usuario_id, projeto_id_ref):
                                        # Notificação no sistema (síncrona)
                                        supabase.table('notificacoes').insert({
                                            'usuario_id': str(old_usuario_id),
                                            'mensagem': f"Você foi removido da tarefa '{nome_tarefa_ref or nome}'",
                                            'tipo': 'remocao',
                                            'projeto_id': str(projeto_id_ref)
                                        }).execute()
                                        
                                        # Preparar notificação por email para background
                                        tarefa_info = {
                                            'nome': nome_tarefa_ref or nome,
                                            'projeto_nome': projeto_nome
                                        }
                                        
                                        notificacoes_background.append({
                                            'tipo': 'remocao',
                                            'usuario_id': old_usuario_id,
                                            'tarefa_info': tarefa_info
                                        })
                                    else:
                                        print(f"[INFO] Notificação de remoção NÃO enviada: usuário {old_usuario_id} não tem acesso ao projeto {projeto_id_ref}")
                            except Exception as e:
                                print(f"Erro ao preparar notificação para usuário removido: {e}")
                        
                        # Iniciar processamento de notificações em background
                        if notificacoes_background:
                            processar_notificacoes_background(notificacoes_background)
                    
                    # Status alterado
                    if pode_alterar_status and status and status != old_status:
                        destinatario_status = usuario_id or old_usuario_id
                        if destinatario_status:
                            try:
                                # Buscar dados do usuário
                                usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(destinatario_status)).single().execute()
                                usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None
                                
                                if usuario:
                                    # Verificar se o usuário tem acesso ao projeto antes de notificar
                                    if usuario_tem_acesso_projeto(destinatario_status, projeto_id_ref):
                                        # Notificação no sistema (síncrona)
                                        supabase.table('notificacoes').insert({
                                            'usuario_id': str(destinatario_status),
                                            'mensagem': f"Status da tarefa '{nome_tarefa_ref or nome}' atualizado para '{status}'",
                                            'tipo': 'conclusao' if status == 'concluída' else 'status',
                                            'projeto_id': str(projeto_id_ref)
                                        }).execute()
                                        
                                        # Preparar notificação por email para background
                                        tarefa_info = {
                                            'nome': nome_tarefa_ref or nome,
                                            'projeto_nome': projeto_nome
                                        }
                                        
                                        notificacao_status = {
                                            'tipo': 'status_alterado',
                                            'usuario_id': destinatario_status,
                                            'tarefa_info': tarefa_info,
                                            'novo_status': status,
                                            'status_anterior': old_status,
                                            'projeto_url': projeto_url
                                        }
                                        
                                        # Processar em background
                                        processar_notificacoes_background([notificacao_status])
                                    else:
                                        print(f"[INFO] Notificação de status NÃO enviada: usuário {destinatario_status} não tem acesso ao projeto {projeto_id_ref}")
                            except Exception as e:
                                print(f"Erro ao preparar notificação de alteração de status: {e}")
                        
                        # Se o status mudou para "concluída" ou "em progresso", notificar também os administradores por email
                        if status in ['concluída', 'em progresso']:
                            try:
                                # Buscar lista de administradores
                                admins_resp = supabase.table("usuarios_admin").select("usuario_id").execute()
                                admin_ids = [a['usuario_id'] for a in admins_resp.data] if admins_resp.data else []
                                
                                # Buscar nome do usuário que fez a alteração
                                usuario_alteracao = "Sistema"
                                try:
                                    usuario_resp = supabase.table("usuarios").select("nome").eq("id", str(session.get('user_id'))).single().execute()
                                    usuario_alteracao = usuario_resp.data.get('nome', 'Usuário') if hasattr(usuario_resp, 'data') and usuario_resp.data else 'Usuário'
                                except Exception:
                                    pass
                                
                                # Preparar notificações por email para admins
                                notificacoes_admins = []
                                for admin_id in admin_ids:
                                    try:
                                        # Buscar dados do admin
                                        admin_resp = supabase.table("usuarios").select("nome, email").eq("id", str(admin_id)).single().execute()
                                        admin_data = admin_resp.data if hasattr(admin_resp, 'data') else None
                                        
                                        if admin_data:
                                            tarefa_info_admin = {
                                                'nome': nome_tarefa_ref or nome,
                                                'projeto_nome': projeto_nome
                                            }
                                            
                                            # Usar tipo específico baseado no status
                                            tipo_notificacao = 'conclusao_admin' if status == 'concluída' else 'progresso_admin'
                                            
                                            notificacao_admin = {
                                                'tipo': tipo_notificacao,
                                                'usuario_id': admin_id,
                                                'tarefa_info': tarefa_info_admin,
                                                'usuario_alteracao': usuario_alteracao,
                                                'projeto_url': projeto_url
                                            }
                                            
                                            notificacoes_admins.append(notificacao_admin)
                                            print(f"[INFO] Preparando notificação de {status} para admin {admin_id} ({admin_data.get('email', 'sem email')})")
                                    except Exception as e:
                                        print(f"[ERRO] Falha ao preparar notificação para admin {admin_id}: {e}")
                                
                                # Enviar notificações para admins em background
                                if notificacoes_admins:
                                    processar_notificacoes_background(notificacoes_admins)
                                    print(f"[INFO] {len(notificacoes_admins)} notificações de {status} enviadas para admins")
                            
                            except Exception as e:
                                print(f"[ERRO] Falha ao preparar notificações de {status} para admins: {e}")
                
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
    
    # Buscar usuários para o select de responsável (incluindo usuários simples)
    try:
        usuarios_resp = supabase.table("usuarios").select("id, nome, email").order("nome").execute()
        usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    except Exception as e:
        usuarios = []
    
    # Definir permissões de edição baseadas nas restrições do usuário
    usuario_id = session.get('user_id')
    restricoes = carregar_restricoes()
    restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
    
    if is_admin_session():
        pode_editar_data_inicio = True
        pode_editar_data_termino = True
    else:
        pode_editar_data_inicio = not restricoes_usuario.get('restr_editar_datas', False)
        pode_editar_data_termino = not restricoes_usuario.get('restr_editar_datas', False)
    
    return render_template('editar_tarefa.html', tarefa=tarefa, projeto=projeto, usuarios=usuarios, 
                          pode_editar_data_inicio=pode_editar_data_inicio, 
                          pode_editar_data_termino=pode_editar_data_termino)

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
            
            # Notificar administradores sobre alteração de status
            try:
                # Buscar lista de administradores
                admins_resp = supabase.table("usuarios_admin").select("usuario_id").execute()
                admin_ids = [a['usuario_id'] for a in admins_resp.data] if admins_resp.data else []
                
                # Buscar informações do projeto
                projeto_info = None
                try:
                    projeto_resp = supabase.table("projetos").select("nome").eq("id", str(tarefa.get('projeto_id'))).single().execute()
                    projeto_info = projeto_resp.data if hasattr(projeto_resp, 'data') else None
                except Exception:
                    pass
                projeto_nome = projeto_info.get('nome', 'Projeto') if projeto_info else 'Projeto'
                
                # Buscar nome do usuário que fez a alteração
                usuario_alteracao = None
                try:
                    usuario_resp = supabase.table("usuarios").select("nome").eq("id", str(session.get('user_id'))).single().execute()
                    usuario_alteracao = usuario_resp.data.get('nome', 'Usuário') if hasattr(usuario_resp, 'data') and usuario_resp.data else 'Usuário'
                except Exception:
                    usuario_alteracao = 'Usuário'
                
                # Criar notificação para cada administrador
                for admin_id in admin_ids:
                    try:
                        supabase.table('notificacoes').insert({
                            'usuario_id': str(admin_id),
                            'mensagem': f"Status da tarefa '{tarefa.get('nome','')}' alterado para '{novo_status}' por {usuario_alteracao} no projeto '{projeto_nome}'",
                            'tipo': 'status',
                            'projeto_id': str(tarefa.get('projeto_id'))
                        }).execute()
                        print(f"[INFO] Notificação enviada para admin {admin_id} sobre alteração de status da tarefa {tarefa_id}")
                    except Exception as e:
                        print(f"[ERRO] Falha ao notificar admin {admin_id}: {e}")
                        
            except Exception as e:
                print(f"[ERRO] Falha ao buscar administradores para notificação: {e}")
            
            # Notificação ao responsável
            try:
                usuario_id = tarefa.get('usuario_id')
                if usuario_id:
                    # Buscar dados do usuário responsável
                    usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", str(usuario_id)).single().execute()
                    usuario = usuario_resp.data if hasattr(usuario_resp, 'data') else None
                    if usuario:
                        # Verificar se o usuário tem acesso ao projeto antes de notificar
                        projeto_id = tarefa.get('projeto_id')
                        if usuario_tem_acesso_projeto(usuario_id, projeto_id):
                            # Buscar informações do projeto
                            projeto_info = None
                            try:
                                projeto_resp = supabase.table("projetos").select("nome").eq("id", str(projeto_id)).single().execute()
                                projeto_info = projeto_resp.data if hasattr(projeto_resp, 'data') else None
                            except Exception:
                                pass
                            projeto_nome = projeto_info.get('nome', 'Projeto') if projeto_info else 'Projeto'
                            projeto_url = f"http://localhost:5000/projetos/{projeto_id}"
                            # Notificação no sistema (síncrona)
                            supabase.table('notificacoes').insert({
                                'usuario_id': str(usuario_id),
                                'mensagem': f"Status da tarefa '{tarefa.get('nome','')}' atualizado para '{novo_status}'",
                                'tipo': 'conclusao' if novo_status == 'concluída' else 'status',
                                'projeto_id': str(projeto_id)
                            }).execute()
                            
                            # Preparar notificação por email para background
                            tarefa_info = {
                                'nome': tarefa.get('nome', ''),
                                'projeto_nome': projeto_nome
                            }
                            
                            if novo_status == 'concluída':
                                notificacao_tipo = 'conclusao'
                            else:
                                notificacao_tipo = 'status_alterado'
                            
                            notificacao_status = {
                                'tipo': notificacao_tipo,
                                'usuario_id': usuario_id,
                                'tarefa_info': tarefa_info,
                                'novo_status': novo_status,
                                'status_anterior': 'pendente',  # Status anterior padrão
                                'projeto_url': projeto_url
                            }
                            
                            # Processar em background
                            processar_notificacoes_background([notificacao_status])
                        else:
                            print(f"[INFO] Notificação de status NÃO enviada: usuário {usuario_id} não tem acesso ao projeto {projeto_id}")
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
            elif campo == 'usuario_id' and restricoes_usuario.get('restr_editar_responsavel', False):
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