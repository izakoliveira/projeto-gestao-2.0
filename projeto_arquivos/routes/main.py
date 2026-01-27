from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita, apenas_admin_izak, carregar_restricoes, is_admin_session
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
@main_bp.route('/projeto/<uuid:projeto_id>')  # Rota alternativa para compatibilidade
@login_required
def detalhes_projeto(projeto_id):
    # Gerar variáveis de cabeçalho do Gantt (meses e dias)
    from datetime import timedelta
    def gerar_meses_e_dias(tarefas):
        datas_inicio = [t.get('data_inicio_iso') for t in tarefas if t.get('data_inicio_iso')]
        datas_fim = [t.get('data_fim_iso') for t in tarefas if t.get('data_fim_iso')]
        if not datas_inicio or not datas_fim:
            return [], []
        data_inicio_min = min(datas_inicio)
        data_fim_max = max(datas_fim)
        # Converter para datetime
        data_inicio_dt = datetime.strptime(data_inicio_min, '%Y-%m-%d')
        data_fim_dt = datetime.strptime(data_fim_max, '%Y-%m-%d')
        dias = []
        meses = []
        data_atual = data_inicio_dt
        mes_corrente = None
        dias_mes = 0
        while data_atual <= data_fim_dt:
            dias.append(data_atual.strftime('%d'))
            nome_mes = data_atual.strftime('%b/%Y')
            if mes_corrente is None:
                mes_corrente = nome_mes
                dias_mes = 1
            elif nome_mes == mes_corrente:
                dias_mes += 1
            else:
                meses.append({'nome': mes_corrente, 'dias': dias_mes})
                mes_corrente = nome_mes
                dias_mes = 1
            data_atual += timedelta(days=1)
        if mes_corrente:
            meses.append({'nome': mes_corrente, 'dias': dias_mes})
        return meses, dias

    meses = []
    dias = []
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
    
    # Gerar meses e dias do Gantt após garantir que tarefas foi definida
    try:
        meses, dias = gerar_meses_e_dias(tarefas)
    except Exception:
        meses, dias = [], []
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
                    'name': str(tarefa.get('nome', '') or 'Tarefa sem nome'),
                    'start': str(data_inicio),
                    'end': str(data_fim),
                    'status': str(tarefa.get('status', 'pendente')),
                    'colecao': str(tarefa.get('colecao', '') or ''),
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
    
    # Verificar se é admin
    is_admin = is_admin_session()
    
    # Se for admin, dar acesso total
    if is_admin:
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
    
    # Buscar usuários para o select de responsável (incluindo usuários simples)
    # Buscar TODOS os usuários do sistema para permitir seleção completa
    try:
        usuarios_resp = supabase.table("usuarios").select("id, nome, email").order("nome").execute()
        usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    except Exception as e:
        print(f"Erro ao buscar usuarios: {e}")
        usuarios = []
    # Buscar usuários para o FILTRO (apenas responsáveis únicos das tarefas desse projeto)
    try:
        responsaveis_ids = list(set([t.get('usuario_id') for t in tarefas if t.get('usuario_id')]))
        if responsaveis_ids:
            usuarios_filtro_resp = supabase.table("usuarios").select("id, nome, email").in_("id", responsaveis_ids).order("nome").execute()
            usuarios_filtro = usuarios_filtro_resp.data if hasattr(usuarios_filtro_resp, 'data') else []
        else:
            usuarios_filtro = []
    except Exception as e:
        print(f"Erro ao buscar usuarios_filtro: {e}")
        usuarios_filtro = []
    # Criar dicionário com todas as variáveis para debug
    from utils.dias_uteis import dias_uteis_entre_datas, obter_feriados_banco, obter_feriados_ano
    # Buscar anos relevantes das tarefas
    anos_tarefas = set()
    for tarefa in tarefas:
        for campo in ['data_inicio_iso', 'data_fim_iso']:
            data = tarefa.get(campo)
            if data and len(data) >= 4:
                try:
                    ano = int(data[:4])
                    anos_tarefas.add(ano)
                except Exception:
                    pass
    if not anos_tarefas:
        anos_tarefas = {datetime.now().year}

    # Buscar feriados manuais do banco
    feriados_manuais = obter_feriados_banco()
    # Buscar feriados nacionais da API para os anos relevantes
    feriados_api = set()
    for ano in anos_tarefas:
        feriados_api.update(obter_feriados_ano(ano))
    feriados_api = list(feriados_api)

    # Cálculo de duração do projeto
    from datetime import datetime
    dias_corridos = None
    dias_uteis = None
    data_inicio_proj = projeto.get('data_inicio')
    data_fim_proj = projeto.get('data_fim')
    if data_inicio_proj and data_fim_proj:
        try:
            # Aceita formatos 'YYYY-MM-DD', 'DD/MM/YYYY' ou com 'T'
            if '/' in data_inicio_proj:
                data_inicio_dt = datetime.strptime(data_inicio_proj, '%d/%m/%Y')
            elif 'T' in data_inicio_proj:
                data_inicio_dt = datetime.strptime(data_inicio_proj.split('T')[0], '%Y-%m-%d')
            else:
                data_inicio_dt = datetime.strptime(data_inicio_proj, '%Y-%m-%d')
            if '/' in data_fim_proj:
                data_fim_dt = datetime.strptime(data_fim_proj, '%d/%m/%Y')
            elif 'T' in data_fim_proj:
                data_fim_dt = datetime.strptime(data_fim_proj.split('T')[0], '%Y-%m-%d')
            else:
                data_fim_dt = datetime.strptime(data_fim_proj, '%Y-%m-%d')
            dias_corridos = (data_fim_dt - data_inicio_dt).days + 1 if data_fim_dt >= data_inicio_dt else 0
            from utils.dias_uteis import dias_uteis_entre_datas
            dias_uteis = dias_uteis_entre_datas(data_inicio_dt.date(), data_fim_dt.date())
        except Exception as e:
            dias_corridos = None
            dias_uteis = None
    template_vars = {
        'projeto': projeto,
        'tarefas': tarefas,
        'usuarios': usuarios,
        'usuarios_filtro': usuarios_filtro,
        'projects_colors': projects_colors,
        'gantt_geral_data': gantt_geral_data,
        'is_admin': is_admin,
        'usuario_id': usuario_id,
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
        'pode_editar_nome_tarefa': pode_editar_nome_tarefa,
        'dias_uteis_entre_datas': dias_uteis_entre_datas,
        'meses': meses,
        'dias': dias,
        'feriados_manuais': feriados_manuais,
        'feriados_api': feriados_api,
        'dias_corridos': dias_corridos,
        'dias_uteis': dias_uteis
    }
    
    # Detectar se é dispositivo mobile
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = is_mobile_device(user_agent)
    
    # DEBUG: Log para verificar qual template está sendo usado
    print(f"[DEBUG] User-Agent: {user_agent}")
    print(f"[DEBUG] is_mobile: {is_mobile}")
    print(f"[DEBUG] Template escolhido: {'detalhes_projeto_mobile.html' if is_mobile else 'detalhes_projeto.html'}")
    
    # Escolher template baseado no dispositivo
    template_name = 'detalhes_projeto_mobile.html' if is_mobile else 'detalhes_projeto.html'
    
    return render_template(template_name, **template_vars)

