from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from utils.auth import login_required, funcionalidade_restrita, is_admin_session
from utils.validators import validar_projeto, normaliza_opcional, verificar_tarefa_atrasada, contar_tarefas_atrasadas, normalizar
from config.database import supabase, SUPABASE_URL, SUPABASE_KEY
import requests
from datetime import datetime

# Criar blueprint para projetos
projetos_bp = Blueprint('projetos', __name__)


@projetos_bp.route('/projetos', methods=['GET', 'POST'])
@login_required
def listar_projetos():
    # (Bloco removido para evitar erro de variável não inicializada)
    """Lista todos os projetos com filtros"""
    usuario_id = session['user_id']
    # DEBUG: Mostrar SUPABASE_URL e SUPABASE_KEY para garantir ambiente
    print(f"[DEBUG] SUPABASE_URL: {SUPABASE_URL}")
    print(f"[DEBUG] SUPABASE_KEY: {SUPABASE_KEY[:10]}... (truncada)")
    nome_list = request.args.getlist('nome[]')  # Lista de nomes de projetos (múltiplo)
    tarefa_list = request.args.getlist('tarefa')  # Lista de nomes de tarefas (múltiplo)
    # responsavel_list = request.args.getlist('responsavel')  # REMOVIDO: coluna não existe
    status_list = request.args.getlist('status')  # Lista de status (múltiplo)
    data_inicio = request.args.get('data_inicio', '')  # Data de início
    data_fim = request.args.get('data_fim', '')  # Data de término
    tipo_id = request.args.get('tipo_id', '')
    ambiente = request.args.get('ambiente', '')

    if is_admin_session():
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
    print(f"[DEBUG] IDs dos projetos encontrados: {projeto_ids}")
    # Buscar tarefas dos projetos específicos
    tarefas_filtradas = []
    if projeto_ids:
        print(f"[DEBUG] status_list: {status_list}")
        print(f"[DEBUG] colecao_list: {request.args.getlist('colecao')}")
        
        if not status_list and not request.args.getlist('colecao'):
            print(f"[DEBUG] Usando caminho SEM FILTROS - busca todas as tarefas")
            try:
                # WORKAROUND: Especificar apenas colunas que existem para evitar erro PGRST204
                print(f"[DEBUG] Tentando buscar tarefas com colunas específicas...")
                tarefas_filtradas = supabase.table("tarefas").select("id, nome, status, data_inicio, data_fim, projeto_id, colecao, usuario_id, ativa, excluida").in_("projeto_id", projeto_ids).execute().data or []
                print(f"[DEBUG] Total de tarefas encontradas SEM filtros: {len(tarefas_filtradas)}")
                
                # DEBUG ESPECÍFICO: Verificar tarefas dos projetos problemáticos
                projetos_problema = ['8b4cd282-203c-4c2f-a13e-1e0d6b0745dc', 'c658bec1-0196-4ad0-b1d9-19b418419223']
                for pid in projetos_problema:
                    tarefas_deste_proj = [t for t in tarefas_filtradas if t.get('projeto_id') == pid]
                    lancamentos = [t for t in tarefas_deste_proj if t.get('nome', '').strip().lower() == 'lançamento']
                    nome_proj = "2509" if pid == '8b4cd282-203c-4c2f-a13e-1e0d6b0745dc' else "2606"
                    print(f"[DEBUG-BUSCA] Projeto {nome_proj}: {len(tarefas_deste_proj)} tarefas, {len(lancamentos)} lançamentos")
                    if lancamentos:
                        l = lancamentos[0]
                        print(f"[DEBUG-BUSCA]   Lançamento encontrado: '{l.get('nome')}' status={l.get('status')} ativa={l.get('ativa')}")
                        
            except Exception as e:
                print(f"[ERROR] Erro ao buscar tarefas (PGRST204?): {e}")
                # Fallback: tentar busca mais simples
                try:
                    print(f"[DEBUG] Tentando fallback com select(*)...")
                    tarefas_filtradas = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute().data or []
                    print(f"[DEBUG] Fallback bem-sucedido: {len(tarefas_filtradas)} tarefas")
                except Exception as e2:
                    print(f"[ERROR] Fallback também falhou: {e2}")
                    tarefas_filtradas = []
        else:
            print(f"[DEBUG] Usando caminho COM FILTROS - aplicando filtros de status/coleção")
            try:
                for projeto_id in projeto_ids:
                    tarefas_projeto = supabase.table("tarefas").select("id, nome, status, data_inicio, data_fim, projeto_id, colecao, usuario_id, ativa, excluida").eq("projeto_id", projeto_id).execute()
                    if hasattr(tarefas_projeto, 'data') and tarefas_projeto.data:
                        tarefas_filtradas.extend(tarefas_projeto.data)
                print(f"[DEBUG] Total de tarefas ANTES dos filtros: {len(tarefas_filtradas)}")
                
                # Filtro de status (múltiplo)
                if status_list:
                    tarefas_antes = len(tarefas_filtradas)
                    tarefas_filtradas = [
                        t for t in tarefas_filtradas
                        if t.get('status') in status_list or normalizar(t.get('nome', '')) == 'lancamento'
                    ]
                    print(f"[DEBUG] Filtro de STATUS aplicado: {tarefas_antes} -> {len(tarefas_filtradas)} tarefas")
                # Filtro de colecao (múltiplo)
                colecao_list = request.args.getlist('colecao')
                if colecao_list:
                    tarefas_antes = len(tarefas_filtradas)
                    tarefas_filtradas = [t for t in tarefas_filtradas if t.get('colecao') in colecao_list]
                    print(f"[DEBUG] Filtro de COLEÇÃO aplicado: {tarefas_antes} -> {len(tarefas_filtradas)} tarefas")
            except Exception as e:
                print(f"Erro ao buscar tarefas dos projetos com filtros: {e}")
                tarefas_filtradas = []
    else:
        tarefas_filtradas = []

    # Limites de segurança para evitar travamento
    MAX_PROJETOS = 100
    MAX_TAREFAS = 1000  # AUMENTADO SIGNIFICATIVAMENTE para garantir que não perca lançamentos
    
    if len(projetos) > MAX_PROJETOS:
        projetos = projetos[:MAX_PROJETOS]
        print(f"[DEBUG-LIMITE] Projetos limitados para {MAX_PROJETOS}")
    
    # SOLUÇÃO: Garantir que tarefas de lançamento sejam sempre incluídas
    if len(tarefas_filtradas) > MAX_TAREFAS:
        print(f"[DEBUG-LIMITE] Muitas tarefas ({len(tarefas_filtradas)}), aplicando limite inteligente...")
        
        # Separar lançamentos das outras tarefas
        lancamentos = [t for t in tarefas_filtradas if normalizar(t.get('nome', '')) == 'lancamento']
        outras_tarefas = [t for t in tarefas_filtradas if normalizar(t.get('nome', '')) != 'lancamento']
        
        # Garantir que todos os lançamentos sejam incluídos + outras tarefas até o limite
        tarefas_prioritarias = lancamentos + outras_tarefas[:MAX_TAREFAS - len(lancamentos)]
        tarefas_filtradas = tarefas_prioritarias
        
        print(f"[DEBUG-LIMITE] Incluídos: {len(lancamentos)} lançamentos + {len(outras_tarefas[:MAX_TAREFAS - len(lancamentos)])} outras tarefas = {len(tarefas_filtradas)} total")
    
    # Verificação final: garantir que os lançamentos problemáticos estão incluídos
    projetos_problema = ['8b4cd282-203c-4c2f-a13e-1e0d6b0745dc', 'c658bec1-0196-4ad0-b1d9-19b418419223']
    for pid in projetos_problema:
        lancamentos_projeto = [t for t in tarefas_filtradas if t.get('projeto_id') == pid and normalizar(t.get('nome', '')) == 'lancamento']
        nome_proj = "2509" if pid == '8b4cd282-203c-4c2f-a13e-1e0d6b0745dc' else "2606"
        print(f"[DEBUG-VERIFICACAO] Projeto {nome_proj}: {len(lancamentos_projeto)} lançamentos garantidos")

    # Construir lista de coleções disponíveis a partir das tarefas filtradas
    try:
        colecoes = sorted(list({str(t.get('colecao')).strip() for t in tarefas_filtradas if t.get('colecao')}))
    except Exception:
        colecoes = []

    # Formatar datas dos projetos para dd/mm/aaaa
    # Associar tarefas a cada projeto
    tarefas_por_projeto = {}
    for projeto in projetos:
        if projeto.get('data_inicio'):
            projeto['data_inicio'] = projeto['data_inicio'].split('T')[0] if 'T' in projeto['data_inicio'] else projeto['data_inicio']
        if projeto.get('data_fim'):
            projeto['data_fim'] = projeto['data_fim'].split('T')[0] if 'T' in projeto['data_fim'] else projeto['data_fim']
        # Adiciona lista de tarefas ao projeto
        projeto['tarefas'] = [t for t in tarefas_filtradas if t.get('projeto_id') == projeto['id']]

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
    
    # Sistema para garantir cores únicas e bem diferenciadas será criado DEPOIS da ordenação
    
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
    print('[DEBUG] Agrupamento de tarefas por projeto:')
    for pid, tarefas in tarefas_por_projeto.items():
        print(f'Projeto {pid}: {len(tarefas)} tarefas')
    
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
    from utils.validators import normaliza_opcional
    
    # Debug específico para projetos problemáticos - ANTES da associação
    projetos_problema_ids = []
    for projeto in projetos:
        nome_projeto = projeto.get('nome', '')
        if nome_projeto in ['2509 - WORLD SET', '2606 - WORLD JUN']:
            projeto_id = projeto.get('id')
            projetos_problema_ids.append(projeto_id)
            print(f"[DEBUG-RASTREAMENTO] Projeto problemático: {nome_projeto} (ID: {projeto_id})")
            
            # Contar quantas tarefas existem para este projeto em tarefas_filtradas
            tarefas_deste_projeto = [t for t in tarefas_filtradas if str(t.get('projeto_id')).strip() == str(projeto_id).strip()]
            print(f"[DEBUG-RASTREAMENTO] Tarefas em tarefas_filtradas para {nome_projeto}: {len(tarefas_deste_projeto)}")
            
            # Verificar se há lançamento em tarefas_filtradas
            lancamentos = [t for t in tarefas_deste_projeto if normalizar(t.get('nome', '')) == 'lancamento']
            print(f"[DEBUG-RASTREAMENTO] Lançamentos em tarefas_filtradas para {nome_projeto}: {len(lancamentos)}")
            for l in lancamentos:
                print(f"[DEBUG-RASTREAMENTO]   - {l.get('nome', '')} | Status: {l.get('status', '')}")
    
    for projeto in projetos:
        pid = projeto.get('id')
        print(f"[DEBUG] Projeto id: {pid} ({type(pid)})")
        tarefas_associadas = []
        nomes_normalizados = []
        for tarefa in tarefas_filtradas:
            tid = tarefa.get('projeto_id')
            if str(tid).strip() == str(pid).strip():
                tarefas_associadas.append(tarefa)
                nome = tarefa.get('nome', '')
                nomes_normalizados.append(normaliza_opcional(nome))
        print(f"[DEBUG] Projeto {pid} recebeu {len(tarefas_associadas)} tarefas")
        if pid in projetos_problema_ids:
            print(f"[DEBUG-RASTREAMENTO] APÓS associação - {projeto.get('nome', '')}: {len(tarefas_associadas)} tarefas")
        print(f"[DEBUG] Nomes normalizados das tarefas do projeto {pid}: {nomes_normalizados}")
        projeto['tarefas'] = tarefas_associadas
    
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
                    'colecao': str(tarefa.get('colecao', '') or ''),
                    'projeto_nome': str(projeto_nome),
                    'projeto_origem': str(projeto_nome),
                    'bar_color': '#4ECDC4',  # Cor temporária, será ajustada após ordenação
                    'ordem': ordem_tarefas_unicas.get((tarefa.get('nome') or '').strip().lower(), 9999)  # Usar a ordem das tarefas_unicas
                })
        except Exception as e:
            print(f"Erro ao processar tarefa: {e}")
            continue

    # Ordenar projetos por nome (ordem crescente) imediatamente antes do render_template
    # Ordenar projetos pela data de início da tarefa "lançamento" (primeira tarefa de cada projeto com nome contendo "lançamento")
    import unicodedata
    # Função normalizar agora é importada de utils.validators no topo do arquivo

    def data_inicio_lancamento(projeto):
        tarefas = projeto.get('tarefas', [])
        for t in tarefas:
            print(f"[ORDENAÇÃO] Tarefa: '{t.get('nome', '')}' | Normalizada: '{normalizar(t.get('nome', ''))}'")
        tarefas_lancamento = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
        print(f"[ORDENAÇÃO] Projeto: {projeto.get('nome', 'Sem nome')}")
        print(f"[ORDENAÇÃO] Tarefas consideradas para lançamento: {[t.get('nome') for t in tarefas_lancamento]}")
        datas = [t.get('data_inicio') or t.get('data_inicio_tarefa') for t in tarefas_lancamento if (t.get('data_inicio') or t.get('data_inicio_tarefa'))]
        datas_validas = [d for d in datas if d]
        print(f"[ORDENAÇÃO] Datas consideradas: {datas_validas}")
        if datas_validas:
            print(f"[ORDENAÇÃO] Data usada para ordenação: {min(datas_validas)}")
            return min(datas_validas)
        
        # Só executa as mensagens de "sem data" quando realmente não há data
        if not tarefas_lancamento:
            print(f"[ORDENAÇÃO] Projeto SEM tarefa de lançamento: {projeto.get('nome', 'Sem nome')}")
            print(f"[ORDENAÇÃO] Nomes normalizados das tarefas:")
            for t in tarefas:
                print(f"  - '{t.get('nome', '')}' | Normalizada: '{normalizar(t.get('nome', ''))}'")
        else:
            # Tem tarefas de lançamento, mas sem data válida
            print(f"[ORDENAÇÃO] Projeto com tarefa de lançamento MAS sem data válida: {projeto.get('nome', 'Sem nome')}")
            for t in tarefas_lancamento:
                print(f"  - Tarefa lançamento: '{t.get('nome', '')}' | data_inicio: {t.get('data_inicio')} | data_inicio_tarefa: {t.get('data_inicio_tarefa')}")
        
        print(f"[ORDENAÇÃO] Sem data de lançamento válida, usando padrão '9999-12-31'")
        return '9999-12-31'
    projetos = sorted(projetos, key=lambda p: (data_inicio_lancamento(p), normalizar(p.get('nome', ''))))

    # Criar cores dos projetos APÓS a ordenação para manter a mesma sequência
    projects_colors = {}
    cores_utilizadas = set()
    
    # Atribuir cores seguindo a ordem dos projetos ordenados
    for i, projeto in enumerate(projetos):
        projeto_nome = projeto.get('nome', 'Projeto sem nome')
        if projeto_nome not in projects_colors:
            # Usar índice sequencial para garantir cores únicas na ordem correta
            cor_escolhida = cores[i % len(cores)]
            projects_colors[projeto_nome] = cor_escolhida
            cores_utilizadas.add(cor_escolhida)

    # Atualizar cores do gantt_geral_data com as cores corretas após ordenação
    for item in gantt_geral_data:
        projeto_nome = item.get('projeto_nome', '')
        item['bar_color'] = str(projects_colors.get(projeto_nome, '#4ECDC4'))

    # Lógica para definir status do projeto
    for projeto in projetos:
        tarefas = projeto.get('tarefas', [])
        if not tarefas:
            projeto['status'] = 'Normal'
        else:
            # Considera concluído se TODAS as tarefas têm status equivalente a 'concluído' (com ou sem acento, maiúsculo/minúsculo)
            def is_concluida(status):
                s = (status or '').strip().lower()
                return s in ['concluido', 'concluida', 'concluído', 'concluída']
            if all(is_concluida(t.get('status', '')) for t in tarefas):
                projeto['status'] = 'Concluído'
            else:
                projeto['status'] = 'Normal'

    # DEBUG: Exibir status de todos os projetos carregados
    print('DEBUG STATUS PROJETOS:')
    for projeto in projetos:
        print(f"Projeto: {projeto.get('nome', 'Sem nome')} | Status: {projeto.get('status', 'Sem status')}")

    print('[DEBUG] Ordem dos projetos antes do render:')
    for projeto in projetos:
        data_lanc = None  # Inicializar sempre como None
        # Print detalhado das tarefas do projeto 2602 - WORLD FEV
        if projeto.get('nome', '').strip().lower() == '2602 - world fev':
            print(f"[DEBUG] Tarefas do projeto 2602 - WORLD FEV:")
            for t in projeto.get('tarefas', []):
                print(f"  Tarefa: {t.get('nome', '')} | data_inicio: {t.get('data_inicio')} | data_inicio_tarefa: {t.get('data_inicio_tarefa')}")
            print(f"[DEBUG] Tarefas filtradas do projeto 2602 - WORLD FEV:")
            for t in tarefas_filtradas:
                if str(t.get('projeto_id')).strip() == str(projeto.get('id')).strip():
                    print(f"  Tarefa: {t.get('nome', '')} | projeto_id: {t.get('projeto_id')} | data_inicio: {t.get('data_inicio')} | data_inicio_tarefa: {t.get('data_inicio_tarefa')}")
        
        # Buscar tarefa de lançamento
        nome_projeto = projeto.get('nome', 'Sem nome')
        tarefas_lancamento_encontradas = []
        
        for t in projeto.get('tarefas', []):
            nome_tarefa = t.get('nome', '')
            nome_normalizado = normalizar(nome_tarefa)
            if nome_normalizado == 'lancamento':
                data_inicio = t.get('data_inicio')
                data_inicio_tarefa = t.get('data_inicio_tarefa')
                data_final = data_inicio or data_inicio_tarefa
                tarefas_lancamento_encontradas.append({
                    'nome': nome_tarefa,
                    'data_inicio': data_inicio,
                    'data_inicio_tarefa': data_inicio_tarefa,
                    'data_final': data_final
                })
                data_lanc = data_final
                break
        
        # Debug específico para projetos problemáticos
        if nome_projeto in ['2509 - WORLD SET', '2606 - WORLD JUN']:
            print(f"[DEBUG-PROBLEMA] Projeto: {nome_projeto}")
            print(f"[DEBUG-PROBLEMA] Total tarefas no projeto: {len(projeto.get('tarefas', []))}")
            print(f"[DEBUG-PROBLEMA] Tarefas lançamento encontradas: {len(tarefas_lancamento_encontradas)}")
            for tl in tarefas_lancamento_encontradas:
                print(f"[DEBUG-PROBLEMA]   - {tl['nome']}: data_final = {tl['data_final']}")
        
        print(f"Projeto: {nome_projeto} | Data lançamento: {data_lanc}")
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
                             gantt_geral_data=gantt_geral_data,
                             colecoes=colecoes,
                             # Passar os valores dos filtros para manter seleções
                             filtros_ativos={
                                 'nome_list': nome_list,
                                 'tarefa_list': tarefa_list,
                                 'status_list': status_list,
                                 'data_inicio': data_inicio,
                                 'data_fim': data_fim,
                                 'tipo_id': tipo_id,
                                 'ambiente': ambiente
                             })
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
                             gantt_geral_data=gantt_geral_data,
                             colecoes=colecoes,
                             # Passar os valores dos filtros para manter seleções
                             filtros_ativos={
                                 'nome_list': nome_list,
                                 'tarefa_list': tarefa_list,
                                 'status_list': status_list,
                                 'data_inicio': data_inicio,
                                 'data_fim': data_fim,
                                 'tipo_id': tipo_id,
                                 'ambiente': ambiente
                             })

