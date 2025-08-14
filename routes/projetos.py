from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita
from utils.validators import validar_projeto, normaliza_opcional, verificar_tarefa_atrasada, contar_tarefas_atrasadas
from config.database import supabase, SUPABASE_URL, SUPABASE_KEY
import requests
from datetime import datetime

# Criar blueprint para projetos
projetos_bp = Blueprint('projetos', __name__)

@projetos_bp.route('/projetos', methods=['GET', 'POST'])
@login_required
def listar_projetos():
    """Lista todos os projetos com filtros"""
    usuario_id = session['user_id']
    nome_list = request.args.getlist('nome')  # Lista de nomes de projetos (múltiplo)
    tarefa_list = request.args.getlist('tarefa')  # Lista de nomes de tarefas (múltiplo)
    responsavel_list = request.args.getlist('responsavel')  # Lista de responsáveis (múltiplo)
    status_list = request.args.getlist('status')  # Lista de status (múltiplo)
    data_inicio = request.args.get('data_inicio', '')  # Data de início
    data_fim = request.args.get('data_fim', '')  # Data de término
    tipo_id = request.args.get('tipo_id', '')
    ambiente = request.args.get('ambiente', '')

    if session.get('user_email') == 'izak.gomes59@gmail.com':
        # Admin vê todos os projetos
        query = supabase.table("projetos").select("*")
        if nome_list:
            # Filtro múltiplo para nomes de projetos
            projetos_temp = query.execute().data
            projetos = []
            for projeto in projetos_temp:
                if any(nome.lower() in projeto['nome'].lower() for nome in nome_list):
                    projetos.append(projeto)
        else:
            projetos = query.execute().data
        # Aplicar outros filtros
        if data_inicio:
            projetos = [p for p in projetos if p.get('data_inicio', '') >= data_inicio]
        if data_fim:
            projetos = [p for p in projetos if p.get('data_fim', '') <= data_fim]
        if tipo_id:
            projetos = [p for p in projetos if p.get('tipo_id') == tipo_id]
        if ambiente:
            projetos = [p for p in projetos if p.get('tipo_id') == ambiente]
    else:
        # Usuário comum vê apenas projetos autorizados
        resp = supabase.table("projetos_usuarios_visiveis").select("projeto_id").eq("usuario_id", usuario_id).execute()
        projetos_ids_visiveis = [r['projeto_id'] for r in resp.data]
        if projetos_ids_visiveis:
            projetos = supabase.table("projetos").select("*").in_("id", projetos_ids_visiveis).execute().data
        else:
            projetos = []

    # Buscar tarefas dos projetos
    projeto_ids = [projeto['id'] for projeto in projetos]
    if projeto_ids:
        try:
            # Buscar tarefas dos projetos específicos
            tarefas_filtradas = []
            for projeto_id in projeto_ids:
                try:
                    # Buscar tarefas sem ordenação específica (será ordenada depois)
                    tarefas_projeto = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute()
                    if hasattr(tarefas_projeto, 'data') and tarefas_projeto.data:
                        tarefas_filtradas.extend(tarefas_projeto.data)
                except Exception as e:
                    print(f"Erro ao buscar tarefas do projeto {projeto_id}: {e}")
        except Exception as e:
            print(f"Erro ao buscar tarefas: {e}")
            tarefas_filtradas = []
        
        # Filtro de status (múltiplo) - igual ao coleção
        if status_list:
            tarefas_filtradas = [t for t in tarefas_filtradas if t.get('status') in status_list]
        
        # Filtro de colecao (múltiplo)
        colecao_list = request.args.getlist('colecao')
        if colecao_list:
            tarefas_filtradas = [t for t in tarefas_filtradas if t.get('colecao') in colecao_list]
        
        # Filtrar projetos que têm tarefas com os filtros aplicados (status e/ou coleção)
        if status_list or colecao_list:
            projetos_com_tarefa = set([t['projeto_id'] for t in tarefas_filtradas])
            projetos = [p for p in projetos if p['id'] in projetos_com_tarefa]
    else:
        projetos = []
        tarefas_filtradas = []

    # Limites de segurança para evitar travamento
    MAX_PROJETOS = 100
    MAX_TAREFAS = 200
    if len(projetos) > MAX_PROJETOS:
        projetos = projetos[:MAX_PROJETOS]
    if len(tarefas_filtradas) > MAX_TAREFAS:
        tarefas_filtradas = tarefas_filtradas[:MAX_TAREFAS]

    # Formatar datas dos projetos para dd/mm/aaaa
    for projeto in projetos:
        if projeto.get('data_inicio'):
            projeto['data_inicio'] = projeto['data_inicio'].split('T')[0] if 'T' in projeto['data_inicio'] else projeto['data_inicio']
        if projeto.get('data_fim'):
            projeto['data_fim'] = projeto['data_fim'].split('T')[0] if 'T' in projeto['data_fim'] else projeto['data_fim']

    # Buscar tipos de projeto
    try:
        tipos_response = supabase.table('tipos_projeto').select('id, nome').execute()
        tipos = tipos_response.data or []
    except Exception as e:
        print(f"Erro ao consultar tipos_projeto: {e}")
        tipos = []

    # Resolver nomes das pastas
    tipos = [t for t in tipos if t['nome'].lower() not in ['calendarios', 'tarefas diarias']]
    tipos_dict = {t['id']: t['nome'] for t in tipos}
    for projeto in projetos:
        projeto['tipo_nome'] = tipos_dict.get(projeto.get('tipo_id'), 'Sem pasta')

    # Detectar dispositivo mobile
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = any(keyword in user_agent.lower() for keyword in ['mobile', 'android', 'iphone', 'ipad'])

    # Determinar nome da pasta baseado no tipo selecionado
    tipo_id_selecionado = request.args.get('tipo_id')
    nome_pasta = 'Projetos'
    if tipo_id_selecionado:
        tipo_selecionado = next((t for t in tipos if str(t['id']) == tipo_id_selecionado), None)
        if tipo_selecionado:
            nome_pasta = tipo_selecionado['nome']
    
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
    cores_utilizadas = set()
    projetos_unicos = list(set([projeto.get('nome', 'Projeto sem nome') for projeto in projetos]))
    
    # Atribuir cores de forma sequencial para garantir unicidade
    for i, projeto_nome in enumerate(projetos_unicos):
        if projeto_nome not in projects_colors:
            # Usar índice sequencial para garantir cores únicas
            cor_escolhida = cores[i % len(cores)]
            projects_colors[projeto_nome] = cor_escolhida
            cores_utilizadas.add(cor_escolhida)
    
    # Verificar permissões do usuário
    pode_criar_projeto = True  # Por enquanto, sempre True
    pode_editar_projeto = True
    pode_excluir_projeto = True
    
    # Agrupar tarefas por projeto
    tarefas_por_projeto = {}
    for tarefa in tarefas_filtradas:
        projeto_id = tarefa.get('projeto_id')
        if projeto_id:
            if projeto_id not in tarefas_por_projeto:
                tarefas_por_projeto[projeto_id] = []
            tarefas_por_projeto[projeto_id].append(tarefa)
    
    # Gerar alertas de projetos baseado nas tarefas
    alertas_projetos = {}
    for projeto in projetos:
        projeto_id = projeto.get('id')
        tarefas_projeto = tarefas_por_projeto.get(projeto_id, [])
        
        # Contar tarefas por status
        tarefas_atrasadas = 0
        tarefas_pendentes = 0
        
        for tarefa in tarefas_projeto:
            # Verificar se está atrasada usando a função utilitária
            if verificar_tarefa_atrasada(tarefa):
                tarefas_atrasadas += 1
            
            # Contar pendentes
            status = tarefa.get('status', '').lower()
            if status in ['pendente', 'em progresso']:
                tarefas_pendentes += 1
        
        # Definir alerta baseado nas contagens
        if tarefas_atrasadas > 0:
            alertas_projetos[projeto_id] = {
                'tipo': 'atrasado',
                'quantidade': tarefas_atrasadas
            }
        elif tarefas_pendentes > 0:
            alertas_projetos[projeto_id] = {
                'tipo': 'pendente',
                'quantidade': tarefas_pendentes
            }
    
    # Adicionar tarefas aos projetos
    for projeto in projetos:
        projeto['tarefas'] = tarefas_por_projeto.get(projeto.get('id'), [])
    
    # Buscar tarefas_unicas para ordenar o Gantt
    try:
        tarefas_unicas = supabase.table('tarefas_unicas').select('nome, ordem').order('ordem').execute().data
    except Exception as e:
        tarefas_unicas = []
    
    # Criar dicionário de ordem das tarefas_unicas
    ordem_tarefas_unicas = {t['nome'].strip().lower(): t.get('ordem', 0) for t in tarefas_unicas}
    
    # Ordenar tarefas_filtradas conforme a ordem das tarefas_unicas
    def ordem_gantt(t):
        nome_tarefa = (t.get('nome') or '').strip().lower()
        return ordem_tarefas_unicas.get(nome_tarefa, 9999)
    
    tarefas_filtradas.sort(key=ordem_gantt)
    
    # Preparar dados para o gráfico Gantt
    gantt_geral_data = []
    for tarefa in tarefas_filtradas:
        try:
            # Verificar se a tarefa tem as datas necessárias
            data_inicio = tarefa.get('data_inicio') or tarefa.get('data_inicio_tarefa')
            data_fim = tarefa.get('data_fim') or tarefa.get('data_fim_tarefa')
            
            if data_inicio and data_fim:
                # Encontrar o nome do projeto para esta tarefa
                projeto_nome = 'Projeto não encontrado'
                for projeto in projetos:
                    if projeto.get('id') == tarefa.get('projeto_id'):
                        projeto_nome = projeto.get('nome', 'Projeto sem nome')
                        break
                
                # Garantir que todos os campos sejam strings válidas
                gantt_geral_data.append({
                    'id': str(tarefa.get('id', '')),
                    'name': str(tarefa.get('nome', '') or tarefa.get('titulo', '') or 'Tarefa sem nome'),
                    'start': str(data_inicio),
                    'end': str(data_fim),
                    'status': str(tarefa.get('status', 'pendente')),
                    'projeto_nome': str(projeto_nome),
                    'projeto_origem': str(projeto_nome),
                    'bar_color': str(projects_colors.get(projeto_nome, '#4ECDC4')),
                    'ordem': ordem_tarefas_unicas.get((tarefa.get('nome') or '').strip().lower(), 9999)  # Usar a ordem das tarefas_unicas
                })
        except Exception as e:
            print(f"Erro ao processar tarefa: {e}")
            continue

    if is_mobile:
        return render_template('projetos_gantt_mobile.html', 
                             projetos=projetos, 
                             tarefas_filtradas=tarefas_filtradas,
                             tipos=tipos,
                             nome_pasta=nome_pasta,
                             projects_colors=projects_colors,
                             pode_criar_projeto=pode_criar_projeto,
                             pode_editar_projeto=pode_editar_projeto,
                             pode_excluir_projeto=pode_excluir_projeto,
                             alertas_projetos=alertas_projetos,
                             gantt_geral_data=gantt_geral_data)
    else:
        return render_template('projetos_gantt_basico.html', 
                             projetos=projetos, 
                             tarefas_filtradas=tarefas_filtradas,
                             tipos=tipos,
                             nome_pasta=nome_pasta,
                             projects_colors=projects_colors,
                             pode_criar_projeto=pode_criar_projeto,
                             pode_editar_projeto=pode_editar_projeto,
                             pode_excluir_projeto=pode_excluir_projeto,
                             alertas_projetos=alertas_projetos,
                             gantt_geral_data=gantt_geral_data)