@main_bp.route('/projetos/<uuid:projeto_id>/criar_tarefa_rapida', methods=['POST'])
@login_required
def criar_tarefa_rapida(projeto_id):
    """Cria uma tarefa rápida via AJAX"""
    try:
        # Verificar se é uma requisição AJAX
        if not request.is_json:
            return jsonify({"sucesso": False, "erro": "Requisição deve ser JSON"}), 400
        
        data = request.get_json()
        nome = data.get('nome', '').strip()
        predecessoras = data.get('predecessoras')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        status = data.get('status', 'pendente')
        usuario_id = data.get('usuario_id')
        duracao = data.get('duracao')
        
        if not nome:
            return jsonify({"sucesso": False, "erro": "Nome da tarefa é obrigatório"}), 400
        
        # Buscar projeto para verificar permissões
        projeto_resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).single().execute()
        projeto = projeto_resp.data if hasattr(projeto_resp, 'data') else None
        if not projeto:
            return jsonify({"sucesso": False, "erro": "Projeto não encontrado"}), 404
        
        # Verificar se o usuário tem permissão para criar tarefas neste projeto
        # (dono do projeto ou usuário com permissão de visualização)
        if str(projeto.get('usuario_id')) != str(session.get('user_id')):
            # Verificar se tem permissão de visualização
            try:
                permissao_resp = supabase.table("projetos_usuarios_visiveis").select("*").eq("projeto_id", str(projeto_id)).eq("usuario_id", str(session.get('user_id'))).execute()
                if not permissao_resp.data:
                    return jsonify({"sucesso": False, "erro": "Sem permissão para criar tarefas neste projeto"}), 403
            except Exception:
                return jsonify({"sucesso": False, "erro": "Sem permissão para criar tarefas neste projeto"}), 403
        
        # Buscar ordem máxima atual
        tarefas_resp = supabase.table("tarefas").select("ordem").eq("projeto_id", str(projeto_id)).order("ordem", desc=True).limit(1).execute()
        nova_ordem = 1
        if tarefas_resp.data:
            nova_ordem = tarefas_resp.data[0]['ordem'] + 1
        
        # Preparar dados da tarefa
        tarefa_data = {
            "nome": nome,
            "projeto_id": str(projeto_id),
            "usuario_id": session['user_id'],
            "ordem": nova_ordem,
            "status": status
        }
        
        # Adicionar campos opcionais se fornecidos
        if predecessoras:
            tarefa_data["predecessoras"] = predecessoras
        if data_inicio:
            tarefa_data["data_inicio"] = data_inicio
        if data_fim:
            tarefa_data["data_fim"] = data_fim
        if usuario_id:
            # CORRIGIDO: usar usuario_id em vez de responsavel (coluna não existe)
            tarefa_data["usuario_id"] = usuario_id
        if duracao:
            tarefa_data["duracao"] = duracao
        
        # Criar tarefa
        resp = supabase.table("tarefas").insert(tarefa_data).execute()
        
        if resp.data:
            nova_tarefa = resp.data[0]
            
            # Buscar usuários para gerar o select (incluindo usuários simples)
            try:
                usuarios_resp = supabase.table("usuarios").select("id, nome, email").order("nome").execute()
                usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
            except Exception as e:
                usuarios = []
            
            # Gerar opções do select de usuários
            opcoes_usuarios = '<option value="">Selecione</option>'
            for usuario in usuarios:
                # CORRIGIDO: usar usuario_id em vez de responsavel
                selected = 'selected' if nova_tarefa.get('usuario_id') == usuario['id'] else ''
                nome_display = usuario['nome']
                # Só mostrar email se não for usuário simples (não termina com @sistema.local)
                if usuario.get('email') and not usuario['email'].endswith('@sistema.local'):
                    nome_display += f" ({usuario['email']})"
                opcoes_usuarios += f'<option value="{usuario["id"]}" {selected}>{nome_display}</option>'
            
            # Gerar opções do select de status
            status_atual = nova_tarefa.get('status', 'pendente')
            opcoes_status = f'''
                <option value="pendente" {"selected" if status_atual == 'pendente' else ""}>Pendente</option>
                <option value="em progresso" {"selected" if status_atual == 'em progresso' else ""}>Em Progresso</option>
                <option value="concluída" {"selected" if status_atual == 'concluída' else ""}>Concluída</option>
            '''
            
            # Gerar HTML da nova linha para inserir na tabela
            html_linha = f'''
            <tr id="linha-tarefa-{nova_tarefa['id']}" data-id="{nova_tarefa['id']}">
                <td class="numero-tarefa">{nova_ordem}</td>
                <td>
                    <input type="text" name="nome" value="{nova_tarefa['nome']}" class="form-control form-control-sm" data-id="{nova_tarefa['id']}" data-original-value="{nova_tarefa['nome']}">
                </td>
                <td>
                    <input type="text" name="predecessoras" value="{nova_tarefa.get('predecessoras', '')}" class="form-control form-control-sm" data-original-value="{nova_tarefa.get('predecessoras', '')}">
                </td>
                <td>
                    <input type="date" name="data_inicio" value="{nova_tarefa.get('data_inicio', '')}" class="form-control form-control-sm" data-original-value="{nova_tarefa.get('data_inicio', '')}">
                </td>
                <td>
                    <input type="date" name="data_fim" value="{nova_tarefa.get('data_fim', '')}" class="form-control form-control-sm" data-original-value="{nova_tarefa.get('data_fim', '')}">
                </td>
                <td>
                    <select name="status" class="form-control form-control-sm" data-original-value="{nova_tarefa.get('status', 'pendente')}">
                        {opcoes_status}
                    </select>
                </td>
                <td>
                    <select name="usuario_id" class="form-control form-control-sm" data-original-value="{nova_tarefa.get('responsavel', '')}">
                        {opcoes_usuarios}
                    </select>
                </td>
                <td>
                    <input type="text" name="duracao" value="{nova_tarefa.get('duracao', '')}" class="form-control form-control-sm" data-original-value="{nova_tarefa.get('duracao', '')}">
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn btn-success" onclick="salvarLinhaTarefa(this)">
                            <i class="fas fa-save"></i>
                        </button>
                        <button type="button" class="btn btn-danger" onclick="excluirTarefa(this)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
            '''
            
            return jsonify({
                "sucesso": True,
                "mensagem": "Tarefa criada com sucesso",
                "html_linha": html_linha,
                "tarefa_id": nova_tarefa['id']
            })
        else:
            return jsonify({"sucesso": False, "erro": "Erro ao criar tarefa no banco de dados"}), 500
            
    except Exception as e:
        print(f"[ERRO] Erro ao criar tarefa rápida: {e}")
        return jsonify({"sucesso": False, "erro": f"Erro interno: {str(e)}"}), 500

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
            # Verificar se o nome do projeto mudou
            nome_anterior = projeto['nome']
            nome_mudou = nome_anterior != nome
            
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
                # Se o nome do projeto mudou, atualizar a coleção de todas as tarefas do projeto
                if nome_mudou:
                    try:
                        tarefas_resp = supabase.table("tarefas").update({"colecao": nome}).eq("projeto_id", str(projeto_id)).execute()
                        print(f"Coleção de {len(tarefas_resp.data) if tarefas_resp.data else 0} tarefas atualizada para '{nome}'")
                    except Exception as e:
                        print(f"Erro ao atualizar coleção das tarefas: {e}")
                        # Não falhar a operação se houver erro na atualização da coleção
                
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