@projetos_bp.route('/projetos/novo', methods=['GET', 'POST'])
@projetos_bp.route('/projetos/criar', methods=['GET', 'POST'])
def criar_projeto():
    """Cria um novo projeto"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        try:
            tipos = supabase.table('tipos_projeto').select('*').execute().data
            print('TYPES DEBUG (criar):', tipos)
        except Exception as e:
            tipos = []
        # Buscar tarefas_unicas para exibir no formulário
        try:
            tarefas_unicas = supabase.table('tarefas_unicas').select('*').order('ordem').execute().data
        except Exception as e:
            tarefas_unicas = []
        if request.method == 'POST':
            nome = request.form['nome']
            data_inicio = request.form['data_inicio']
            data_fim = request.form['data_fim']
            tipo_id = normaliza_opcional(request.form.get('tipo_id'))
            # Validação
            erro = validar_projeto(nome, data_inicio, data_fim)
            if erro:
                flash(erro)
                return render_template('novo_projeto.html', tipos=tipos, tarefas_unicas=tarefas_unicas)
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
        return render_template('novo_projeto.html', tipos=tipos, tarefas_unicas=tarefas_unicas)
    except Exception as e:
        print('ERRO INESPERADO EM criar_projeto:', e)
        return render_template('novo_projeto.html', tipos=[], tarefas_unicas=[])


# ROTA DE EDIÇÃO DE PROJETO
@projetos_bp.route('/projetos/editar/<projeto_id>', methods=['GET', 'POST'])
@login_required
@funcionalidade_restrita('editar_projeto')
def editar_projeto(projeto_id):
    print('DEBUG: Entrou na função editar_projeto')
    try:
        tipos = supabase.table('tipos_projeto').select('*').execute().data
        print('TYPES DEBUG:', tipos)
    except Exception as e:
        tipos = []
        print('TYPES DEBUG ERRO:', e)
    """Edita um projeto existente"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # Buscar projeto existente
    projeto = None
    try:
        resp = supabase.table('projetos').select('*').eq('id', projeto_id).single().execute()
        if hasattr(resp, 'data') and resp.data:
            projeto = resp.data
        else:
            flash('Projeto não encontrado.')
            return redirect('/projetos')
    except Exception as e:
        flash(f'Erro ao buscar projeto: {e}')
        return redirect('/projetos')

    # Buscar tipos de projeto para o formulário
    try:
        tipos = supabase.table('tipos_projeto').select('*').execute().data
        print('TYPES DEBUG:', tipos)
    except Exception as e:
        tipos = []

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        tipo_id = normaliza_opcional(request.form.get('tipo_id'))
        # Validação
        erro = validar_projeto(nome, data_inicio, data_fim)
        if erro:
            flash(erro)
            return render_template('editar_projeto.html', projeto=projeto, tipos=tipos)
        try:
            update_data = {
                "nome": nome,
                "descricao": descricao,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "tipo_id": tipo_id
            }
            resp = supabase.table('projetos').update(update_data).eq('id', projeto_id).execute()
            if hasattr(resp, 'data') and resp.data:
                flash('Projeto atualizado com sucesso!')
                return redirect('/projetos')
            else:
                flash('Erro ao atualizar o projeto.')
        except Exception as e:
            flash(f'Erro ao atualizar o projeto: {e}')
        # Atualizar objeto projeto para refletir alterações no formulário
        projeto.update(update_data)
    return render_template('editar_projeto.html', projeto=projeto, tipos=tipos)
    """Cria um novo projeto"""
    # Verificar se usuário está logado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
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
        try:
            tipos = supabase.table('tipos_projeto').select('*').execute().data
            print('TYPES DEBUG (criar):', tipos)
        except Exception as e:
            tipos = []
        # Buscar tarefas_unicas para exibir no formulário
        try:
            tarefas_unicas = supabase.table('tarefas_unicas').select('*').order('ordem').execute().data
        except Exception as e:
            tarefas_unicas = []
        return render_template('novo_projeto.html', tipos=tipos, tarefas_unicas=tarefas_unicas)
    except Exception as e:
        print('ERRO INESPERADO EM criar_projeto:', e)
        return render_template('novo_projeto.html', tipos=[], tarefas_unicas=[])