@projetos_bp.route('/projetos/criar', methods=['GET', 'POST'])
@login_required
@funcionalidade_restrita('restr_criar_projeto')
def criar_projeto():
    """Cria um novo projeto"""
    if request.method == 'POST':
        nome = request.form['nome']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        tipo_id = normaliza_opcional(request.form.get('tipo_id'))
        # Validação
        erro = validar_projeto(nome, data_inicio, data_fim)
        if erro:
            # Buscar tarefas_unicas para exibir no template em caso de erro
            try:
                tarefas_unicas = supabase.table('tarefas_unicas').select('*').order('ordem').execute().data
            except Exception as e:
                tarefas_unicas = []
            flash(erro)
            return render_template('novo_projeto.html', tipos=[], tarefas_unicas=tarefas_unicas)
        try:
            resp = supabase.table("projetos").insert({
                "nome": nome,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "tipo_id": tipo_id,
                "usuario_id": session['user_id']
            }).execute()
            if resp.data:
                flash("Projeto criado com sucesso!")
                return redirect('/projetos')
            else:
                flash(f"Erro ao criar o projeto: {resp}")
        except Exception as e:
            flash(f"Erro ao criar o projeto: {str(e)}")
            print(f"Erro ao criar o projeto: {e}")
    # Buscar tipos de projeto para o formulário
    try:
        tipos = supabase.table('tipos_projeto').select('*').execute().data
    except Exception as e:
        tipos = []
    # Buscar tarefas_unicas para exibir no formulário
    try:
        tarefas_unicas = supabase.table('tarefas_unicas').select('*').order('ordem').execute().data
    except Exception as e:
        tarefas_unicas = []
    return render_template('novo_projeto.html', tipos=tipos, tarefas_unicas=tarefas_unicas) 