@main_bp.route('/projetos/excluir/<projeto_id>', methods=['POST'])
@login_required
@funcionalidade_restrita('restr_excluir_projeto')
def excluir_projeto(projeto_id):
    """Exclui um projeto"""
    # Buscar o projeto para verificar se pertence ao usuário
    try:
        print(f"[EXCLUIR] Tentando buscar projeto {projeto_id} para usuário {session.get('user_id')}")
        projeto_resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).eq("usuario_id", session['user_id']).execute()
        projeto = projeto_resp.data[0] if hasattr(projeto_resp, 'data') and projeto_resp.data else None
        print(f"[EXCLUIR] Projeto encontrado: {projeto}")
        if not projeto:
            flash("Projeto não encontrado ou você não tem permissão para excluí-lo.")
            print(f"[EXCLUIR] Permissão negada ou projeto inexistente para {projeto_id}")
            return redirect('/projetos')
    except Exception as e:
        flash("Projeto não encontrado ou você não tem permissão para excluí-lo.")
        print(f"[EXCLUIR] Erro ao buscar projeto: {e}")
        return redirect('/projetos')

    try:
        # 1. Excluir notificações relacionadas ao projeto primeiro
        try:
            print(f"[EXCLUIR] Tentando excluir notificações do projeto {projeto_id}")
            del_notif_resp = supabase.table("notificacoes").delete() \
                .eq("projeto_id", str(projeto_id)) \
                .execute()
            print(f"[EXCLUIR] Exclusão de notificações resp: {getattr(del_notif_resp, 'data', None)}")
        except Exception as e_del_notif:
            print(f"[EXCLUIR] ERRO ao excluir notificações do projeto {projeto_id}: {e_del_notif}")
            # Prosseguir mesmo assim

        # 2. Excluir tarefas do projeto (respeitando RLS do usuário)
        try:
            print(f"[EXCLUIR] Tentando excluir tarefas do projeto {projeto_id}")
            del_tarefas_resp = supabase.table("tarefas").delete() \
                .eq("projeto_id", str(projeto_id)) \
                .eq("usuario_id", str(session['user_id'])) \
                .execute()
            print(f"[EXCLUIR] Exclusão de tarefas resp: {getattr(del_tarefas_resp, 'data', None)}")
        except Exception as e_del_tarefas:
            print(f"[EXCLUIR] ERRO ao excluir tarefas do projeto {projeto_id}: {e_del_tarefas}")
            # Prosseguir mesmo assim para tentar excluir o projeto; o RLS pode exigir ordem inversa

        # 3. Excluir projeto (restrito ao dono)
        print(f"[EXCLUIR] Tentando excluir projeto {projeto_id}")
        resp = supabase.table("projetos").delete() \
            .eq("id", str(projeto_id)) \
            .eq("usuario_id", str(session['user_id'])) \
            .execute()
        print(f"[EXCLUIR] Resposta exclusão projeto: {getattr(resp, 'data', None)}")

        if getattr(resp, 'data', None):
            flash("Projeto excluído com sucesso!")
            print(f"[EXCLUIR] Projeto {projeto_id} excluído com sucesso!")
        else:
            # Tentar obter mais contexto para o usuário
            flash("Erro ao excluir projeto. Verifique permissões ou registros dependentes.")
            print(f"[EXCLUIR] Falha ao excluir projeto {projeto_id}. Permissões ou dependências?")
    except Exception as e:
        flash(f"Erro ao excluir projeto: {str(e)}")
        print(f"[EXCLUIR] Erro ao excluir projeto: {e}")
    
    return redirect('/projetos') 

