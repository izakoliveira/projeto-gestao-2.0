from flask import Blueprint, render_template, request, send_file, make_response
from config.database import supabase
from utils.dias_uteis import dias_uteis_entre_datas
import os
import base64
from datetime import datetime
import io

# Matplotlib imports opcionais para Render
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import pandas as pd
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
    pd = MockModule()

relatorio_bp = Blueprint('relatorio', __name__)

print('DEBUG: routes/relatorio.py carregado com sucesso')


@relatorio_bp.route('/relatorio/gantt_excel', methods=['GET', 'POST'])
def exportar_gantt_excel():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        gantt_base64 = data.get('gantt_base64')
        tipo_id = data.get('tipo_id', '')
        projeto_id = data.get('projeto_id', '')
        status = data.get('status', [])
        colecao = data.get('colecao', [])
        data_inicio = data.get('data_inicio', '')
        data_fim = data.get('data_fim', '')
    else:
        gantt_base64 = request.args.get('gantt_base64')
        tipo_id = request.args.get('tipo_id', '')
        projeto_id = request.args.get('projeto_id', '')
        status = request.args.getlist('status')
        colecao = request.args.getlist('colecao')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        
        # Se não foi fornecido projeto_id nos parâmetros, verificar se estamos na página de detalhes do projeto
        if not projeto_id:
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

    # Buscar tarefas diretamente do banco
    query = supabase.table('tarefas').select('*')
    if projeto_id:
        query = query.eq('projeto_id', projeto_id)
    if tipo_id:
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
            responsavel_nome = nomes_usuarios.get(str(usuario_id), '')
            print(f"[DEBUG EXCEL MAP] Nome responsável: '{responsavel_nome}'")
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

    # Ordenar projetos e tarefas igual ao relatório
    def normalizar(nome):
        if not nome:
            return ''
        return nome.strip().lower().replace('ã','a').replace('á','a').replace('â','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('ô','o').replace('ú','u').replace('ç','c')

    def data_inicio_lancamento(projeto):
        tarefas = projeto.get('tarefas', [])
        tarefas_lancamento = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
        datas = [t.get('inicio') for t in tarefas_lancamento if t.get('inicio')]
        datas_validas = [d for d in datas if d]
        if datas_validas:
            return min(datas_validas)
        return '9999-12-31'

    projetos_nome = sorted(projetos_relatorio, key=lambda p: p['nome'])
    projetos_ordenados = sorted(projetos_nome, key=data_inicio_lancamento)

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
                'Início': formatar_data_excel(tarefa['inicio']),
                'Fim': formatar_data_excel(tarefa['fim']),
                'Dias Úteis': tarefa['dias_uteis'],
                'Duração': tarefa['duracao'],
                'Coleção': tarefa['colecao'],
                'Responsável': responsavel_final,
            })
    df = pd.DataFrame(dados)

    # Gerar arquivo Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
        # Autoajustar largura das colunas na aba Dados
        dados_sheet = writer.sheets['Dados']
        for i, col in enumerate(df.columns):
            if col == 'Duração':
                max_len = max(
                    [len(str(val)) for val in df[col].values] + [len(str(col))]
                )
                dados_sheet.set_column(i, i, max_len + 2)
            else:
                max_len = max(
                    [len(str(val)) for val in df[col].values] + [len(str(col))]
                )
                dados_sheet.set_column(i, i, max_len + 2)
        workbook = writer.book
        from datetime import datetime
        # Para cada projeto, criar uma aba de Gantt
        for idx, projeto in enumerate(projetos_ordenados):
            # Formato de fonte cinza para a coluna Dias até início
            formato_cinza = workbook.add_format({'font_color': '#888888'})
            nome_aba = str(projeto['nome'])[:31]  # Limite do Excel para nome de aba
            gantt_sheet = workbook.add_worksheet(nome_aba)
            gantt_sheet.write('A1', 'Tarefa')
            gantt_sheet.write('B1', 'Início')
            gantt_sheet.write('C1', 'Fim')
            gantt_sheet.write('D1', 'Duração')
            gantt_sheet.write('E1', 'Coleção')
            gantt_sheet.write('F1', 'Responsável')
            gantt_sheet.write('G1', 'Dias até início')
            # Preencher dados e calcular largura máxima de cada coluna
            col_widths = [len('Tarefa'), len('Início'), len('Fim'), len('Duração'), len('Coleção'), len('Responsável'), len('Dias até início')]
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
                col_widths = [len('Tarefa'), len('Início'), len('Fim'), duracao_max_len, len('Coleção'), responsavel_max_len, len('Dias até início')]
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
                        gantt_sheet.write_number(row, 3, duracao_int)
                        duracao_len = len(str(duracao_int))
                    except Exception:
                        gantt_sheet.write(row, 3, str(duracao_val))
                        duracao_len = len(str(duracao_val))
                    # Destacar tarefa 'Lançamento' em vermelho e negrito
                    if str(tarefa['nome']).strip().lower() == 'lançamento':
                        destaque_format = workbook.add_format({'font_color': 'red', 'bold': True})
                        gantt_sheet.write(row, 0, tarefa['nome'], destaque_format)
                    else:
                        gantt_sheet.write(row, 0, tarefa['nome'])
                    gantt_sheet.write(row, 1, inicio)
                    gantt_sheet.write(row, 2, fim)
                    gantt_sheet.write(row, 4, colecao)
                    gantt_sheet.write(row, 5, responsavel)
                    gantt_sheet.write(row, 6, excel_date, formato_cinza)
                    col_widths[0] = max(col_widths[0], len(str(tarefa['nome'])))
                    col_widths[1] = max(col_widths[1], len(str(inicio)))
                    col_widths[2] = max(col_widths[2], len(str(fim)))
                    # Garantir que a largura da coluna Duração considere o nome da coluna e o valor convertido para string
                    col_widths[3] = max(col_widths[3], duracao_len, len('Duração'))
                    col_widths[4] = max(col_widths[4], len(str(colecao)))
                    col_widths[5] = max(col_widths[5], len(str(responsavel)))
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
                'values':     [nome_aba, 1, 3, row-1, 3],
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
            # Não sobrescrever largura da coluna 'Duração' (índice 3)
    output.seek(0)

    # Definir nome do arquivo baseado no contexto
    nome_arquivo = 'gantt_relatorio.xlsx'
    if projeto_id and projetos_ordenados:
        # Se estamos exportando um projeto específico, usar o nome do projeto
        projeto_nome = projetos_ordenados[0]['nome'] if len(projetos_ordenados) == 1 else 'projeto_especifico'
        # Limpar caracteres especiais do nome do arquivo
        import re
        projeto_nome_limpo = re.sub(r'[^\w\s-]', '', projeto_nome).strip()
        projeto_nome_limpo = re.sub(r'[-\s]+', '_', projeto_nome_limpo)
        nome_arquivo = f'gantt_{projeto_nome_limpo}.xlsx'
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
        status = data.get('status', [])
        colecao = data.get('colecao', [])
        data_inicio = data.get('data_inicio', '')
        data_fim = data.get('data_fim', '')
    else:
        gantt_base64 = None
        tipo_id = request.args.get('tipo_id', '')
        projeto_id = request.args.get('projeto_id', '')
        status = request.args.getlist('status')
        colecao = request.args.getlist('colecao')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')

    # Buscar tarefas diretamente do banco
    query = supabase.table('tarefas').select('*')
    if projeto_id:
        query = query.eq('projeto_id', projeto_id)
    if tipo_id:
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

    # Ordenar as tabelas de projetos pelo nome do projeto (crescente)
    projetos_relatorio.sort(key=lambda p: p['nome'].lower())
    html = render_template('relatorio_gantt.html', projetos=projetos_relatorio, gantt_base64=gantt_base64)
    return html
