from flask import Blueprint, render_template, request, send_file, make_response, jsonify
from config.database import supabase
from utils.dias_uteis import dias_uteis_entre_datas
from utils.auth import login_required
import os
import base64
from datetime import datetime
import io
import json

# Pandas import (necessário para Excel)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print('DEBUG: routes/relatorio.py - pandas carregado com sucesso')
except ImportError as e:
    print(f'DEBUG: routes/relatorio.py - pandas não disponível: {e}')
    PANDAS_AVAILABLE = False
    pd = None

# Matplotlib imports opcionais para Render
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
    print('DEBUG: routes/relatorio.py - matplotlib carregado com sucesso')
except ImportError as e:
    print(f'DEBUG: routes/relatorio.py - matplotlib não disponível: {e}')
    MATPLOTLIB_AVAILABLE = False
    # Criar mocks para evitar erros
    class MockModule:
        def __getattr__(self, name): return lambda *args, **kwargs: None
    plt = MockModule()
    mdates = MockModule()

relatorio_bp = Blueprint('relatorio', __name__)

print('DEBUG: routes/relatorio.py carregado com sucesso')

def gerar_grafico_gantt(projetos_data, tarefas_data):
    """Gera um gráfico Gantt simples usando matplotlib"""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib não disponível para gerar gráfico Gantt")
        return None
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
        import io
        
        # Configurar matplotlib para não usar display
        plt.switch_backend('Agg')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Preparar dados
        y_positions = []
        y_labels = []
        colors = []
        
        # Adicionar projetos
        for i, projeto in enumerate(projetos_data):
            if projeto.get('data_inicio') and projeto.get('data_fim'):
                try:
                    start_date = pd.to_datetime(projeto['data_inicio']).date()
                    end_date = pd.to_datetime(projeto['data_fim']).date()
                    
                    y_positions.append(len(projetos_data) - i - 1)
                    y_labels.append(f"[PROJETO] {projeto.get('nome', 'Projeto')[:30].encode('ascii', 'ignore').decode('ascii')}")
                    
                    # Barra do projeto
                    ax.barh(y_positions[-1], (end_date - start_date).days, 
                           left=mdates.date2num(start_date), height=0.3, 
                           color='lightblue', alpha=0.7, edgecolor='blue')
                    
                except Exception as e:
                    print(f"Erro ao processar projeto {projeto.get('id')}: {e}")
        
        # Adicionar tarefas (se houver)
        tarefa_offset = len(projetos_data)
        for i, tarefa in enumerate(tarefas_data[:20]):  # Limitar a 20 tarefas para não sobrecarregar
            if tarefa.get('data_inicio') and tarefa.get('data_fim'):
                try:
                    start_date = pd.to_datetime(tarefa['data_inicio']).date()
                    end_date = pd.to_datetime(tarefa['data_fim']).date()
                    
                    y_positions.append(tarefa_offset + i)
                    y_labels.append(f"[TAREFA] {tarefa.get('titulo', tarefa.get('nome', 'Tarefa'))[:25].encode('ascii', 'ignore').decode('ascii')}")
                    
                    # Barra da tarefa
                    ax.barh(y_positions[-1], (end_date - start_date).days, 
                           left=mdates.date2num(start_date), height=0.3, 
                           color='lightgreen', alpha=0.7, edgecolor='green')
                    
                except Exception as e:
                    print(f"Erro ao processar tarefa {tarefa.get('id')}: {e}")
        
        # Configurar eixos
        ax.set_yticks(y_positions)
        ax.set_yticklabels(y_labels)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        
        plt.xticks(rotation=45)
        plt.title('Grafico Gantt - Visao Geral dos Projetos', fontsize=14, fontweight='bold')
        plt.xlabel('Datas')
        plt.ylabel('Projetos e Tarefas')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Salvar em buffer de memória
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
        
    except Exception as e:
        print(f"Erro ao gerar gráfico Gantt: {e}")
        return None


@relatorio_bp.route('/exportacao')
def pagina_exportacao():
    """Página de teste para exportação de relatórios"""
    try:
        # Buscar todos os projetos para o dropdown
        projetos_data = supabase.table('projetos').select('id, nome').order('nome').execute()
        projetos = projetos_data.data if projetos_data.data else []
        
        return render_template('relatorio_exportacao.html', projetos=projetos)
    except Exception as e:
        print(f"❌ Erro ao carregar página de exportação: {str(e)}")
        return f"Erro: {str(e)}", 500