@main_bp.route('/notificacoes/<user_id>')
@login_required
def notificacoes(user_id):
    """Retorna notificações do usuário logado (ou admin pode ver qualquer)."""
    try:
        # Segurança básica: só o próprio usuário pode ver suas notificações
        if str(session.get('user_id')) != str(user_id) and not is_admin_session():
            return jsonify({'notificacoes': [], 'total': 0}), 403

        # Buscar notificações do Supabase
        resp = supabase.table('notificacoes') \
            .select('id, usuario_id, mensagem, tipo, lida, projeto_id, data_criacao') \
            .eq('usuario_id', str(user_id)) \
            .order('data_criacao', desc=True) \
            .execute()

        notificacoes = resp.data if hasattr(resp, 'data') and resp.data else []
        return jsonify({
            'notificacoes': notificacoes,
            'total': len(notificacoes)
        })
    except Exception as e:
        return jsonify({'notificacoes': [], 'total': 0, 'error': str(e)}), 500

@main_bp.route('/notificacoes/<notif_id>/ler', methods=['PATCH'])
@login_required
def marcar_notificacao_lida(notif_id):
    """Marca uma notificação como lida, validando pertença ao usuário."""
    try:
        # Verificar se a notificação pertence ao usuário logado (ou se é admin)
        notif_resp = supabase.table('notificacoes').select('usuario_id').eq('id', str(notif_id)).single().execute()
        notif = notif_resp.data if hasattr(notif_resp, 'data') else None
        if not notif:
            return jsonify({'error': 'Notificação não encontrada'}), 404
        if str(notif.get('usuario_id')) != str(session.get('user_id')) and not is_admin_session():
            return jsonify({'error': 'Sem permissão'}), 403

        upd = supabase.table('notificacoes').update({'lida': True}).eq('id', str(notif_id)).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/notificacoes/<user_id>/limpar', methods=['DELETE'])