@projetos_bp.route('/projetos/duplicar/<projeto_id>', methods=['POST'])
@login_required
@funcionalidade_restrita('restr_criar_projeto')
def duplicar_projeto(projeto_id):
    """Duplica um projeto existente com todas suas tarefas"""
    try:
        # Buscar o projeto original
        projeto_original = supabase.table("projetos").select("*").eq("id", projeto_id).execute()
        if not projeto_original.data:
            flash("Projeto não encontrado.")
            return redirect('/projetos')
        
        projeto = projeto_original.data[0]
        
        # Criar novo nome para o projeto duplicado
        nome_original = projeto['nome']
        nome_duplicado = f"{nome_original} - Cópia"
        
        # Verificar se já existe um projeto com este nome e incrementar se necessário
        contador = 1
        nome_final = nome_duplicado
        while True:
            existe = supabase.table("projetos").select("id").eq("nome", nome_final).execute()
            if not existe.data:
                break
            contador += 1
            nome_final = f"{nome_duplicado} {contador}"
        
        # Criar o novo projeto
        novo_projeto_data = {
            "nome": nome_final,
            "data_inicio": projeto['data_inicio'],
            "data_fim": projeto['data_fim'],
            "tipo_id": projeto['tipo_id'],
            "usuario_id": session['user_id']
        }
        
        novo_projeto_resp = supabase.table("projetos").insert(novo_projeto_data).execute()
        if not novo_projeto_resp.data:
            flash("Erro ao duplicar o projeto.")
            return redirect('/projetos')
        
        novo_projeto_id = novo_projeto_resp.data[0]['id']
        
        # Buscar e duplicar todas as tarefas do projeto original
        tarefas_originais = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute()
        
        if tarefas_originais.data:
            tarefas_duplicadas = []
            for tarefa in tarefas_originais.data:
                nova_tarefa = {
                    "nome": tarefa['nome'],
                    "data_inicio": tarefa.get('data_inicio'),
                    "data_fim": tarefa.get('data_fim'),
                    "duracao": tarefa.get('duracao'),
                    "status": 'pendente',  # Todas as tarefas duplicadas começam como pendentes
                    "projeto_id": novo_projeto_id,
                    "usuario_id": session['user_id'],
                    "colecao": tarefa.get('colecao'),
                    "predecessoras": tarefa.get('predecessoras'),
                    "ordem": tarefa.get('ordem', len(tarefas_duplicadas) + 1)
                }
                tarefas_duplicadas.append(nova_tarefa)
            
            # Inserir todas as tarefas duplicadas
            if tarefas_duplicadas:
                supabase.table("tarefas").insert(tarefas_duplicadas).execute()
        
        flash(f"Projeto '{nome_final}' duplicado com sucesso!")
        return redirect('/projetos')
        
    except Exception as e:
        flash(f"Erro ao duplicar o projeto: {str(e)}")
        print(f"Erro ao duplicar projeto: {e}")
        return redirect('/projetos')