@relatorio_bp.route('/gantt_excel', methods=['GET', 'POST'])
def exportar_gantt_excel():
    print(f"[GANTT EXCEL] ===== INÍCIO DA FUNÇÃO =====")
    print(f"[GANTT EXCEL] Método da requisição: {request.method}")
    print(f"[GANTT EXCEL] É JSON?: {request.is_json}")
    
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        print(f"[GANTT EXCEL] Dados JSON recebidos: {data}")
        gantt_base64 = data.get('gantt_base64')
        tipo_id = data.get('tipo_id', '')
        projeto_id = data.get('projeto_id', '')
        projeto_ids = data.get('projeto_ids', [])
        status = data.get('status', [])
        colecao = data.get('colecao', [])
        data_inicio = data.get('data_inicio', '')
        data_fim = data.get('data_fim', '')
    else:
        gantt_base64 = request.args.get('gantt_base64')
        tipo_id = request.args.get('tipo_id', '')
        projeto_id = request.args.get('projeto_id', '')
        projeto_ids = request.args.getlist('projeto_ids')
        status = request.args.getlist('status')
        colecao = request.args.getlist('colecao')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        
        # Se não foi fornecido projeto_id nos parâmetros, verificar se estamos na página de detalhes do projeto
        if not projeto_id and not projeto_ids:
            # Verificar se a URL de referência é de detalhes do projeto
            referer = request.headers.get('Referer', '')
            if '/projetos/' in referer and referer.count('/') >= 4:
                # Extrair projeto_id da URL de referência (formato: .../projetos/{projeto_id})
                try:
                    import re
                    match = re.search(r'/projetos/([a-f0-9-]+)(?:/|$)', referer)
                    if match:
                        projeto_id = match.group(1)
                        print(f"[GANTT EXCEL] Detectado projeto_id da URL de referência: {projeto_id}")
                except Exception as e:
                    print(f"[GANTT EXCEL] Erro ao extrair projeto_id: {e}")
    
    # Consolidar projeto_ids (suporta tanto projeto_id único quanto projeto_ids múltiplos)
    all_projeto_ids = []
    if projeto_id:  # Compatibilidade com versão antiga
        all_projeto_ids.append(projeto_id)
    if projeto_ids:  # Nova versão com múltiplos projetos
        all_projeto_ids.extend(projeto_ids)
    
    print(f"[GANTT EXCEL] Filtros recebidos - projeto_id: {projeto_id}, projeto_ids: {projeto_ids}, tipo_id: {tipo_id}")
    print(f"[GANTT EXCEL] projeto_ids consolidados: {all_projeto_ids}")
    
    # Buscar tarefas diretamente do banco
    query = supabase.table('tarefas').select('*')
    if all_projeto_ids:
        query = query.in_('projeto_id', all_projeto_ids)
    elif tipo_id:
        projetos = supabase.table('projetos').select('id').eq('tipo_id', tipo_id).execute().data
        projetos_ids = [p['id'] for p in projetos]
        if projetos_ids:
            query = query.in_('projeto_id', projetos_ids)
        else:
            tarefas = []
    tarefas = query.execute().data if 'tarefas' not in locals() else tarefas

    # Aplicar filtros adicionais: status, coleção, datas
    if status:
        tarefas = [t for t in tarefas if t.get('status','').lower() in [s.lower() for s in status]]
    if colecao:
        tarefas = [t for t in tarefas if t.get('colecao','') in colecao]
    if data_inicio:
        tarefas = [t for t in tarefas if (t.get('data_inicio') or t.get('data_inicio_tarefa','')) >= data_inicio]
    if data_fim:
        tarefas = [t for t in tarefas if (t.get('data_fim') or t.get('data_fim_tarefa','')) <= data_fim]

    # Buscar nomes dos projetos
    projetos_ids = list(set([t.get('projeto_id') for t in tarefas if t.get('projeto_id')]))
    nomes_projetos = {}
    if projetos_ids:
        try:
            projetos_resp = supabase.table('projetos').select('id, nome').in_('id', projetos_ids).execute()
            if hasattr(projetos_resp, 'data') and projetos_resp.data:
                for p in projetos_resp.data:
                    nomes_projetos[p['id']] = p.get('nome', '')
        except Exception:
            pass

    # Montar projetos_relatorio igual ao relatório
    projetos_dict = {}
    for t in tarefas:
        pid = t.get('projeto_id')
        if not pid:
            continue
        if pid not in projetos_dict:
            projetos_dict[pid] = []
        projetos_dict[pid].append(t)

    nomes_projetos = {}
    if projetos_dict:
        try:
            projetos_ids = list(projetos_dict.keys())
            projetos_resp = supabase.table('projetos').select('id, nome').in_('id', projetos_ids).execute()
            if hasattr(projetos_resp, 'data') and projetos_resp.data:
                for p in projetos_resp.data:
                    nomes_projetos[p['id']] = p.get('nome', '')
        except Exception:
            pass

    # Buscar nomes dos usuários responsáveis
    usuario_ids = set()
    for tarefas_proj in projetos_dict.values():
        for t in tarefas_proj:
            if t.get('usuario_id'):
                usuario_ids.add(str(t.get('usuario_id')))
    nomes_usuarios = {}
    if usuario_ids:
        try:
            usuarios_resp = supabase.table('usuarios').select('id, nome').in_('id', list(usuario_ids)).execute()
            if hasattr(usuarios_resp, 'data') and usuarios_resp.data:
                for u in usuarios_resp.data:
                    nomes_usuarios[str(u['id'])] = u.get('nome', '')
        except Exception:
            pass

    # Montar lista de projetos para exportação
    projetos_relatorio = []
    for pid, tarefas_proj in projetos_dict.items():
        tarefas_ordenadas = sorted(tarefas_proj, key=lambda t: t.get('ordem', 0))
        tarefas_relatorio = []
        for t in tarefas_ordenadas:
            def formatar_data(data):
                if not data:
                    return ''
                try:
                    return datetime.strptime(data[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    return data
            data_inicio_raw = t.get('data_inicio') or t.get('data_inicio_tarefa', '')
            data_fim_raw = t.get('data_fim') or t.get('data_fim_tarefa', '')
            dias_uteis = ''
            if data_inicio_raw and data_fim_raw:
                try:
                    dias_uteis = dias_uteis_entre_datas(data_inicio_raw, data_fim_raw)
                except Exception:
                    dias_uteis = ''
            usuario_id = t.get('usuario_id')
            print(f"[DEBUG EXCEL MAP] Tarefa: {t.get('nome', 'Sem nome')}, usuario_id: {usuario_id}")
            responsavel_nome = nomes_usuarios.get(str(usuario_id), '') if usuario_id else ''
            print(f"[DEBUG EXCEL MAP] Nome responsável: '{responsavel_nome}' (usuario_id: {usuario_id})")
            tarefas_relatorio.append({
                'nome': t.get('nome', t.get('titulo', 'Tarefa sem nome')),
                'inicio': formatar_data(data_inicio_raw),
                'fim': formatar_data(data_fim_raw),
                'dias_uteis': dias_uteis,
                'duracao': t.get('duracao', ''),
                'colecao': t.get('colecao', ''),
                'responsavel': responsavel_nome,
            })
        projetos_relatorio.append({
            'nome': nomes_projetos.get(pid, 'Projeto'),
            'tarefas': tarefas_relatorio
        })

    # Ordenar projetos por nome (ordem alfabética)
    projetos_ordenados = sorted(projetos_relatorio, key=lambda p: p['nome'].lower())
    
    print(f"[ORDEM] Projetos ordenados alfabeticamente:")
    for i, p in enumerate(projetos_ordenados):
        print(f"[ORDEM] {i+1}. {p['nome']}")

    # Montar dados para exportação na ordem do relatório
    dados = []
    from datetime import datetime
    def formatar_data_excel(data):
        if not data:
            return ''
        try:
            # Aceita tanto dd/mm/aaaa quanto yyyy-mm-dd
            if '/' in data:
                return datetime.strptime(data, '%d/%m/%Y').strftime('%d/%m/%Y')
            elif '-' in data:
                return datetime.strptime(data[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        except Exception:
            return data
        return data

    for projeto in projetos_ordenados:
        for tarefa in projeto['tarefas']:
            responsavel_final = tarefa.get('responsavel', '')
            print(f"[DEBUG FINAL EXCEL] Tarefa: {tarefa['nome']}, Responsável final: '{responsavel_final}'")
            dados.append({
                'Projeto': projeto['nome'],
                'Tarefa': tarefa['nome'],
                'Responsável': responsavel_final,
                'Início': formatar_data_excel(tarefa['inicio']),
                'Fim': formatar_data_excel(tarefa['fim']),
                'Dias Úteis': tarefa['dias_uteis'],
                'Duração': tarefa['duracao'],
                'Coleção': tarefa['colecao'],
            })
    
    # Verificar se pandas está disponível (verificação local)
    try:
        import pandas as pd
        print("[GANTT EXCEL] pandas importado com sucesso na função")
        pandas_ok = True
    except ImportError as e:
        print(f"[GANTT EXCEL] ERROR: Não foi possível importar pandas: {e}")
        return f"Erro: pandas não está disponível. Instale com: pip install pandas. Erro: {e}", 500
    
    print(f"[GANTT EXCEL] Criando DataFrame com {len(dados)} linhas")
    df = pd.DataFrame(dados)
    print(f"[GANTT EXCEL] DataFrame criado: {df.shape}")

    # Gerar arquivo Excel em memória
    print("[GANTT EXCEL] Iniciando geração do arquivo Excel...")
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            from datetime import datetime
            print(f"[GANTT EXCEL] Verificando dados antes das abas de Gantt:")
            print(f"[GANTT EXCEL] - projetos_ordenados: {len(projetos_ordenados) if projetos_ordenados else 0}")
            print(f"[GANTT EXCEL] - all_projeto_ids: {all_projeto_ids}")
            
            if not projetos_ordenados:
                print(f"[GANTT EXCEL] ERRO: projetos_ordenados está vazio!")
                return f"Erro: Nenhum projeto encontrado para gerar o Excel", 400
                
            print(f"[GANTT EXCEL] Processando {len(projetos_ordenados)} projetos para abas de Gantt...")
            
            # Para cada projeto, criar uma aba de Gantt
            for idx, projeto in enumerate(projetos_ordenados):
                print(f"[GANTT EXCEL] Criando aba {idx+1} para projeto: {projeto.get('nome', 'SEM NOME')}")
                nome_aba = str(projeto['nome'])[:31]  # Limite do Excel para nome de aba
                print(f"[GANTT EXCEL] Nome da aba: '{nome_aba}'")
                gantt_sheet.write('A1', 'Tarefa')
                gantt_sheet.write('B1', 'Responsável')
                gantt_sheet.write('C1', 'Início')
                gantt_sheet.write('D1', 'Fim')
                gantt_sheet.write('E1', 'Duração')
                gantt_sheet.write('F1', 'Coleção')
                gantt_sheet.write('G1', 'Dias até início')
                # Preencher dados e calcular largura máxima de cada coluna
                col_widths = [len('Tarefa'), len('Responsável'), len('Início'), len('Fim'), len('Duração'), len('Coleção'), len('Dias até início')]
                row = 1
                tarefas_validas = []
                if 'tarefas' in projeto and projeto['tarefas']:
                    for tarefa in projeto['tarefas']:
                        inicio = formatar_data_excel(tarefa['inicio'])
                        fim = formatar_data_excel(tarefa.get('fim', ''))
                        duracao = tarefa['duracao'] if tarefa['duracao'] else 0
                        colecao = tarefa.get('colecao', '')
                        responsavel = tarefa.get('responsavel', '')
                        try:
                            data_ini = datetime.strptime(inicio, '%d/%m/%Y')
                            if inicio and duracao and data_ini.year > 2000:
                                tarefas_validas.append({
                                    'nome': tarefa['nome'],
                                    'inicio': inicio,
                                    'fim': fim,
                                    'duracao': duracao,
                                    'colecao': colecao,
                                    'responsavel': responsavel
                                })
                        except Exception:
                            continue

                if tarefas_validas:
                    datas_validas = []
                    for tarefa in tarefas_validas:
                        try:
                            datas_validas.append(datetime.strptime(tarefa['inicio'], '%d/%m/%Y'))
                        except Exception:
                            pass
                    data_min = min(datas_validas) if datas_validas else None

                    # Calcular largura máxima da coluna Duração considerando todos os valores e o cabeçalho
                    duracao_max_len = len('Duração')
                    responsavel_max_len = len('Responsável')
                    for tarefa in tarefas_validas:
                        valor_duracao = tarefa.get('duracao', '')
                        try:
                            valor_duracao = str(int(valor_duracao))
                        except Exception:
                            valor_duracao = str(valor_duracao)
                        duracao_max_len = max(duracao_max_len, len(valor_duracao))
                        responsavel_max_len = max(responsavel_max_len, len(str(tarefa.get('responsavel', ''))))
                    col_widths = [len('Tarefa'), responsavel_max_len, len('Início'), len('Fim'), duracao_max_len, len('Coleção'), len('Dias até início')]
                    row = 1
                    for tarefa in tarefas_validas:
                        inicio = tarefa['inicio']
                        fim = tarefa.get('fim', '')
                        duracao_val = tarefa.get('duracao', '')
                        colecao = tarefa.get('colecao', '')
                        responsavel = tarefa.get('responsavel', '')
                        try:
                            data_ini = datetime.strptime(inicio, '%d/%m/%Y')
                            excel_date = (data_ini - datetime(1899, 12, 30)).days  # formato Excel
                        except Exception:
                            excel_date = ''
                        try:
                            duracao_int = int(duracao_val)
                            gantt_sheet.write_number(row, 4, duracao_int)
                            duracao_len = len(str(duracao_int))
                        except Exception:
                            gantt_sheet.write(row, 4, str(duracao_val))
                            duracao_len = len(str(duracao_val))
                        # Destacar tarefa 'Lançamento' em vermelho e negrito
                        if str(tarefa['nome']).strip().lower() == 'lançamento':
                            destaque_format = workbook.add_format({'font_color': 'red', 'bold': True})
                            gantt_sheet.write(row, 0, tarefa['nome'], destaque_format)
                        else:
                            gantt_sheet.write(row, 0, tarefa['nome'])
                        gantt_sheet.write(row, 1, responsavel)
                        gantt_sheet.write(row, 2, inicio)
                        gantt_sheet.write(row, 3, fim)
                        gantt_sheet.write(row, 5, colecao)
                        gantt_sheet.write(row, 6, excel_date, formato_cinza)
                        col_widths[0] = max(col_widths[0], len(str(tarefa['nome'])))
                        col_widths[1] = max(col_widths[1], len(str(responsavel)))
                        col_widths[2] = max(col_widths[2], len(str(inicio)))
                        col_widths[3] = max(col_widths[3], len(str(fim)))
                        # Garantir que a largura da coluna Duração considere o nome da coluna e o valor convertido para string
                        col_widths[4] = max(col_widths[4], duracao_len, len('Duração'))
                        col_widths[5] = max(col_widths[5], len(str(colecao)))
                        col_widths[6] = max(col_widths[6], len(str(excel_date)))
                        row += 1
                    # Autoajustar largura das colunas na aba do Gantt
                    for i, w in enumerate(col_widths):
                        # Reduzir largura da coluna Dias até início (índice 6)
                        if i == 6:
                            gantt_sheet.set_column(i, i, 2)
                        elif i == 3:
                            # Aplicar formato numérico à coluna Duração
                            num_format = workbook.add_format({'num_format': '0'})
                            gantt_sheet.set_column(i, i, w + 2, num_format)
                        else:
                            gantt_sheet.set_column(i, i, w + 2)

                    chart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})
                    # Série 1: datas de início (formato Excel)
                    chart.add_series({
                        'name': 'Início',
                        'categories': [nome_aba, 1, 0, row-1, 0],
                        'values':     [nome_aba, 1, 6, row-1, 6],
                        'fill':       {'color': '#FFFFFF'},
                        'border':     {'none': True},
                    })
                    # Série 2: duração (dias)
                    chart.add_series({
                        'name': 'Duração',
                        'categories': [nome_aba, 1, 0, row-1, 0],
                        'values':     [nome_aba, 1, 4, row-1, 4],
                        'fill':       {'color': '#00C853'},
                        'border':     {'none': True},
                    })
                    chart.set_title({'none': True})
                    chart.set_x_axis({
                        'num_format': 'dd/mm/yyyy',
                        'major_gridlines': {'visible': False},
                        'minor_gridlines': {'visible': False},
                        'name': '',
                    })
                    chart.set_y_axis({
                        'reverse': True,
                        'name': '',
                        'major_gridlines': {'visible': False},
                        'minor_gridlines': {'visible': False},
                    })
                    chart.set_legend({'none': True})
                    gantt_sheet.insert_chart('H2', chart, {'x_scale': 3.5, 'y_scale': 3.0})
                print(f"[GANTT EXCEL] Aba '{nome_aba}' criada com sucesso! Gráfico de Gantt inserido.")
                # Não sobrescrever largura da coluna 'Duração' (índice 3)
            
            # Inserir imagem do Gantt visual se fornecida
            if gantt_base64:
                print(f"[GANTT EXCEL] Inserindo imagem do Gantt visual...")
                try:
                    from PIL import Image
                    
                    # Decodificar base64 para bytes
                    image_data = base64.b64decode(gantt_base64)
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Criar aba para a imagem do Gantt
                    gantt_visual_sheet = workbook.add_worksheet('Gantt Visual')
                    
                    # Salvar imagem temporariamente em memória para inserir no Excel
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    # Inserir imagem na aba
                    gantt_visual_sheet.insert_image('A1', 'gantt_image.png', {'image_data': img_buffer, 'x_scale': 0.8, 'y_scale': 0.8})
                    
                    print(f"[GANTT EXCEL] Imagem do Gantt visual inserida com sucesso!")
                except Exception as e:
                    print(f"[GANTT EXCEL] Erro ao inserir imagem do Gantt: {e}")
                    # Continuar sem a imagem se houver erro
        
        print("[GANTT EXCEL] Excel gerado com sucesso!")
        
    except Exception as e:
        print(f"[GANTT EXCEL] ERROR na geração do Excel: {e}")
        return f"Erro na geração do Excel: {str(e)}", 500
        
    output.seek(0)

    # Definir nome do arquivo baseado no contexto
    nome_arquivo = 'gantt_relatorio.xlsx'
    if all_projeto_ids and projetos_ordenados:
        if len(projetos_ordenados) == 1:
            # Se estamos exportando um projeto específico, usar o nome do projeto
            projeto_nome = projetos_ordenados[0]['nome']
            # Limpar caracteres especiais do nome do arquivo
            import re
            projeto_nome_limpo = re.sub(r'[^\w\s-]', '', projeto_nome).strip()
            projeto_nome_limpo = re.sub(r'[-\s]+', '_', projeto_nome_limpo)
            nome_arquivo = f'gantt_{projeto_nome_limpo}.xlsx'
        else:
            # Se são múltiplos projetos, usar um nome genérico com a quantidade
            nome_arquivo = f'gantt_{len(projetos_ordenados)}_projetos.xlsx'
        print(f"[GANTT EXCEL] Nome do arquivo definido: {nome_arquivo}")
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=nome_arquivo
    )



@relatorio_bp.route('/relatorio/pdf', methods=['GET', 'POST'])
def gerar_relatorio_pdf():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        gantt_base64 = data.get('gantt_base64')
        tipo_id = data.get('tipo_id', '')
        projeto_id = data.get('projeto_id', '')
        projeto_ids = data.get('projeto_ids', [])
        status = data.get('status', [])
        colecao = data.get('colecao', [])
        data_inicio = data.get('data_inicio', '')
        data_fim = data.get('data_fim', '')
    else:
        gantt_base64 = None
        tipo_id = request.args.get('tipo_id', '')
        projeto_id = request.args.get('projeto_id', '')
        projeto_ids = request.args.getlist('projeto_ids')
        status = request.args.getlist('status')
        colecao = request.args.getlist('colecao')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')

    # Consolidar projeto_ids (suporta tanto projeto_id único quanto projeto_ids múltiplos)
    all_projeto_ids = []
    if projeto_id:  # Compatibilidade com versão antiga
        all_projeto_ids.append(projeto_id)
    if projeto_ids:  # Nova versão com múltiplos projetos
        all_projeto_ids.extend(projeto_ids)
    
    # Buscar tarefas diretamente do banco
    query = supabase.table('tarefas').select('*')
    if all_projeto_ids:
        query = query.in_('projeto_id', all_projeto_ids)
    elif tipo_id:
        projetos = supabase.table('projetos').select('id').eq('tipo_id', tipo_id).execute().data
        projetos_ids = [p['id'] for p in projetos]
        if projetos_ids:
            query = query.in_('projeto_id', projetos_ids)
        else:
            tarefas = []
    tarefas = query.execute().data if 'tarefas' not in locals() else tarefas

    # Aplicar filtros adicionais: status, coleção, datas
    if status:
        tarefas = [t for t in tarefas if t.get('status','').lower() in [s.lower() for s in status]]
    if colecao:
        tarefas = [t for t in tarefas if t.get('colecao','') in colecao]
    if data_inicio:
        tarefas = [t for t in tarefas if (t.get('data_inicio') or t.get('data_inicio_tarefa','')) >= data_inicio]
    if data_fim:
        tarefas = [t for t in tarefas if (t.get('data_fim') or t.get('data_fim_tarefa','')) <= data_fim]


    # Agrupar tarefas por projeto_id
    projetos_dict = {}
    for t in tarefas:
        pid = t.get('projeto_id')
        if not pid:
            continue
        if pid not in projetos_dict:
            projetos_dict[pid] = []
        projetos_dict[pid].append(t)

    # Buscar nomes dos projetos
    nomes_projetos = {}
    if projetos_dict:
        try:
            projetos_ids = list(projetos_dict.keys())
            projetos_resp = supabase.table('projetos').select('id, nome').in_('id', projetos_ids).execute()
            if hasattr(projetos_resp, 'data') and projetos_resp.data:
                for p in projetos_resp.data:
                    nomes_projetos[p['id']] = p.get('nome', '')
        except Exception:
            pass

    # Buscar nomes dos usuários responsáveis
    usuario_ids = set()
    for tarefas_proj in projetos_dict.values():
        for t in tarefas_proj:
            if t.get('usuario_id'):
                usuario_ids.add(str(t.get('usuario_id')))
    
    print(f"[RELATORIO DEBUG] Total de usuario_ids encontrados: {len(usuario_ids)}")
    print(f"[RELATORIO DEBUG] usuario_ids: {list(usuario_ids)}")
    
    nomes_usuarios = {}
    if usuario_ids:
        try:
            usuarios_resp = supabase.table('usuarios').select('id, nome').in_('id', list(usuario_ids)).execute()
            print(f"[RELATORIO DEBUG] Resposta usuários: {usuarios_resp}")
            if hasattr(usuarios_resp, 'data') and usuarios_resp.data:
                print(f"[RELATORIO DEBUG] Usuários encontrados: {len(usuarios_resp.data)}")
                for u in usuarios_resp.data:
                    nomes_usuarios[str(u['id'])] = u.get('nome', '')
                    print(f"[RELATORIO DEBUG] Usuário: ID={u['id']}, Nome={u.get('nome')}")
            else:
                print("[RELATORIO DEBUG] Nenhum usuário encontrado ou resposta inválida")
        except Exception as e:
            print(f"[RELATORIO DEBUG] Erro ao buscar usuários: {e}")
            pass
    else:
        print("[RELATORIO DEBUG] Nenhum usuario_id para buscar")
    
    print(f"[RELATORIO DEBUG] Mapeamento final nomes_usuarios: {len(nomes_usuarios)} usuários")
    
    # Debug: testar uma busca específica
    if nomes_usuarios:
        primeiro_id = list(nomes_usuarios.keys())[0]
        print(f"[RELATORIO DEBUG] Teste busca: '{primeiro_id}' -> '{nomes_usuarios.get(primeiro_id)}'")
        print(f"[RELATORIO DEBUG] Tipo da chave: {type(primeiro_id)}")
        print(f"[RELATORIO DEBUG] Primeiras 3 chaves: {list(nomes_usuarios.keys())[:3]}")

    # Montar lista de projetos para o template
    projetos_relatorio = []
    for pid, tarefas_proj in projetos_dict.items():
        tarefas_ordenadas = sorted(tarefas_proj, key=lambda t: t.get('ordem', 0))
        tarefas_relatorio = []
        for t in tarefas_ordenadas:
            def formatar_data(data):
                if not data:
                    return ''
                try:
                    return datetime.strptime(data[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    return data
            data_inicio_raw = t.get('data_inicio') or t.get('data_inicio_tarefa', '')
            data_fim_raw = t.get('data_fim') or t.get('data_fim_tarefa', '')
            dias_uteis = ''
            if data_inicio_raw and data_fim_raw:
                try:
                    dias_uteis = dias_uteis_entre_datas(data_inicio_raw, data_fim_raw)
                except Exception:
                    dias_uteis = ''
            responsavel_nome = nomes_usuarios.get(str(t.get('usuario_id')), '')
            tarefas_relatorio.append({
                'nome': t.get('nome', t.get('titulo', 'Tarefa sem nome')),
                'inicio': formatar_data(data_inicio_raw),
                'fim': formatar_data(data_fim_raw),
                'dias_uteis': dias_uteis,
                'duracao': t.get('duracao', ''),
                'colecao': t.get('colecao', ''),
                'responsavel': responsavel_nome,
            })
        projetos_relatorio.append({
            'nome': nomes_projetos.get(pid, 'Projeto'),
            'tarefas': tarefas_relatorio
        })

    # Função para encontrar data de lançamento de um projeto
    def data_inicio_lancamento(projeto):
        datas_lancamento = []
        for tarefa in projeto.get('tarefas', []):
            nome_tarefa = tarefa.get('nome', '').lower().strip()
            # Normalizar o nome da tarefa (remover acentos)
            nome_normalizado = nome_tarefa.replace('ã','a').replace('á','a').replace('â','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('ô','o').replace('ú','u').replace('ç','c')
            if nome_normalizado == 'lancamento' or nome_normalizado == 'lançamento':
                inicio = tarefa.get('inicio', '')
                if inicio:
                    try:
                        # Converter formato DD/MM/YYYY para YYYY-MM-DD para ordenação
                        if '/' in inicio:
                            dia, mes, ano = inicio.split('/')
                            data_ordenacao = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
                            datas_lancamento.append(data_ordenacao)
                        else:
                            datas_lancamento.append(inicio)
                    except Exception:
                        pass
        return min(datas_lancamento) if datas_lancamento else '9999-12-31'

    # Ordenar apenas por data de lançamento
    projetos_ordenados = sorted(projetos_relatorio, key=data_inicio_lancamento)
    
    html = render_template('relatorio_gantt.html', projetos=projetos_ordenados, gantt_base64=gantt_base64)
    return html


@relatorio_bp.route('/exportar_excel', methods=['POST'])
@login_required
def exportar_excel():
    """Exporta relatório completo em Excel com múltiplas abas"""
    try:
        print("🔍 [EXPORT] Iniciando exportação Excel...")
        data = request.get_json()
        projetos_selecionados = data.get('projetos', [])
        incluir_tarefas = True  # Sempre incluir tarefas
        incluir_pastas = True   # Sempre incluir pastas

        print(f"🔍 [EXPORT] Projetos selecionados: {projetos_selecionados}")

        # Verificar se pandas está disponível
        if not PANDAS_AVAILABLE:
            print("❌ [EXPORT] Pandas não disponível")
            return jsonify({
                'success': False,
                'message': 'Pandas nao esta disponivel. Instale com: pip install pandas'
            }), 500

        print("✅ [EXPORT] Pandas disponível, criando buffer...")
        
        # Criar buffer para o arquivo Excel
        output = io.BytesIO()

        # Inicializar variável para gráfico Gantt
        projetos_para_gantt = []

        # Criar writer do pandas para Excel com múltiplas abas
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

            # Adicionar abas de Gantt individuais para cada projeto
            workbook = writer.book

            # Preparar dados dos projetos para as abas de Gantt ANTES de criar as abas
            print("Preparando dados para abas de Gantt...")

            # Buscar dados dos projetos e tarefas para o Gantt
            projetos_gantt = supabase.table('projetos').select('id, nome').execute()
            tarefas_gantt = supabase.table('tarefas').select('*').execute()

            # Processar dados para Gantt sempre, mesmo que vazios
            if projetos_gantt.data and tarefas_gantt.data:
                # Organizar tarefas por projeto
                tarefas_por_projeto = {}
                for tarefa in tarefas_gantt.data:
                    pid = tarefa.get('projeto_id')
                    if pid not in tarefas_por_projeto:
                        tarefas_por_projeto[pid] = []
                    tarefas_por_projeto[pid].append(tarefa)

                # Criar estrutura para o gráfico Gantt
                for projeto in projetos_gantt.data:
                    pid = projeto['id']
                    if pid in tarefas_por_projeto:
                        tarefas_proj = tarefas_por_projeto[pid]
                        tarefas_ordenadas = sorted(tarefas_proj, key=lambda t: t.get('ordem', 0))

                        tarefas_relatorio = []
                        for t in tarefas_ordenadas:
                            def formatar_data_gantt(data):
                                if not data:
                                    return ''
                                try:
                                    return datetime.strptime(data[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                                except Exception:
                                    return data

                            data_inicio_raw = t.get('data_inicio') or t.get('data_inicio_tarefa', '')
                            data_fim_raw = t.get('data_fim') or t.get('data_fim_tarefa', '')

                            tarefas_relatorio.append({
                                'nome': t.get('nome', t.get('titulo', 'Tarefa sem nome')),
                                'inicio': formatar_data_gantt(data_inicio_raw),
                                'fim': formatar_data_gantt(data_fim_raw),
                                'duracao': t.get('duracao', ''),
                                'colecao': t.get('colecao', ''),
                                'responsavel': t.get('responsavel', ''),
                            })

                        projetos_para_gantt.append({
                            'nome': projeto.get('nome', 'Projeto'),
                            'tarefas': tarefas_relatorio
                        })

            if projetos_para_gantt:
                print(f"Criando abas de Gantt para {len(projetos_para_gantt)} projetos...")

                # Lista para rastrear nomes de abas já usados
                nomes_abas_usados = set()
                
                for projeto in projetos_para_gantt:
                    # Sanitizar nome da aba (remover caracteres especiais e limitar tamanho)
                    nome_base = str(projeto['nome'])[:28]  # Reservar espaço para sufixo se necessário
                    nome_aba = ''.join(c for c in nome_base if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    # Garantir unicidade
                    contador = 1
                    nome_final = nome_aba
                    while nome_final in nomes_abas_usados:
                        nome_final = f"{nome_aba[:25]}_{contador}"
                        contador += 1
                    
                    nomes_abas_usados.add(nome_final)
                    
                    try:
                        gantt_sheet = workbook.add_worksheet(nome_final)
                        print(f"Aba de Gantt criada: '{nome_final}'")
                    except Exception as e:
                        print(f"Erro ao criar aba '{nome_final}': {e}")
                        continue
                    gantt_sheet.write('B1', 'Responsável')
                    gantt_sheet.write('C1', 'Início')
                    gantt_sheet.write('D1', 'Fim')
                    gantt_sheet.write('E1', 'Duração')
                    gantt_sheet.write('F1', 'Coleção')
                    gantt_sheet.write('G1', 'Dias até início')

                    # Formato para coluna "Dias até início"
                    formato_cinza = workbook.add_format({'font_color': '#888888'})

                    # Filtrar tarefas válidas
                    tarefas_validas = []
                    for tarefa in projeto.get('tarefas', []):
                        inicio = tarefa.get('inicio', '')
                        duracao = tarefa.get('duracao', 0)
                        try:
                            data_ini = datetime.strptime(inicio, '%d/%m/%Y')
                            if inicio and duracao and data_ini.year > 2000:
                                tarefas_validas.append(tarefa)
                        except Exception:
                            continue

                    if tarefas_validas:
                        # Encontrar data mínima
                        datas_validas = []
                        for tarefa in tarefas_validas:
                            try:
                                datas_validas.append(datetime.strptime(tarefa['inicio'], '%d/%m/%Y'))
                            except Exception:
                                pass
                        data_min = min(datas_validas) if datas_validas else None

                        # Preencher dados
                        row = 1
                        for tarefa in tarefas_validas:
                            inicio = tarefa['inicio']
                            fim = tarefa.get('fim', '')
                            duracao_val = tarefa.get('duracao', '')
                            colecao = tarefa.get('colecao', '')
                            responsavel = tarefa.get('responsavel', '')

                            try:
                                data_ini = datetime.strptime(inicio, '%d/%m/%Y')
                                excel_date = (data_ini - datetime(1899, 12, 30)).days
                            except Exception:
                                excel_date = ''

                            # Escrever dados
                            if str(tarefa['nome']).strip().lower() == 'lançamento':
                                destaque_format = workbook.add_format({'font_color': 'red', 'bold': True})
                                gantt_sheet.write(row, 0, tarefa['nome'], destaque_format)
                            else:
                                gantt_sheet.write(row, 0, tarefa['nome'])

                            gantt_sheet.write(row, 1, responsavel)
                            gantt_sheet.write(row, 2, inicio)
                            gantt_sheet.write(row, 3, fim)

                            try:
                                duracao_int = int(duracao_val)
                                gantt_sheet.write_number(row, 4, duracao_int)
                            except Exception:
                                gantt_sheet.write(row, 4, str(duracao_val))

                            gantt_sheet.write(row, 5, colecao)
                            gantt_sheet.write(row, 6, excel_date, formato_cinza)

                            row += 1

                        # Autoajustar largura das colunas
                        col_widths = [len('Tarefa'), len('Responsável'), len('Início'), len('Fim'), len('Duração'), len('Coleção'), len('Dias até início')]
                        for tarefa in tarefas_validas:
                            col_widths[0] = max(col_widths[0], len(str(tarefa['nome'])))
                            col_widths[1] = max(col_widths[1], len(str(tarefa.get('responsavel', ''))))
                            col_widths[2] = max(col_widths[2], len(str(tarefa.get('inicio', ''))))
                            col_widths[3] = max(col_widths[3], len(str(tarefa.get('fim', ''))))
                            col_widths[4] = max(col_widths[4], len(str(tarefa.get('duracao', ''))))
                            col_widths[5] = max(col_widths[5], len(str(tarefa.get('colecao', ''))))

                        for i, w in enumerate(col_widths):
                            if i == 6:  # Coluna "Dias até início"
                                gantt_sheet.set_column(i, i, 2)
                            elif i == 4:  # Coluna Duração
                                num_format = workbook.add_format({'num_format': '0'})
                                gantt_sheet.set_column(i, i, w + 2, num_format)
                            else:
                                gantt_sheet.set_column(i, i, w + 2)

                        # Criar gráfico de Gantt apenas se há dados
                        if row > 1:
                            try:
                                chart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

                                # Série 1: datas de início
                                chart.add_series({
                                    'name': 'Início',
                                    'categories': [nome_final, 1, 0, row-1, 0],
                                    'values': [nome_final, 1, 6, row-1, 6],
                                    'fill': {'color': '#FFFFFF'},
                                    'border': {'none': True},
                                })

                                # Série 2: duração
                                chart.add_series({
                                    'name': 'Duração',
                                    'categories': [nome_final, 1, 0, row-1, 0],
                                    'values': [nome_final, 1, 4, row-1, 4],
                                    'fill': {'color': '#00C853'},
                                    'border': {'none': True},
                                })

                                chart.set_title({'none': True})
                                chart.set_x_axis({
                                    'num_format': 'dd/mm/yyyy',
                                    'major_gridlines': {'visible': False},
                                    'minor_gridlines': {'visible': False},
                                    'name': '',
                                })
                                chart.set_y_axis({
                                    'reverse': True,
                                    'name': '',
                                    'major_gridlines': {'visible': False},
                                    'minor_gridlines': {'visible': False},
                                })
                                chart.set_legend({'none': True})

                                gantt_sheet.insert_chart('H2', chart, {'x_scale': 3.5, 'y_scale': 3.0})
                                print(f"Gráfico de Gantt criado para aba: {nome_final}")
                            except Exception as e:
                                print(f"Erro ao criar gráfico para aba '{nome_final}': {e}")
                        
                        print(f"Aba de Gantt criada para projeto: {projeto['nome']}")

            # 1. ABA DADOS - Combinar projetos e tarefas em uma única tabela (criada por último)
            print("Criando aba Dados com projetos e tarefas combinados...")

        # Buscar dados dos projetos
        projetos_query = supabase.table('projetos').select('*')
        if len(projetos_selecionados) > 0 and projetos_selecionados != ['todos']:
            projetos_query = projetos_query.in_('id', projetos_selecionados)
        projetos_data = projetos_query.execute()
        print(f"[DADOS] Projetos encontrados: {len(projetos_data.data) if projetos_data.data else 0}")

        # Buscar tarefas
        tarefas_query = supabase.table('tarefas').select('*')
        if len(projetos_selecionados) > 0 and projetos_selecionados != ['todos']:
            tarefas_query = tarefas_query.in_('projeto_id', projetos_selecionados)
        tarefas_data = tarefas_query.execute()
        print(f"[DADOS] Tarefas encontradas: {len(tarefas_data.data) if tarefas_data.data else 0}")

        # Coletar todos os usuario_ids para buscar nomes
        usuario_ids = set()

        # IDs dos projetos
        if projetos_data.data:
            for projeto in projetos_data.data:
                if projeto.get('usuario_id'):
                    usuario_ids.add(str(projeto.get('usuario_id')))

        # IDs das tarefas
        if tarefas_data.data:
            for tarefa in tarefas_data.data:
                if tarefa.get('usuario_id'):
                    usuario_ids.add(str(tarefa.get('usuario_id')))

        # Buscar nomes dos usuários
        nomes_usuarios = {}
        if usuario_ids:
            try:
                usuarios_data = supabase.table('usuarios').select('id, nome').in_('id', list(usuario_ids)).execute()
                if usuarios_data.data:
                    for usuario in usuarios_data.data:
                        nomes_usuarios[str(usuario['id'])] = usuario.get('nome', '')
                print(f"[DADOS] Nomes de usuários carregados: {len(nomes_usuarios)}")
            except Exception as e:
                print(f"[DADOS] Erro ao buscar nomes de usuários: {e}")

        # Combinar dados de projetos e tarefas
        dados_combinados = []

        # Adicionar projetos sem tarefas
        if projetos_data.data:
            for projeto in projetos_data.data:
                projeto_nome = projeto.get('nome', 'Projeto sem nome')
                usuario_nome = nomes_usuarios.get(str(projeto.get('usuario_id', '')), '')

                dados_combinados.append({
                    'Projeto': projeto_nome,
                    'Tarefa': '',
                    'Responsável': usuario_nome,
                    'Inicio': projeto.get('data_inicio', ''),
                    'Fim': projeto.get('data_fim', ''),
                    'Dias Úteis': '',
                    'Duração': '',
                    'Coleção': ''
                })

        # Adicionar tarefas
        if tarefas_data.data:
            for tarefa in tarefas_data.data:
                projeto_nome = 'Projeto não encontrado'
                usuario_nome = nomes_usuarios.get(str(tarefa.get('usuario_id', '')), '')

                # Encontrar nome do projeto
                if projetos_data.data:
                    for p in projetos_data.data:
                        if p['id'] == tarefa.get('projeto_id'):
                            projeto_nome = p.get('nome', 'Projeto sem nome')
                            break

                # Calcular dias úteis
                try:
                    data_inicio = tarefa.get('data_inicio', '')
                    data_fim = tarefa.get('data_fim', '')
                    if data_inicio and data_fim:
                        dias_uteis_calc = dias_uteis_entre_datas(data_inicio, data_fim)
                    else:
                        dias_uteis_calc = ''
                except:
                    dias_uteis_calc = ''

                dados_combinados.append({
                    'Projeto': projeto_nome,
                    'Tarefa': tarefa.get('titulo') or tarefa.get('nome', ''),
                    'Responsável': nomes_usuarios.get(str(tarefa.get('usuario_id', '')), ''),
                    'Inicio': tarefa.get('data_inicio', ''),
                    'Fim': tarefa.get('data_fim', ''),
                    'Dias Úteis': dias_uteis_calc if dias_uteis_calc != '' else '',
                    'Duração': tarefa.get('duracao', ''),
                    'Coleção': tarefa.get('colecao', '')
                })

        if dados_combinados:
            print(f"[DADOS] Criando aba Dados com {len(dados_combinados)} registros")
            print(f"[DADOS] Colunas: {[d.keys() for d in dados_combinados[:1]]}")
            df_dados = pd.DataFrame(dados_combinados)
            print(f"[DADOS] DataFrame shape: {df_dados.shape}")
            print(f"[DADOS] DataFrame columns: {list(df_dados.columns)}")

            # Formatar datas
            colunas_data = ['Inicio', 'Fim']
            for col in colunas_data:
                if col in df_dados.columns:
                    df_dados[col] = pd.to_datetime(df_dados[col], errors='coerce').dt.strftime('%d/%m/%Y')

            # Substituir NaN por strings vazias
            df_dados = df_dados.fillna('')

            # Usar workbook diretamente para garantir que a aba seja criada
            workbook = writer.book
            worksheet = workbook.add_worksheet('Dados')
            print(f"[DADOS] Aba 'Dados' criada no workbook")

            # Escrever cabeçalhos
            headers = list(df_dados.columns)
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            # Escrever dados
            for row, data_row in enumerate(df_dados.itertuples(index=False), 1):
                for col, value in enumerate(data_row):
                    worksheet.write(row, col, str(value) if value is not None else '')

            print(f"Exportados {len(dados_combinados)} registros na aba Dados")
        else:
            print("[DADOS] Nenhum dado encontrado para criar aba Dados")

        # Buscar dados dos projetos
        projetos_query = supabase.table('projetos').select('*')
        if len(projetos_selecionados) > 0 and projetos_selecionados != ['todos']:
            projetos_query = projetos_query.in_('id', projetos_selecionados)
        projetos_data = projetos_query.execute()
        print(f"[DADOS] Projetos encontrados: {len(projetos_data.data) if projetos_data.data else 0}")

        # Buscar tarefas
        tarefas_query = supabase.table('tarefas').select('*')
        if len(projetos_selecionados) > 0 and projetos_selecionados != ['todos']:
            tarefas_query = tarefas_query.in_('projeto_id', projetos_selecionados)
        tarefas_data = tarefas_query.execute()
        print(f"[DADOS] Tarefas encontradas: {len(tarefas_data.data) if tarefas_data.data else 0}")

        # Coletar todos os usuario_ids para buscar nomes
        usuario_ids = set()

        # IDs dos projetos
        if projetos_data.data:
            for projeto in projetos_data.data:
                if projeto.get('usuario_id'):
                    usuario_ids.add(str(projeto.get('usuario_id')))

        # IDs das tarefas
        if tarefas_data.data:
            for tarefa in tarefas_data.data:
                if tarefa.get('usuario_id'):
                    usuario_ids.add(str(tarefa.get('usuario_id')))

        # Buscar nomes dos usuários
        nomes_usuarios = {}
        if usuario_ids:
            usuarios_resp = supabase.table('usuarios').select('id, nome').in_('id', list(usuario_ids)).execute()
            if usuarios_resp.data:
                nomes_usuarios = {str(u['id']): u.get('nome', '') for u in usuarios_resp.data}
                print(f"[DADOS] Usuários encontrados: {len(nomes_usuarios)} - {list(nomes_usuarios.values())}")
            else:
                print("[DADOS] Nenhum usuário encontrado")

        # Criar mapeamento de nomes de projetos
        projetos_nomes = {}
        if projetos_data.data:
            projetos_nomes = {p['id']: p['nome'] for p in projetos_data.data}

        # Combinar dados de projetos e tarefas com apenas as colunas solicitadas
        dados_combinados = []

        # Adicionar projetos (com campos vazios para tarefa)
        if projetos_data.data:
            for projeto in projetos_data.data:
                responsavel_nome = nomes_usuarios.get(str(projeto.get('usuario_id', '')), '')
                dados_combinados.append({
                    'Projeto': projeto.get('nome', ''),
                    'Tarefa': '',  # Campo vazio para projetos
                    'Responsável': responsavel_nome,
                    'Inicio': projeto.get('data_inicio', ''),
                    'Fim': projeto.get('data_fim', ''),
                    'Dias Úteis': '',  # Campo vazio para projetos
                    'Duração': '',  # Campo vazio para projetos
                    'Coleção': ''  # Campo vazio para projetos
                })

        # Adicionar tarefas
        if tarefas_data.data:
            for tarefa in tarefas_data.data:
                projeto_nome = projetos_nomes.get(tarefa.get('projeto_id'), 'N/A')

                # Calcular dias úteis se possível
                dias_uteis = ''
                try:
                    if tarefa.get('data_inicio') and tarefa.get('data_fim'):
                        data_inicio = pd.to_datetime(tarefa.get('data_inicio'))
                        data_fim = pd.to_datetime(tarefa.get('data_fim'))
                        # Calcular dias úteis aproximados (simples)
                        dias_totais = (data_fim - data_inicio).days
                        # Aproximação: considerar 5 dias úteis por semana
                        semanas = dias_totais // 7
                        dias_restantes = dias_totais % 7
                        dias_uteis_calc = semanas * 5 + min(dias_restantes, 5)
                        dias_uteis = dias_uteis_calc if dias_uteis_calc > 0 else ''
                except:
                    dias_uteis = ''

                dados_combinados.append({
                    'Projeto': projeto_nome,
                    'Tarefa': tarefa.get('titulo') or tarefa.get('nome', ''),
                    'Responsável': nomes_usuarios.get(str(tarefa.get('usuario_id', '')), ''),
                    'Inicio': tarefa.get('data_inicio', ''),
                    'Fim': tarefa.get('data_fim', ''),
                    'Dias Úteis': dias_uteis,
                    'Duração': tarefa.get('duracao', ''),
                    'Coleção': tarefa.get('colecao', '')
                })

        if dados_combinados:
            print(f"[DADOS] Criando aba Dados com {len(dados_combinados)} registros")
            print(f"[DADOS] Colunas: {[d.keys() for d in dados_combinados[:1]]}")
            df_dados = pd.DataFrame(dados_combinados)
            print(f"[DADOS] DataFrame shape: {df_dados.shape}")
            print(f"[DADOS] DataFrame columns: {list(df_dados.columns)}")

            # Formatar datas
            colunas_data = ['Inicio', 'Fim']
            for col in colunas_data:
                if col in df_dados.columns:
                    df_dados[col] = pd.to_datetime(df_dados[col], errors='coerce').dt.strftime('%d/%m/%Y')

            # Substituir NaN por strings vazias
            df_dados = df_dados.fillna('')

            # Usar workbook diretamente para garantir que a aba seja criada
            workbook = writer.book
            worksheet = workbook.add_worksheet('Dados')
            print(f"[DADOS] Aba 'Dados' criada no workbook")
            
            # Escrever cabeçalhos
            headers = list(df_dados.columns)
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Escrever dados
            for row, data_row in enumerate(df_dados.itertuples(index=False), 1):
                for col, value in enumerate(data_row):
                    worksheet.write(row, col, str(value) if value is not None else '')
            
            print(f"Exportados {len(dados_combinados)} registros na aba Dados")
        else:
            print("[DADOS] Nenhum dado encontrado para criar aba Dados")

        # Preparar arquivo para download
        output.seek(0)

        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'relatorio_projetos_{timestamp}.xlsx'

        print(f"✅ [EXPORT] Arquivo Excel criado: {filename}, tamanho: {len(output.getvalue())} bytes")

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"❌ [EXPORT] Erro ao exportar Excel: {str(e)}")
        import traceback
        print(f"❌ [EXPORT] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Erro ao exportar relatorio: {str(e)}'
        }), 500


@relatorio_bp.route('/exportar_csv', methods=['POST'])
@login_required
def exportar_csv():
    """Exporta apenas projetos em CSV"""
    try:
        data = request.get_json()
        projetos_selecionados = data.get('projetos', [])
        
        print(f"🔍 Projetos selecionados para CSV: {projetos_selecionados}")
        
        # Verificar se pandas está disponível
        if not PANDAS_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'Pandas não está disponível. Instale com: pip install pandas'
            }), 500
        
        # Buscar dados dos projetos
        projetos_query = supabase.table('projetos').select('*')
        
        # Aplicar filtro se projetos específicos foram selecionados
        if len(projetos_selecionados) > 0 and projetos_selecionados != ['todos']:
            projetos_query = projetos_query.in_('id', projetos_selecionados)
        
        projetos_data = projetos_query.execute()
        
        if not projetos_data.data:
            return jsonify({
                'success': False,
                'message': 'Nenhum projeto encontrado para exportação'
            }), 404
        
        # Converter para DataFrame
        df_projetos = pd.DataFrame(projetos_data.data)
        
        # Reorganizar colunas
        colunas_desejadas = ['id', 'nome', 'cliente', 'descricao', 'status', 'prioridade', 
                           'data_inicio', 'data_fim', 'orcamento', 'progresso', 'responsavel', 
                           'observacoes', 'created_at', 'updated_at']
        
        colunas_existentes = [col for col in colunas_desejadas if col in df_projetos.columns]
        df_export = df_projetos[colunas_existentes].copy()
        
        # Criar buffer para CSV
        output = io.BytesIO()
        df_export.to_csv(output, index=False, encoding='utf-8-sig', sep=';')
        output.seek(0)
        
        # Nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'projetos_{timestamp}.csv'
        
        print(f"✅ Arquivo CSV criado: {filename} com {len(df_export)} projetos")
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"❌ Erro ao exportar CSV: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao exportar CSV: {str(e)}'
        }), 500


@relatorio_bp.route('/datas-conflitantes')
@login_required
def datas_conflitantes():
    """Página para identificar e mostrar datas conflitantes no sistema"""
    try:
        # Buscar usuários para o filtro
        try:
            usuarios_data = supabase.table('usuarios').select('id, nome').execute()
            usuarios = usuarios_data.data if usuarios_data.data else []
        except Exception as e:
            print(f"Erro ao consultar usuários: {e}")
            usuarios = []

        # Verificar se há filtro de responsáveis (aceita ID numérico ou string/UUID)
        responsaveis_ids = [rid for rid in request.args.getlist('responsaveis') if rid]

        def normalizar_resp(valor):
            if valor is None:
                return None
            try:
                return int(valor)
            except (TypeError, ValueError):
                return str(valor).strip()

        conflitos = {}
        calcular_conflitos = True  # Sempre calcular conflitos agora

        # Buscar todos os projetos e tarefas
        try:
            projetos_data = supabase.table('projetos').select('id, nome, data_inicio, data_fim, status, usuario_id').execute()
            projetos = projetos_data.data if projetos_data.data else []
        except Exception as e:
            print(f"Erro ao buscar projetos: {str(e)}")
            projetos = []

        try:
            tarefas_data = supabase.table('tarefas').select('id, nome, data_inicio, data_fim, projeto_id, usuario_id, status, ordem').execute()
            tarefas = tarefas_data.data if tarefas_data.data else []
        except Exception as e:
            print(f"Erro ao buscar tarefas: {str(e)}")
            tarefas = []

        # Detectar conflitos
        conflitos = detectar_conflitos_datas(projetos, tarefas)

        # Aplicar filtro de responsáveis apenas se houver seleção
        if responsaveis_ids:
            # Aplicar filtro de responsáveis
            responsaveis_normalizados = [normalizar_resp(rid) for rid in responsaveis_ids]
            responsaveis_normalizados = [rid for rid in responsaveis_normalizados if rid is not None]
            if responsaveis_normalizados:
                conflitos = filtrar_conflitos_por_responsaveis(conflitos, responsaveis_normalizados, tarefas)
        # Se responsaveis_ids estiver vazio, mantém todos os conflitos (sem filtrar)

        return render_template('datas_conflitantes.html',
                             conflitos=conflitos,
                             usuarios=usuarios,
                             responsaveis_selecionados=responsaveis_ids,
                             calcular_conflitos=calcular_conflitos)

    except Exception as e:
        print(f"Erro ao carregar datas conflitantes: {str(e)}")
        return render_template('datas_conflitantes.html',
                             conflitos={
                                 'projetos_inconsistentes': [],
                                 'tarefas_fora_projeto': [],
                                 'tarefas_sobrepostas': [],
                                 'tarefas_sobrepostas_entre_projetos': [],
                                 'datas_invalidas': [],
                                 'predecessoras_conflito': []
                             },
                             usuarios=[],
                             responsaveis_selecionados=[],
                             erro=str(e))
        """
        Detecta diversos tipos de conflitos de datas no sistema
        
        Args:
            projetos (list): Lista de projetos
            tarefas (list): Lista de tarefas
        
        Returns:
            dict: Dicionário com os diferentes tipos de conflitos encontrados
        """
        def formatar_data_brasileira(data_iso):
            """
            Converte data do formato ISO (YYYY-MM-DD) para formato brasileiro (DD/MM/YYYY)
            """
            try:
                if not data_iso:
                    return ''
                # Remove a parte de tempo se existir
                data_str = data_iso.split('T')[0]
                # Converte de YYYY-MM-DD para DD/MM/YYYY
                data_dt = datetime.strptime(data_str, '%Y-%m-%d')
                return data_dt.strftime('%d/%m/%Y')
            except (ValueError, AttributeError):
                return data_iso if data_iso else ''
        
        conflitos = {
        'projetos_inconsistentes': [],
        'tarefas_fora_projeto': [],
        'tarefas_sobrepostas': [],
        'tarefas_sobrepostas_entre_projetos': [],
        'datas_invalidas': [],
        'predecessoras_conflito': []
    }
    
    # 1. Projetos com datas inconsistentes (data fim anterior à data início)
    for projeto in projetos:
        data_inicio = projeto.get('data_inicio')
        data_fim = projeto.get('data_fim')
        
        if data_inicio and data_fim:
            try:
                inicio_dt = datetime.strptime(data_inicio.split('T')[0], '%Y-%m-%d')
                fim_dt = datetime.strptime(data_fim.split('T')[0], '%Y-%m-%d')
                
                if fim_dt < inicio_dt:
                    conflitos['projetos_inconsistentes'].append({
                        'tipo': 'Projeto com data fim anterior à data início',
                        'projeto_nome': projeto.get('nome', 'N/A'),
                        'projeto_id': projeto.get('id'),
                        'data_inicio': formatar_data_brasileira(data_inicio),
                        'data_fim': formatar_data_brasileira(data_fim),
                        'descricao': f"Data fim ({formatar_data_brasileira(data_fim)}) é anterior à data início ({formatar_data_brasileira(data_inicio)})"
                    })
            except (ValueError, AttributeError) as e:
                conflitos['datas_invalidas'].append({
                    'tipo': 'Data inválida em projeto',
                    'projeto_nome': projeto.get('nome', 'N/A'),
                    'projeto_id': projeto.get('id'),
                    'descricao': f"Erro ao processar datas: {str(e)}"
                })
    
    # 2. Tarefas com datas fora do período do projeto
    projeto_dict = {p['id']: p for p in projetos}
    
    for tarefa in tarefas:
        projeto_id = tarefa.get('projeto_id')
        tarefa_inicio = tarefa.get('data_inicio')
        tarefa_fim = tarefa.get('data_fim')
        
        if projeto_id in projeto_dict and tarefa_inicio and tarefa_fim:
            projeto = projeto_dict[projeto_id]
            projeto_inicio = projeto.get('data_inicio')
            projeto_fim = projeto.get('data_fim')
            
            if projeto_inicio and projeto_fim:
                try:
                    tarefa_inicio_dt = datetime.strptime(tarefa_inicio.split('T')[0], '%Y-%m-%d')
                    tarefa_fim_dt = datetime.strptime(tarefa_fim.split('T')[0], '%Y-%m-%d')
                    projeto_inicio_dt = datetime.strptime(projeto_inicio.split('T')[0], '%Y-%m-%d')
                    projeto_fim_dt = datetime.strptime(projeto_fim.split('T')[0], '%Y-%m-%d')
                    
                    if tarefa_inicio_dt < projeto_inicio_dt or tarefa_fim_dt > projeto_fim_dt:
                        conflitos['tarefas_fora_projeto'].append({
                            'tipo': 'Tarefa fora do período do projeto',
                            'projeto_nome': projeto.get('nome', 'N/A'),
                            'projeto_id': projeto_id,
                            'tarefa_nome': tarefa.get('nome', 'N/A'),
                            'tarefa_id': tarefa.get('id'),
                            'tarefa_inicio': formatar_data_brasileira(tarefa_inicio),
                            'tarefa_fim': formatar_data_brasileira(tarefa_fim),
                            'projeto_inicio': formatar_data_brasileira(projeto_inicio),
                            'projeto_fim': formatar_data_brasileira(projeto_fim),
                            'descricao': f"Tarefa ({formatar_data_brasileira(tarefa_inicio)} - {formatar_data_brasileira(tarefa_fim)}) está fora do período do projeto ({formatar_data_brasileira(projeto_inicio)} - {formatar_data_brasileira(projeto_fim)})"
                        })
                except (ValueError, AttributeError) as e:
                    conflitos['datas_invalidas'].append({
                        'tipo': 'Data inválida em tarefa',
                        'projeto_nome': projeto.get('nome', 'N/A'),
                        'tarefa_nome': tarefa.get('nome', 'N/A'),
                        'tarefa_id': tarefa.get('id'),
                        'descricao': f"Erro ao processar datas da tarefa: {str(e)}"
                    })
    
    # 3. Tarefas com datas inconsistentes (data fim anterior à data início)
    for tarefa in tarefas:
        tarefa_inicio = tarefa.get('data_inicio')
        tarefa_fim = tarefa.get('data_fim')
        
        if tarefa_inicio and tarefa_fim:
            try:
                inicio_dt = datetime.strptime(tarefa_inicio.split('T')[0], '%Y-%m-%d')
                fim_dt = datetime.strptime(tarefa_fim.split('T')[0], '%Y-%m-%d')
                
                if fim_dt < inicio_dt:
                    projeto_nome = 'N/A'
                    projeto_id = tarefa.get('projeto_id')
                    if projeto_id in projeto_dict:
                        projeto_nome = projeto_dict[projeto_id].get('nome', 'N/A')
                    
                    conflitos['datas_invalidas'].append({
                        'tipo': 'Tarefa com data fim anterior à data início',
                        'projeto_nome': projeto_nome,
                        'projeto_id': projeto_id,
                        'tarefa_nome': tarefa.get('nome', 'N/A'),
                        'tarefa_id': tarefa.get('id'),
                        'tarefa_inicio': tarefa_inicio.split('T')[0],
                        'tarefa_fim': tarefa_fim.split('T')[0],
                        'descricao': f"Data fim ({tarefa_fim.split('T')[0]}) é anterior à data início ({tarefa_inicio.split('T')[0]})"
                    })
            except (ValueError, AttributeError):
                continue
    
    # 4. Detectar problemas com predecessoras
    for tarefa in tarefas:
        predecessoras = tarefa.get('predecessoras')
        if predecessoras:
            try:
                # Analisar predecessoras (formato: "1FS,2SS+3d,3FF-1d")  
                pred_list = [p.strip() for p in predecessoras.split(',') if p.strip()]
                tarefa_ordem = tarefa.get('ordem', 0)
                
                for pred in pred_list:
                    # Extrair número da tarefa predecessora
                    import re
                    match = re.match(r'^(\d+)', pred)
                    if match:
                        pred_ordem = int(match.group(1))
                        
                        # Verificar se predecessora existe
                        pred_existe = any(t.get('ordem') == pred_ordem and t.get('projeto_id') == tarefa.get('projeto_id') for t in tarefas)
                        
                        if not pred_existe:
                            projeto_nome = 'N/A'
                            projeto_id = tarefa.get('projeto_id')
                            if projeto_id in projeto_dict:
                                projeto_nome = projeto_dict[projeto_id].get('nome', 'N/A')
                            
                            conflitos['predecessoras_conflito'].append({
                                'tipo': 'Predecessora inexistente',
                                'projeto_nome': projeto_nome,
                                'projeto_id': projeto_id,
                                'tarefa_nome': tarefa.get('nome', 'N/A'),
                                'tarefa_id': tarefa.get('id'),
                                'tarefa_ordem': tarefa_ordem,
                                'predecessora_ordem': pred_ordem,
                                'descricao': f"Tarefa {tarefa_ordem} referencia predecessora {pred_ordem} que não existe"
                            })
                        

                            
            except Exception as e:
                continue
    
    # 5. Detectar sobreposições entre tarefas do mesmo projeto
    tarefas_por_projeto = {}
    for tarefa in tarefas:
        projeto_id = tarefa.get('projeto_id')
        if projeto_id:
            if projeto_id not in tarefas_por_projeto:
                tarefas_por_projeto[projeto_id] = []
            tarefas_por_projeto[projeto_id].append(tarefa)
    
    for projeto_id, tarefas_projeto in tarefas_por_projeto.items():
        projeto_nome = projeto_dict.get(projeto_id, {}).get('nome', 'N/A')
        
        for i, tarefa1 in enumerate(tarefas_projeto):
            for tarefa2 in tarefas_projeto[i+1:]:
                if verificar_sobreposicao_tarefas(tarefa1, tarefa2):
                    conflitos['tarefas_sobrepostas'].append({
                        'tipo': 'Tarefas sobrepostas no mesmo projeto',
                        'projeto_nome': projeto_nome,
                        'projeto_id': projeto_id,
                        'tarefa1_nome': tarefa1.get('nome', 'N/A'),
                        'tarefa1_id': tarefa1.get('id'),
                        'tarefa1_responsavel': tarefa1.get('usuario_id', ''),
                        'tarefa1_inicio': formatar_data_brasileira(tarefa1.get('data_inicio')),
                        'tarefa1_fim': formatar_data_brasileira(tarefa1.get('data_fim')),
                        'tarefa2_nome': tarefa2.get('nome', 'N/A'),
                        'tarefa2_id': tarefa2.get('id'),
                        'tarefa2_responsavel': tarefa2.get('usuario_id', ''),
                        'tarefa2_inicio': formatar_data_brasileira(tarefa2.get('data_inicio')),
                        'tarefa2_fim': formatar_data_brasileira(tarefa2.get('data_fim')),
                        'descricao': f"As tarefas '{tarefa1.get('nome', 'N/A')}' e '{tarefa2.get('nome', 'N/A')}' possuem datas sobrepostas"
                    })

    # 6. Detectar sobreposições entre tarefas de projetos diferentes
    projetos_ids = list(tarefas_por_projeto.keys())
    for i, projeto_id1 in enumerate(projetos_ids):
        for projeto_id2 in projetos_ids[i+1:]:
            projeto_nome1 = projeto_dict.get(projeto_id1, {}).get('nome', 'N/A')
            projeto_nome2 = projeto_dict.get(projeto_id2, {}).get('nome', 'N/A')
            
            for tarefa1 in tarefas_por_projeto[projeto_id1]:
                for tarefa2 in tarefas_por_projeto[projeto_id2]:
                    if verificar_sobreposicao_tarefas(tarefa1, tarefa2):
                        conflitos['tarefas_sobrepostas_entre_projetos'].append({
                            'tipo': 'Tarefas sobrepostas entre projetos',
                            'projeto1_nome': projeto_nome1,
                            'projeto1_id': projeto_id1,
                            'projeto2_nome': projeto_nome2,
                            'projeto2_id': projeto_id2,
                            'tarefa1_nome': tarefa1.get('nome', 'N/A'),
                            'tarefa1_id': tarefa1.get('id'),
                            'tarefa1_responsavel': tarefa1.get('usuario_id', ''),
                            'tarefa1_inicio': formatar_data_brasileira(tarefa1.get('data_inicio')),
                            'tarefa1_fim': formatar_data_brasileira(tarefa1.get('data_fim')),
                            'tarefa2_nome': tarefa2.get('nome', 'N/A'),
                            'tarefa2_id': tarefa2.get('id'),
                            'tarefa2_responsavel': tarefa2.get('usuario_id', ''),
                            'tarefa2_inicio': formatar_data_brasileira(tarefa2.get('data_inicio')),
                            'tarefa2_fim': formatar_data_brasileira(tarefa2.get('data_fim')),
                            'descricao': f"A tarefa '{tarefa1.get('nome', 'N/A')}' do projeto '{projeto_nome1}' sobrepõe com a tarefa '{tarefa2.get('nome', 'N/A')}' do projeto '{projeto_nome2}'"
                        })
    
    return conflitos


def verificar_sobreposicao_tarefas(tarefa1, tarefa2):
    """
    Verifica se duas tarefas possuem datas sobrepostas
    
    Args:
        tarefa1 (dict): Primeira tarefa
        tarefa2 (dict): Segunda tarefa
    
    Returns:
        bool: True se há sobreposição, False caso contrário
    """
    try:
        inicio1 = tarefa1.get('data_inicio')
        fim1 = tarefa1.get('data_fim')
        inicio2 = tarefa2.get('data_inicio')
        fim2 = tarefa2.get('data_fim')
        
        if not all([inicio1, fim1, inicio2, fim2]):
            return False
        
        # Converter para datetime
        inicio1_dt = datetime.strptime(inicio1.split('T')[0], '%Y-%m-%d')
        fim1_dt = datetime.strptime(fim1.split('T')[0], '%Y-%m-%d')
        inicio2_dt = datetime.strptime(inicio2.split('T')[0], '%Y-%m-%d')
        fim2_dt = datetime.strptime(fim2.split('T')[0], '%Y-%m-%d')
        
        # Verificar sobreposição: há sobreposição se uma tarefa não termina antes da outra começar
        return not (fim1_dt < inicio2_dt or fim2_dt < inicio1_dt)
        
    except (ValueError, AttributeError):
        return False


def filtrar_conflitos_por_responsaveis(conflitos, responsaveis_ids, tarefas):
    """
    Filtra conflitos baseado nos responsáveis selecionados

    Args:
        conflitos (dict): Dicionário com todos os conflitos
        responsaveis_ids (list): Lista de IDs dos responsáveis selecionados (ints)
        tarefas (list): Lista de todas as tarefas

    Returns:
        dict: Dicionário com conflitos filtrados
    """
    # Normalizar IDs (aceita int ou string/UUID) e preparar conjuntos
    def normalizar_resp(valor):
        if valor is None:
            return None
        try:
            return int(valor)
        except (TypeError, ValueError):
            return str(valor).strip()

    responsaveis_normalizados = [normalizar_resp(r) for r in responsaveis_ids if r is not None]
    responsaveis_set = set(r for r in responsaveis_normalizados if r is not None)

    # Dicionário de tarefas por ID para recuperar responsável
    tarefas_dict = {t.get('id'): t for t in tarefas}

    def tarefa_responsavel(tarefa_id):
        tarefa = tarefas_dict.get(tarefa_id)
        return normalizar_resp(tarefa.get('usuario_id')) if tarefa else None

    conflitos_filtrados = {
        'projetos_inconsistentes': [],
        'tarefas_fora_projeto': [],
        'tarefas_sobrepostas': [],
        'tarefas_sobrepostas_entre_projetos': [],
        'datas_invalidas': [],
        'predecessoras_conflito': []
    }

    # --- Tarefas sobrepostas (mesmo projeto) ---
    for conflito in conflitos['tarefas_sobrepostas']:
        resp1 = normalizar_resp(conflito.get('tarefa1_responsavel'))
        resp2 = normalizar_resp(conflito.get('tarefa2_responsavel'))

        if len(responsaveis_set) == 1:
            alvo = next(iter(responsaveis_set))
            if resp1 == alvo or resp2 == alvo:
                conflitos_filtrados['tarefas_sobrepostas'].append(conflito)
        else:
            if resp1 in responsaveis_set and resp2 in responsaveis_set:
                conflitos_filtrados['tarefas_sobrepostas'].append(conflito)

    # --- Tarefas sobrepostas (entre projetos) ---
    for conflito in conflitos['tarefas_sobrepostas_entre_projetos']:
        resp1 = normalizar_resp(conflito.get('tarefa1_responsavel'))
        resp2 = normalizar_resp(conflito.get('tarefa2_responsavel'))

        if len(responsaveis_set) == 1:
            alvo = next(iter(responsaveis_set))
            if resp1 == alvo or resp2 == alvo:
                conflitos_filtrados['tarefas_sobrepostas_entre_projetos'].append(conflito)
        else:
            if resp1 in responsaveis_set and resp2 in responsaveis_set:
                conflitos_filtrados['tarefas_sobrepostas_entre_projetos'].append(conflito)

    # --- Tarefas fora do projeto ---
    for conflito in conflitos['tarefas_fora_projeto']:
        resp = tarefa_responsavel(conflito.get('tarefa_id'))
        if resp in responsaveis_set:
            conflitos_filtrados['tarefas_fora_projeto'].append(conflito)

    # --- Datas inválidas ---
    for conflito in conflitos['datas_invalidas']:
        tarefa_id = conflito.get('tarefa_id')
        if tarefa_id is None:
            continue  # Descartar itens sem responsável associado
        resp = tarefa_responsavel(tarefa_id)
        if resp in responsaveis_set:
            conflitos_filtrados['datas_invalidas'].append(conflito)

    # --- Predecessoras ---
    for conflito in conflitos['predecessoras_conflito']:
        resp = tarefa_responsavel(conflito.get('tarefa_id'))
        if resp in responsaveis_set:
            conflitos_filtrados['predecessoras_conflito'].append(conflito)

    # Projetos inconsistentes não são ligados a responsáveis; omitir quando há filtro aplicado

    return conflitos_filtrados


def detectar_conflitos_datas(projetos, tarefas):
    """
    Detecta diversos tipos de conflitos de datas no sistema
    
    Args:
        projetos (list): Lista de projetos
        tarefas (list): Lista de tarefas
    
    Returns:
        dict: Dicionário com os diferentes tipos de conflitos encontrados
    """
    def formatar_data_brasileira(data_iso):
        """
        Converte data do formato ISO (YYYY-MM-DD) para formato brasileiro (DD/MM/YYYY)
        """
        try:
            if not data_iso:
                return ''
            # Remove a parte de tempo se existir
            data_str = data_iso.split('T')[0]
            # Converte de YYYY-MM-DD para DD/MM/YYYY
            data_dt = datetime.strptime(data_str, '%Y-%m-%d')
            return data_dt.strftime('%d/%m/%Y')
        except (ValueError, AttributeError):
            return data_iso if data_iso else ''
    
    conflitos = {
        'projetos_inconsistentes': [],
        'tarefas_fora_projeto': [],
        'tarefas_sobrepostas': [],
        'tarefas_sobrepostas_entre_projetos': [],
        'datas_invalidas': [],
        'predecessoras_conflito': []
    }
    
    # 1. Projetos com datas inconsistentes (data fim anterior à data início)
    for projeto in projetos:
        data_inicio = projeto.get('data_inicio')
        data_fim = projeto.get('data_fim')
        
        if data_inicio and data_fim:
            try:
                inicio_dt = datetime.strptime(data_inicio.split('T')[0], '%Y-%m-%d')
                fim_dt = datetime.strptime(data_fim.split('T')[0], '%Y-%m-%d')
                
                if fim_dt < inicio_dt:
                    conflitos['projetos_inconsistentes'].append({
                        'tipo': 'Projeto com data fim anterior à data início',
                        'projeto_nome': projeto.get('nome', 'N/A'),
                        'projeto_id': projeto.get('id'),
                        'data_inicio': formatar_data_brasileira(data_inicio),
                        'data_fim': formatar_data_brasileira(data_fim),
                        'descricao': f"Data fim ({formatar_data_brasileira(data_fim)}) é anterior à data início ({formatar_data_brasileira(data_inicio)})"
                    })
            except (ValueError, AttributeError) as e:
                conflitos['datas_invalidas'].append({
                    'tipo': 'Data inválida em projeto',
                    'projeto_nome': projeto.get('nome', 'N/A'),
                    'projeto_id': projeto.get('id'),
                    'descricao': f"Erro ao processar datas: {str(e)}"
                })
    
    # 2. Tarefas com datas fora do período do projeto
    projeto_dict = {p['id']: p for p in projetos}
    
    for tarefa in tarefas:
        projeto_id = tarefa.get('projeto_id')
        tarefa_inicio = tarefa.get('data_inicio')
        tarefa_fim = tarefa.get('data_fim')
        
        if projeto_id in projeto_dict and tarefa_inicio and tarefa_fim:
            projeto = projeto_dict[projeto_id]
            projeto_inicio = projeto.get('data_inicio')
            projeto_fim = projeto.get('data_fim')
            
            if projeto_inicio and projeto_fim:
                try:
                    tarefa_inicio_dt = datetime.strptime(tarefa_inicio.split('T')[0], '%Y-%m-%d')
                    tarefa_fim_dt = datetime.strptime(tarefa_fim.split('T')[0], '%Y-%m-%d')
                    projeto_inicio_dt = datetime.strptime(projeto_inicio.split('T')[0], '%Y-%m-%d')
                    projeto_fim_dt = datetime.strptime(projeto_fim.split('T')[0], '%Y-%m-%d')
                    
                    if tarefa_inicio_dt < projeto_inicio_dt or tarefa_fim_dt > projeto_fim_dt:
                        conflitos['tarefas_fora_projeto'].append({
                            'tipo': 'Tarefa fora do período do projeto',
                            'projeto_nome': projeto.get('nome', 'N/A'),
                            'projeto_id': projeto_id,
                            'tarefa_nome': tarefa.get('nome', 'N/A'),
                            'tarefa_id': tarefa.get('id'),
                            'tarefa_inicio': formatar_data_brasileira(tarefa_inicio),
                            'tarefa_fim': formatar_data_brasileira(tarefa_fim),
                            'projeto_inicio': formatar_data_brasileira(projeto_inicio),
                            'projeto_fim': formatar_data_brasileira(projeto_fim),
                            'descricao': f"Tarefa ({formatar_data_brasileira(tarefa_inicio)} - {formatar_data_brasileira(tarefa_fim)}) está fora do período do projeto ({formatar_data_brasileira(projeto_inicio)} - {formatar_data_brasileira(projeto_fim)})"
                        })
                except (ValueError, AttributeError) as e:
                    conflitos['datas_invalidas'].append({
                        'tipo': 'Data inválida em tarefa',
                        'projeto_nome': projeto.get('nome', 'N/A'),
                        'tarefa_nome': tarefa.get('nome', 'N/A'),
                        'tarefa_id': tarefa.get('id'),
                        'descricao': f"Erro ao processar datas da tarefa: {str(e)}"
                    })
    
    # 3. Tarefas com datas inconsistentes (data fim anterior à data início)
    for tarefa in tarefas:
        tarefa_inicio = tarefa.get('data_inicio')
        tarefa_fim = tarefa.get('data_fim')
        
        if tarefa_inicio and tarefa_fim:
            try:
                inicio_dt = datetime.strptime(tarefa_inicio.split('T')[0], '%Y-%m-%d')
                fim_dt = datetime.strptime(tarefa_fim.split('T')[0], '%Y-%m-%d')
                
                if fim_dt < inicio_dt:
                    projeto_nome = 'N/A'
                    projeto_id = tarefa.get('projeto_id')
                    if projeto_id in projeto_dict:
                        projeto_nome = projeto_dict[projeto_id].get('nome', 'N/A')
                    
                    conflitos['datas_invalidas'].append({
                        'tipo': 'Tarefa com data fim anterior à data início',
                        'projeto_nome': projeto_nome,
                        'projeto_id': projeto_id,
                        'tarefa_nome': tarefa.get('nome', 'N/A'),
                        'tarefa_id': tarefa.get('id'),
                        'tarefa_inicio': tarefa_inicio.split('T')[0],
                        'tarefa_fim': tarefa_fim.split('T')[0],
                        'descricao': f"Data fim ({tarefa_fim.split('T')[0]}) é anterior à data início ({tarefa_inicio.split('T')[0]})"
                    })
            except (ValueError, AttributeError):
                continue
    
    # 4. Detectar problemas com predecessoras
    for tarefa in tarefas:
        predecessoras = tarefa.get('predecessoras')
        if predecessoras:
            try:
                # Analisar predecessoras (formato: "1FS,2SS+3d,3FF-1d")  
                pred_list = [p.strip() for p in predecessoras.split(',') if p.strip()]
                tarefa_ordem = tarefa.get('ordem', 0)
                
                for pred in pred_list:
                    # Extrair número da tarefa predecessora
                    import re
                    match = re.match(r'^(\d+)', pred)
                    if match:
                        pred_ordem = int(match.group(1))
                        
                        # Verificar se predecessora existe
                        pred_existe = any(t.get('ordem') == pred_ordem and t.get('projeto_id') == tarefa.get('projeto_id') for t in tarefas)
                        
                        if not pred_existe:
                            projeto_nome = 'N/A'
                            projeto_id = tarefa.get('projeto_id')
                            if projeto_id in projeto_dict:
                                projeto_nome = projeto_dict[projeto_id].get('nome', 'N/A')
                            
                            conflitos['predecessoras_conflito'].append({
                                'tipo': 'Predecessora inexistente',
                                'projeto_nome': projeto_nome,
                                'projeto_id': projeto_id,
                                'tarefa_nome': tarefa.get('nome', 'N/A'),
                                'tarefa_id': tarefa.get('id'),
                                'tarefa_ordem': tarefa_ordem,
                                'predecessora_ordem': pred_ordem,
                                'descricao': f"Tarefa {tarefa_ordem} referencia predecessora {pred_ordem} que não existe"
                            })
                        

                            
            except Exception as e:
                continue
    
    # 5. Detectar sobreposições entre tarefas do mesmo projeto
    tarefas_por_projeto = {}
    for tarefa in tarefas:
        projeto_id = tarefa.get('projeto_id')
        if projeto_id:
            if projeto_id not in tarefas_por_projeto:
                tarefas_por_projeto[projeto_id] = []
            tarefas_por_projeto[projeto_id].append(tarefa)
    
    for projeto_id, tarefas_projeto in tarefas_por_projeto.items():
        projeto_nome = projeto_dict.get(projeto_id, {}).get('nome', 'N/A')
        
        for i, tarefa1 in enumerate(tarefas_projeto):
            for tarefa2 in tarefas_projeto[i+1:]:
                if verificar_sobreposicao_tarefas(tarefa1, tarefa2):
                    conflitos['tarefas_sobrepostas'].append({
                        'tipo': 'Tarefas sobrepostas no mesmo projeto',
                        'projeto_nome': projeto_nome,
                        'projeto_id': projeto_id,
                        'tarefa1_nome': tarefa1.get('nome', 'N/A'),
                        'tarefa1_id': tarefa1.get('id'),
                        'tarefa1_responsavel': tarefa1.get('usuario_id', ''),
                        'tarefa1_inicio': formatar_data_brasileira(tarefa1.get('data_inicio')),
                        'tarefa1_fim': formatar_data_brasileira(tarefa1.get('data_fim')),
                        'tarefa2_nome': tarefa2.get('nome', 'N/A'),
                        'tarefa2_id': tarefa2.get('id'),
                        'tarefa2_responsavel': tarefa2.get('usuario_id', ''),
                        'tarefa2_inicio': formatar_data_brasileira(tarefa2.get('data_inicio')),
                        'tarefa2_fim': formatar_data_brasileira(tarefa2.get('data_fim')),
                        'descricao': f"As tarefas '{tarefa1.get('nome', 'N/A')}' e '{tarefa2.get('nome', 'N/A')}' possuem datas sobrepostas"
                    })

    # 6. Detectar sobreposições entre tarefas de projetos diferentes
    projetos_ids = list(tarefas_por_projeto.keys())
    for i, projeto_id1 in enumerate(projetos_ids):
        for projeto_id2 in projetos_ids[i+1:]:
            projeto_nome1 = projeto_dict.get(projeto_id1, {}).get('nome', 'N/A')
            projeto_nome2 = projeto_dict.get(projeto_id2, {}).get('nome', 'N/A')
            
            for tarefa1 in tarefas_por_projeto[projeto_id1]:
                for tarefa2 in tarefas_por_projeto[projeto_id2]:
                    if verificar_sobreposicao_tarefas(tarefa1, tarefa2):
                        conflitos['tarefas_sobrepostas_entre_projetos'].append({
                            'tipo': 'Tarefas sobrepostas entre projetos',
                            'projeto1_nome': projeto_nome1,
                            'projeto1_id': projeto_id1,
                            'projeto2_nome': projeto_nome2,
                            'projeto2_id': projeto_id2,
                            'tarefa1_nome': tarefa1.get('nome', 'N/A'),
                            'tarefa1_id': tarefa1.get('id'),
                            'tarefa1_responsavel': tarefa1.get('usuario_id', ''),
                            'tarefa1_inicio': formatar_data_brasileira(tarefa1.get('data_inicio')),
                            'tarefa1_fim': formatar_data_brasileira(tarefa1.get('data_fim')),
                            'tarefa2_nome': tarefa2.get('nome', 'N/A'),
                            'tarefa2_id': tarefa2.get('id'),
                            'tarefa2_responsavel': tarefa2.get('usuario_id', ''),
                            'tarefa2_inicio': formatar_data_brasileira(tarefa2.get('data_inicio')),
                            'tarefa2_fim': formatar_data_brasileira(tarefa2.get('data_fim')),
                            'descricao': f"A tarefa '{tarefa1.get('nome', 'N/A')}' do projeto '{projeto_nome1}' sobrepõe com a tarefa '{tarefa2.get('nome', 'N/A')}' do projeto '{projeto_nome2}'"
                        })
    
    return conflitos


def verificar_sobreposicao_tarefas(tarefa1, tarefa2):
    """
    Verifica se duas tarefas possuem datas sobrepostas
    
    Args:
        tarefa1 (dict): Primeira tarefa
        tarefa2 (dict): Segunda tarefa
    
    Returns:
        bool: True se há sobreposição, False caso contrário
    """
    try:
        inicio1 = tarefa1.get('data_inicio')
        fim1 = tarefa1.get('data_fim')
        inicio2 = tarefa2.get('data_inicio')
        fim2 = tarefa2.get('data_fim')
        
        if not all([inicio1, fim1, inicio2, fim2]):
            return False
        
        # Converter para datetime
        inicio1_dt = datetime.strptime(inicio1.split('T')[0], '%Y-%m-%d')
        fim1_dt = datetime.strptime(fim1.split('T')[0], '%Y-%m-%d')
        inicio2_dt = datetime.strptime(inicio2.split('T')[0], '%Y-%m-%d')
        fim2_dt = datetime.strptime(fim2.split('T')[0], '%Y-%m-%d')
        
        # Verificar sobreposição: há sobreposição se uma tarefa não termina antes da outra começar
        return not (fim1_dt < inicio2_dt or fim2_dt < inicio1_dt)
        
    except (ValueError, AttributeError):
        return False