@login_required
def limpar_notificacoes(user_id):
    """Remove todas as notificações do usuário (ou marca como lidas)."""
    try:
        if str(session.get('user_id')) != str(user_id) and not is_admin_session():
            return jsonify({'error': 'Sem permissão'}), 403
        # Opção 1: deletar
        supabase.table('notificacoes').delete().eq('usuario_id', str(user_id)).execute()
        # Opção 2 (alternativa): marcar como lidas
        # supabase.table('notificacoes').update({'lida': True}).eq('usuario_id', str(user_id)).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/feriados')
@login_required
@apenas_admin_izak
def gerenciar_feriados():
    """Página para gerenciar feriados manuais e mostrar feriados da API"""
    try:
        # Buscar feriados manuais via REST API para contornar RLS
        from supabase_client import SUPABASE_URL, headers
        url = f"{SUPABASE_URL}/rest/v1/feriados?order=data"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            todos_feriados = response.json()
            # Separar feriados manuais e da API
            feriados_manuais = [f for f in todos_feriados if f.get('tipo') != 'API']
            feriados_api_salvos = [f for f in todos_feriados if f.get('tipo') == 'API']
        else:
            feriados_manuais = []
            feriados_api_salvos = []

        # Buscar feriados da API do BrasilAPI para o ano atual (para mostrar disponíveis)
        from utils.dias_uteis import obter_feriados_ano_completos
        from datetime import datetime

        try:
            ano_atual = datetime.now().year
            feriados_api_disponiveis = obter_feriados_ano_completos(ano_atual)
        except Exception as e:
            print(f"Erro ao carregar feriados da API: {e}")
            feriados_api_disponiveis = []

        return render_template('feriados.html',
                             feriados_manuais=feriados_manuais,
                             feriados_api=feriados_api_salvos,
                             feriados_api_disponiveis=feriados_api_disponiveis,
                             ano_atual=ano_atual)
    except Exception as e:
        flash(f"Erro ao carregar feriados: {str(e)}")
        return render_template('feriados.html',
                             feriados_manuais=[],
                             feriados_api=[],
                             feriados_api_disponiveis=[],
                             ano_atual=datetime.now().year)

@main_bp.route('/feriados/adicionar', methods=['POST'])
@login_required
@apenas_admin_izak
def adicionar_feriado():
    """Adiciona um novo feriado manual"""
    try:
        data = request.form.get('data')
        nome = request.form.get('nome')
        tipo = request.form.get('tipo', 'manual')
        uf = request.form.get('uf', '')
        cidade = request.form.get('cidade', '')

        if not data or not nome:
            flash("Data e nome são obrigatórios")
            return redirect('/feriados')

        # Extrair ano da data
        ano = datetime.strptime(data, '%Y-%m-%d').year

        # Usar API REST diretamente para contornar RLS
        from supabase_client import SUPABASE_URL, headers

        dados_insercao = {
            'data': data,
            'nome': nome,
            'tipo': tipo,
            'uf': uf,
            'cidade': cidade,
            'ano': ano
        }

        # Inserir via REST API
        url = f"{SUPABASE_URL}/rest/v1/feriados"
        response = requests.post(url, json=dados_insercao, headers=headers)

        if response.status_code in [200, 201]:
            # Verificar se é uma requisição AJAX
            if request.headers.get('Content-Type') == 'application/json' or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Feriado adicionado com sucesso!'})

            flash("Feriado adicionado com sucesso!")
        else:
            if request.headers.get('Content-Type') == 'application/json' or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Erro ao adicionar feriado: {response.text}'})

            flash(f"Erro ao adicionar feriado: {response.text}")

        return redirect('/feriados')

    except Exception as e:
        # Verificar se é uma requisição AJAX
        if request.headers.get('Content-Type') == 'application/json' or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': f'Erro ao adicionar feriado: {str(e)}'})

        flash(f"Erro ao adicionar feriado: {str(e)}")
        return redirect('/feriados')

@main_bp.route('/feriados/<int:feriado_id>/excluir', methods=['POST'])
@login_required
@apenas_admin_izak
def excluir_feriado(feriado_id):
    """Exclui um feriado manual"""
    try:
        supabase.table('feriados').delete().eq('id', feriado_id).execute()

        # Verificar se é uma requisição AJAX
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'success': True, 'message': 'Feriado excluído com sucesso!'})

        flash("Feriado excluído com sucesso!")
        return redirect('/feriados')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'success': False, 'message': str(e)})

        flash(f"Erro ao excluir feriado: {str(e)}")
        return redirect('/feriados')

@main_bp.route('/feriados/<int:feriado_id>', methods=['PUT', 'POST'])
@login_required
@apenas_admin_izak
def editar_feriado(feriado_id):
    """Edita um feriado manual"""
    try:
        # Verificar se é uma requisição PUT simulada via POST
        if request.method == 'POST' and request.form.get('_method') == 'PUT':
            # Trata como PUT
            pass
        elif request.method != 'PUT':
            return jsonify({'success': False, 'message': 'Método não permitido'}), 405

        data = request.form.get('data')
        nome = request.form.get('nome')
        tipo = request.form.get('tipo', 'manual')
        uf = request.form.get('uf', '')
        cidade = request.form.get('cidade', '')

        if not data or not nome:
            return jsonify({'success': False, 'message': 'Data e nome são obrigatórios'})

        # Extrair ano da data
        ano = datetime.strptime(data, '%Y-%m-%d').year

        # Atualizar feriado
        dados_atualizacao = {
            'data': data,
            'nome': nome,
            'tipo': tipo,
            'uf': uf,
            'cidade': cidade,
            'ano': ano
        }

        supabase.table("feriados").update(dados_atualizacao).eq("id", feriado_id).execute()

        return jsonify({'success': True, 'message': 'Feriado atualizado com sucesso!'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/feriados/carregar_api/<int:ano>', methods=['POST'])
@login_required
@apenas_admin_izak
def carregar_feriados_api(ano):
    """Carrega feriados de um ano específico da API BrasilAPI e salva no banco"""
    try:
        print(f"[DEBUG] Iniciando carregamento de feriados para o ano {ano}")
        from utils.dias_uteis import obter_feriados_ano_completos
        from supabase_client import SUPABASE_URL, headers
        import requests

        # Buscar feriados da API
        print(f"[DEBUG] Carregando feriados da API para {ano}")
        feriados_api = obter_feriados_ano_completos(ano)
        print(f"[DEBUG] Feriados carregados da API: {len(feriados_api) if feriados_api else 0}")

        if not feriados_api:
            print(f"[DEBUG] Nenhum feriado carregado da API para {ano}")
            flash(f"Erro ao carregar feriados de {ano} da API BrasilAPI")
            return redirect('/feriados')

        # Verificar quais feriados já existem no banco para evitar duplicatas
        print(f"[DEBUG] Verificando feriados existentes no banco")
        url = f"{SUPABASE_URL}/rest/v1/feriados?select=data,nome"
        response = requests.get(url, headers=headers)
        feriados_existentes = []

        if response.status_code == 200:
            feriados_banco = response.json()
            feriados_existentes = [(f.get('data'), f.get('nome'), f.get('tipo')) for f in feriados_banco]
            print(f"[DEBUG] Feriados existentes no banco: {len(feriados_existentes)}")

        # Filtrar feriados que ainda não existem no banco
        feriados_para_salvar = []
        for feriado in feriados_api:
            data_feriado = feriado.get('date')
            nome_feriado = feriado.get('name')
            tipo_feriado = feriado.get('type', 'national')  # Usar o tipo da API

            # Mapear tipos da API para os tipos do sistema
            if tipo_feriado == 'national':
                tipo_sistema = 'nacional'
            elif tipo_feriado == 'state':
                tipo_sistema = 'estadual'
            elif tipo_feriado == 'municipal':
                tipo_sistema = 'municipal'
            else:
                tipo_sistema = 'nacional'  # fallback

            # Verificar se já existe (comparar data, nome e tipo)
            feriado_chave = (data_feriado, nome_feriado, tipo_sistema)
            if feriado_chave not in feriados_existentes:
                # Extrair ano da data
                ano_feriado = int(data_feriado.split('-')[0]) if data_feriado else ano
                feriados_para_salvar.append({
                    'data': data_feriado,
                    'nome': nome_feriado,
                    'tipo': tipo_sistema,  # Usar o tipo mapeado
                    'uf': None,
                    'cidade': None,
                    'ano': ano_feriado
                })

        print(f"[DEBUG] Feriados para salvar: {len(feriados_para_salvar)}")

        # Salvar os feriados no banco
        salvos = 0
        for feriado in feriados_para_salvar:
            try:
                print(f"[DEBUG] Salvando feriado: {feriado['nome']} - {feriado['data']}")
                url = f"{SUPABASE_URL}/rest/v1/feriados"
                response = requests.post(url, headers=headers, json=feriado)
                print(f"[DEBUG] Status do salvamento: {response.status_code}")
                if response.status_code == 201:
                    salvos += 1
                    print(f"[DEBUG] Feriado salvo com sucesso: {feriado['nome']}")
                else:
                    print(f"[DEBUG] Erro ao salvar {feriado['nome']}: {response.text}")
            except Exception as e:
                print(f"[DEBUG] Exceção ao salvar feriado {feriado['nome']}: {e}")

        print(f"[DEBUG] Total de feriados salvos: {salvos}")

        # Mensagem de sucesso
        if salvos > 0:
            flash(f"✅ {salvos} feriados de {ano} foram carregados e salvos com sucesso!")
        else:
            flash(f"ℹ️ Todos os feriados de {ano} já estavam cadastrados no sistema.")

        print(f"[DEBUG] Redirecionando para /feriados")
        return redirect('/feriados')

    except Exception as e:
        print(f"[DEBUG] Erro geral na função: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"❌ Erro ao carregar feriados da API: {str(e)}")
        return redirect('/feriados')