
print("[DEBUG] routes/relatorio.py sendo executado!")
import pandas as pd
import io
from datetime import datetime
from flask import Blueprint, render_template, request, send_file, make_response
from reportlab.pdfgen import canvas
from utils.auth import login_required
from config.database import supabase

relatorio_bp = Blueprint('relatorio', __name__)

print(f"[DEBUG] Blueprint relatorio criado: {relatorio_bp}")

@relatorio_bp.route('/pdf', methods=['GET', 'POST'])
@login_required
def relatorio_pdf():
    # Buscar dados reais
    # Filtrar por projeto_id se fornecido
    projeto_id = request.args.get('projeto_id') or request.form.get('projeto_id')
    projeto_ids = []
    # Suporte a múltiplos projetos via POST (tela de projetos)
    if request.method == 'POST':
        try:
            data = request.get_json(force=True, silent=True)
            if data:
                if 'projeto_ids' in data and isinstance(data['projeto_ids'], list):
                    projeto_ids = [str(pid) for pid in data['projeto_ids'] if pid]
        except Exception:
            pass
    if projeto_id:
        projeto_ids = [str(projeto_id)]

    status_filtro = []
    if request.method == 'POST':
        try:
            data = request.get_json(force=True, silent=True)
            if data:
                # O filtro 'status' agora corresponde ao status do projeto
                if 'status' in data and isinstance(data['status'], list):
                    status_filtro = [str(s).strip().lower() for s in data['status'] if s]
        except Exception:
            pass
    if projeto_ids or status_filtro:
        projetos_query = supabase.table('projetos').select('*')
        if projeto_ids:
            projetos_query = projetos_query.in_('id', projeto_ids)
        if status_filtro:
            # O campo de status do projeto pode ser salvo com ou sem acentuação, então vamos normalizar ambos os lados
            # Buscar todos projetos e filtrar manualmente se necessário
            projetos_response = projetos_query.execute()
            projetos = projetos_response.data if projetos_response.data else []
            def normalizar_status(s):
                return str(s).strip().lower().replace('í','i').replace('ú','u').replace('á','a').replace('é','e').replace('ó','o').replace('ê','e').replace('â','a').replace('ã','a').replace('ç','c')
            projetos = [p for p in projetos if normalizar_status(p.get('status','')) in [normalizar_status(sf) for sf in status_filtro]]
        else:
            projetos_response = projetos_query.execute()
            projetos = projetos_response.data if projetos_response.data else []
        projeto_ids_final = [p['id'] for p in projetos]
        tarefas_response = supabase.table('tarefas').select('*').in_('projeto_id', projeto_ids_final).execute() if projeto_ids_final else supabase.table('tarefas').select('*').execute()
        tarefas = tarefas_response.data if tarefas_response.data else []
    else:
        projetos_response = supabase.table('projetos').select('*').execute()
        projetos = projetos_response.data if projetos_response.data else []
        tarefas_response = supabase.table('tarefas').select('*').execute()
        tarefas = tarefas_response.data if tarefas_response.data else []
    usuario_ids = set()
    for projeto in projetos:
        if projeto.get('usuario_id'):
            usuario_ids.add(str(projeto['usuario_id']))
    for tarefa in tarefas:
        if tarefa.get('usuario_id'):
            usuario_ids.add(str(tarefa['usuario_id']))
    nomes_usuarios = {}
    if usuario_ids:
        usuarios_response = supabase.table('usuarios').select('id, nome').in_('id', list(usuario_ids)).execute()
        if usuarios_response.data:
            nomes_usuarios = {str(u['id']): u.get('nome', '') for u in usuarios_response.data}

    def normalizar(nome):
        if not nome:
            return ''
        return nome.strip().lower().replace('ã','a').replace('á','a').replace('â','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('ô','o').replace('ú','u').replace('ç','c')
    def data_inicio_lancamento(projeto_id):
        tarefas_proj = [t for t in tarefas if t.get('projeto_id') == projeto_id]
        tarefas_lancamento = [t for t in tarefas_proj if normalizar(t.get('nome', '')) == 'lancamento']
        datas = [t.get('data_inicio') for t in tarefas_lancamento if t.get('data_inicio')]
        datas_validas = [d for d in datas if d]
        if datas_validas:
            return min(datas_validas)
        return '9999-12-31'
    projetos_ordenados = sorted(projetos, key=lambda p: data_inicio_lancamento(p['id']))

    # Montar dados para PDF
    dados_pdf = []
    for projeto in projetos_ordenados:
        projeto_id = projeto['id']
        projeto_nome = projeto.get('nome', f'Projeto_{projeto_id}')
        # Adiciona uma linha especial para o título do projeto
        dados_pdf.append({
            'projeto_titulo': True,
            'nome': projeto_nome
        })
        tarefas_projeto = [t for t in tarefas if t.get('projeto_id') == projeto_id]
        tarefas_projeto_ordenadas = sorted(tarefas_projeto, key=lambda t: t.get('ordem', 0))
        for tarefa in tarefas_projeto_ordenadas:
            dias_uteis = ''
            try:
                if tarefa.get('data_inicio') and tarefa.get('data_fim'):
                    data_inicio = pd.to_datetime(tarefa['data_inicio'])
                    data_fim = pd.to_datetime(tarefa['data_fim'])
                    dias_totais = (data_fim - data_inicio).days + 1
                    semanas = dias_totais // 7
                    dias_restantes = dias_totais % 7
                    dias_uteis_calc = semanas * 5 + min(dias_restantes, 5)
                    if dias_uteis_calc < 0:
                        dias_uteis_calc = 0
                    dias_uteis = str(dias_uteis_calc)
            except Exception as e:
                dias_uteis = ''
            dados_pdf.append({
                'projeto_titulo': False,
                'nome': tarefa.get('nome', ''),
                'responsavel': nomes_usuarios.get(str(tarefa.get('usuario_id', '')), ''),
                'inicio': tarefa.get('data_inicio', ''),
                'fim': tarefa.get('data_fim', ''),
                'duracao': tarefa.get('duracao', ''),
                'dias_uteis': dias_uteis,
                'colecao': tarefa.get('colecao', '')
            })

    # Gerar PDF
    from reportlab.lib.pagesizes import A4, landscape
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    p.setTitle("Relatório de Projetos e Tarefas")
    width, height = landscape(A4)
    # Margens maiores
    margem_esq = 30  # Reduzido para aproximar a tabela da esquerda
    margem_dir = 80
    largura_util = width - margem_esq - margem_dir
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margem_esq, height - 40, "Relatório de Projetos e Tarefas")
    p.setFont("Helvetica", 10)
    p.drawString(margem_esq, height - 60, "Gerado em: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    # Cabeçalho
    colunas = ["Tarefas", "Responsável", "Início", "Fim", "Duração", "Dias Úteis", "Coleção"]
    y = height - 90
    larguras = [260, 140, 65, 65, 40, 60, 170]  # Coleção mais larga
    total_largura_tabela = sum(larguras)
    x_inicial = (width - total_largura_tabela) / 2
    altura_linha = 14
    from reportlab.lib import colors
    def desenhar_linha(y, valores, bold=False, fill=None):
        # Desenha retângulos e textos para cada célula
        font_size = 8
        for i, valor in enumerate(valores):
            x = x_inicial + sum(larguras[:i])
            largura = larguras[i]
            if fill:
                p.setFillColor(fill)
                p.rect(x, y-altura_linha+2, largura, altura_linha, fill=1, stroke=0)
                p.setFillColor(colors.black)
            p.rect(x, y-altura_linha+2, largura, altura_linha, fill=0, stroke=1)
            p.setFont("Helvetica-Bold" if bold else "Helvetica", font_size)
            texto = str(valor)
            # Truncar coluna Tarefas (i==0) se ultrapassar largura e adicionar padding
            if i == 0:
                padding = 5
                max_width = largura - 2 * padding
                texto_trunc = texto
                while p.stringWidth(texto_trunc, "Helvetica-Bold" if bold else "Helvetica", font_size) > max_width and len(texto_trunc) > 3:
                    texto_trunc = texto_trunc[:-1]
                if texto_trunc != texto:
                    texto_trunc = texto_trunc[:-3] + '...'
                p.drawString(x+padding, y-altura_linha+6, texto_trunc)
            # Truncar coluna Coleção (i==6) se ultrapassar largura e adicionar padding
            elif i == 6:
                padding = 5
                max_width = largura - 2 * padding
                texto_trunc = texto
                while p.stringWidth(texto_trunc, "Helvetica-Bold" if bold else "Helvetica", font_size) > max_width and len(texto_trunc) > 3:
                    texto_trunc = texto_trunc[:-1]
                if texto_trunc != texto:
                    texto_trunc = texto_trunc[:-3] + '...'
                p.drawString(x+padding, y-altura_linha+6, texto_trunc)
            elif i in [1, 2, 3, 4, 5]:
                # Centralizar Responsável (1), Início (2), Fim (3), Duração (4), Dias Úteis (5)
                text_width = p.stringWidth(texto, "Helvetica-Bold" if bold else "Helvetica", font_size)
                p.drawString(x + (largura - text_width) / 2, y-altura_linha+6, texto)
            else:
                p.drawString(x+2, y-altura_linha+6, texto)

    # Cabeçalho geral
    # Linhas
    for idx, linha in enumerate(dados_pdf):
        if linha.get('projeto_titulo'):
            # Espaço extra entre projetos (aumentado)
            y -= 28
            # Verifica se há espaço suficiente para título + cabeçalho (2 linhas grandes)
            altura_titulo = altura_linha + 6
            altura_total = altura_titulo + altura_linha
            if y - altura_total < 40:
                p.showPage()
                y = height - 40
            # Cabeçalho visual para cada projeto
            p.setFont("Helvetica-Bold", 13)
            p.setFillColor(colors.whitesmoke)
            p.rect(x_inicial, y-altura_linha+2, sum(larguras), altura_titulo, fill=1, stroke=0)
            p.setFillColor(colors.black)
            p.drawString(x_inicial+2, y-altura_linha+10, f"Projeto: {linha['nome']}")
            p.setFont("Helvetica", 8)
            y -= altura_titulo
            # Cabeçalho da tabela para este projeto
            desenhar_linha(y, colunas, bold=True, fill=colors.lightgrey)
            y -= altura_linha
        else:
            # Formatar datas para DD/MM/AAAA
            def formatar_data(data):
                try:
                    if data and len(str(data)) >= 10:
                        return pd.to_datetime(data).strftime('%d/%m/%Y')
                except Exception:
                    pass
                return data or ''
            valores = [
                linha['nome'],
                linha['responsavel'],
                formatar_data(linha['inicio']),
                formatar_data(linha['fim']),
                linha['duracao'],
                linha['dias_uteis'],
                (linha['colecao'] or '').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
            ]
            # Se for linha de lançamento, pintar de vermelho e negrito
            if str(linha['nome']).strip().lower() == 'lançamento' or str(linha['nome']).strip().lower() == 'lancamento':
                p.setFillColor(colors.red)
                desenhar_linha(y, valores, bold=True)
                p.setFillColor(colors.black)
            else:
                desenhar_linha(y, valores)
            y -= altura_linha
        if y < 40:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 40
    p.save()
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=False,
        download_name='relatorio_projetos_tarefas.pdf'
    )

@relatorio_bp.route('/teste_blueprint')
def teste_blueprint():
    return 'Blueprint relatorio funcionando!'

@relatorio_bp.route('/exportar_excel_projetos', methods=['GET', 'POST'])
@login_required
def exportar_excel_projetos():
    try:
        # Função auxiliar para parse de datas
        def parse_data(data_str):
            if not data_str:
                return None
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    return datetime.strptime(data_str, fmt)
                except Exception:
                    continue
            return None
        
        # Receber filtros via POST (projeto_ids, status do projeto, data_inicio, data_fim)
        projeto_ids = []
        status_filtro = []
        data_inicio_filtro = ''
        data_fim_filtro = ''
        if request.method == 'POST':
            try:
                data = request.get_json(force=True, silent=True)
                if data:
                    if 'projeto_ids' in data and isinstance(data['projeto_ids'], list):
                        projeto_ids = [str(pid) for pid in data['projeto_ids'] if pid]
                    if 'status' in data and isinstance(data['status'], list):
                        status_filtro = [str(s).strip().lower() for s in data['status'] if s]
                    if 'data_inicio' in data:
                        data_inicio_filtro = str(data['data_inicio']).strip()
                    if 'data_fim' in data:
                        data_fim_filtro = str(data['data_fim']).strip()
            except Exception:
                pass
        # Buscar projetos filtrados
        if projeto_ids:
            # Se projeto_ids foi enviado, buscar apenas esses projetos
            projetos_query = supabase.table('projetos').select('*').in_('id', projeto_ids)
            projetos_response = projetos_query.execute()
            projetos = projetos_response.data if projetos_response.data else []
            
            # Aplicar filtros adicionais aos projetos selecionados
            if status_filtro:
                def normalizar_status(s):
                    return str(s).strip().lower().replace('í','i').replace('ú','u').replace('á','a').replace('é','e').replace('ó','o').replace('ê','e').replace('â','a').replace('ã','a').replace('ç','c')
                projetos = [p for p in projetos if normalizar_status(p.get('status','')) in [normalizar_status(sf) for sf in status_filtro]]
            
            # Aplicar filtro de data aos projetos selecionados
            if data_inicio_filtro or data_fim_filtro:
                data_inicio_dt = parse_data(data_inicio_filtro) if data_inicio_filtro else None
                data_fim_dt = parse_data(data_fim_filtro) if data_fim_filtro else None
                projetos_filtrados = []
                for p in projetos:
                    data_inicio_proj = parse_data(p.get('data_inicio'))
                    data_fim_proj = parse_data(p.get('data_fim'))
                    if data_inicio_proj and data_fim_proj:
                        # Interseção de períodos
                        if (not data_fim_dt or data_inicio_proj <= data_fim_dt) and (not data_inicio_dt or data_fim_proj >= data_inicio_dt):
                            projetos_filtrados.append(p)
                    else:
                        # Se não tem datas, mantém por segurança
                        projetos_filtrados.append(p)
                projetos = projetos_filtrados
        else:
            # Se não há projeto_ids específicos, aplicar filtros de status e data
            projetos_query = supabase.table('projetos').select('*')
            projetos_response = projetos_query.execute()
            projetos = projetos_response.data if projetos_response.data else []
            
            # Aplicar filtro de status
            if status_filtro:
                def normalizar_status(s):
                    return str(s).strip().lower().replace('í','i').replace('ú','u').replace('á','a').replace('é','e').replace('ó','o').replace('ê','e').replace('â','a').replace('ã','a').replace('ç','c')
                projetos = [p for p in projetos if normalizar_status(p.get('status','')) in [normalizar_status(sf) for sf in status_filtro]]
            
            # Aplicar filtro de data
            if data_inicio_filtro or data_fim_filtro:
                data_inicio_dt = parse_data(data_inicio_filtro) if data_inicio_filtro else None
                data_fim_dt = parse_data(data_fim_filtro) if data_fim_filtro else None
                projetos_filtrados = []
                for p in projetos:
                    data_inicio_proj = parse_data(p.get('data_inicio'))
                    data_fim_proj = parse_data(p.get('data_fim'))
                    if data_inicio_proj and data_fim_proj:
                        # Interseção de períodos
                        if (not data_fim_dt or data_inicio_proj <= data_fim_dt) and (not data_inicio_dt or data_fim_proj >= data_inicio_dt):
                            projetos_filtrados.append(p)
                    else:
                        # Se não tem datas, mantém por segurança
                        projetos_filtrados.append(p)
                projetos = projetos_filtrados
        
        if not projetos:
            # Retornar Excel vazio se não houver projetos
            output = io.BytesIO()
            df_vazio = pd.DataFrame(columns=['Tarefas', 'Responsável', 'Inicio', 'Fim', 'Duração', 'Dias Úteis', 'Coleção'])
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_vazio.to_excel(writer, sheet_name='Sem_Projetos', index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='relatorio_projetos_vazio.xlsx'
            )
        # Buscar tarefas apenas dos projetos filtrados
        projeto_ids_final = [p['id'] for p in projetos]
        tarefas_response = supabase.table('tarefas').select('*').in_('projeto_id', projeto_ids_final).execute() if projeto_ids_final else supabase.table('tarefas').select('*').execute()
        tarefas = tarefas_response.data if tarefas_response.data else []

        # Buscar usuários para nomes dos responsáveis
        usuario_ids = set()
        for projeto in projetos:
            if projeto.get('usuario_id'):
                usuario_ids.add(str(projeto['usuario_id']))
        for tarefa in tarefas:
            if tarefa.get('usuario_id'):
                usuario_ids.add(str(tarefa['usuario_id']))

        nomes_usuarios = {}
        if usuario_ids:
            usuarios_response = supabase.table('usuarios').select('id, nome').in_('id', list(usuario_ids)).execute()
            if usuarios_response.data:
                nomes_usuarios = {str(u['id']): u.get('nome', '') for u in usuarios_response.data}


        # Função para normalizar nome (sem acentos, minúsculo)
        def normalizar(nome):
            if not nome:
                return ''
            return nome.strip().lower().replace('ã','a').replace('á','a').replace('â','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('ô','o').replace('ú','u').replace('ç','c')

        # Função para pegar data de lançamento (primeira tarefa chamada 'lançamento')
        def data_inicio_lancamento(projeto_id):
            tarefas_proj = [t for t in tarefas if t.get('projeto_id') == projeto_id]
            tarefas_lancamento = [t for t in tarefas_proj if normalizar(t.get('nome', '')) == 'lancamento']
            datas = [t.get('data_inicio') for t in tarefas_lancamento if t.get('data_inicio')]
            datas_validas = [d for d in datas if d]
            if datas_validas:
                return min(datas_validas)
            return '9999-12-31'

        # Ordenar projetos por data de lançamento
        projetos_ordenados = sorted(projetos, key=lambda p: data_inicio_lancamento(p['id']))

        # Montar dados para a aba 'Todos'
        todos_dados = []
        for projeto in projetos_ordenados:
            projeto_id = projeto['id']
            projeto_nome = projeto.get('nome', f'Projeto_{projeto_id}')
            tarefas_projeto = [t for t in tarefas if t.get('projeto_id') == projeto_id]
            tarefas_projeto_ordenadas = sorted(tarefas_projeto, key=lambda t: t.get('ordem', 0))
            for tarefa in tarefas_projeto_ordenadas:
                dias_uteis = ''
                try:
                    if tarefa.get('data_inicio') and tarefa.get('data_fim'):
                        data_inicio = pd.to_datetime(tarefa['data_inicio'])
                        data_fim = pd.to_datetime(tarefa['data_fim'])
                        dias_totais = (data_fim - data_inicio).days + 1
                        semanas = dias_totais // 7
                        dias_restantes = dias_totais % 7
                        dias_uteis_calc = semanas * 5 + min(dias_restantes, 5)
                        if dias_uteis_calc < 0:
                            dias_uteis_calc = 0
                        dias_uteis = str(dias_uteis_calc)
                except Exception as e:
                    dias_uteis = ''
                todos_dados.append({
                    'Projeto': projeto_nome,
                    'Tarefas': tarefa.get('nome', ''),
                    'Responsável': nomes_usuarios.get(str(tarefa.get('usuario_id', '')), ''),
                    'Início': tarefa.get('data_inicio', ''),
                    'Fim': tarefa.get('data_fim', ''),
                    'Duração': tarefa.get('duracao', ''),
                    'Dias Úteis': dias_uteis,
                    'Coleção': tarefa.get('colecao', '')
                })

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Escrever aba 'Todos'
            if todos_dados:
                df_todos = pd.DataFrame(todos_dados)
                colunas_data = ['Início', 'Fim']
                for col in colunas_data:
                    if col in df_todos.columns:
                        df_todos[col] = pd.to_datetime(df_todos[col], errors='coerce').dt.strftime('%d/%m/%Y')
                df_todos = df_todos.fillna('')
                # Converter Dias Úteis para número
                if 'Dias Úteis' in df_todos.columns:
                    df_todos['Dias Úteis'] = pd.to_numeric(df_todos['Dias Úteis'], errors='coerce').astype('Int64')
                df_todos.to_excel(writer, sheet_name='Todos', index=False)
                worksheet_todos = writer.sheets['Todos']
                for idx, col in enumerate(df_todos.columns):
                    max_len = max(
                        [len(str(val)) for val in df_todos[col].values] + [len(str(col))]
                    )
                    worksheet_todos.set_column(idx, idx, max_len + 2)
                if 'Dias Úteis' in df_todos.columns:
                    col_idx = df_todos.columns.get_loc('Dias Úteis')
                    num_format = writer.book.add_format({'num_format': '0'})
                    worksheet_todos.set_column(col_idx, col_idx, None, num_format)

            # Escrever abas dos projetos
            for projeto in projetos_ordenados:
                projeto_id = projeto['id']
                projeto_nome = projeto.get('nome', f'Projeto_{projeto_id}')
                # Filtrar tarefas deste projeto e ordenar pelo campo ordem
                tarefas_projeto = [t for t in tarefas if t.get('projeto_id') == projeto_id]
                tarefas_projeto_ordenadas = sorted(tarefas_projeto, key=lambda t: t.get('ordem', 0))

                # Preparar dados das tarefas
                dados_tarefas = []
                for tarefa in tarefas_projeto_ordenadas:
                    dias_uteis = ''
                    try:
                        if tarefa.get('data_inicio') and tarefa.get('data_fim'):
                            data_inicio = pd.to_datetime(tarefa['data_inicio'])
                            data_fim = pd.to_datetime(tarefa['data_fim'])
                            dias_totais = (data_fim - data_inicio).days + 1
                            semanas = dias_totais // 7
                            dias_restantes = dias_totais % 7
                            dias_uteis_calc = semanas * 5 + min(dias_restantes, 5)
                            if dias_uteis_calc < 0:
                                dias_uteis_calc = 0
                            dias_uteis = str(dias_uteis_calc)
                    except Exception as e:
                        print(f"Erro calculando dias úteis: {e}")
                        dias_uteis = ''

                    dados_tarefas.append({
                        'Tarefas': tarefa.get('nome', ''),
                        'Responsável': nomes_usuarios.get(str(tarefa.get('usuario_id', '')), ''),
                        'Inicio': tarefa.get('data_inicio', ''),
                        'Fim': tarefa.get('data_fim', ''),
                        'Duração': tarefa.get('duracao', ''),
                        'Dias Úteis': dias_uteis,
                        'Coleção': tarefa.get('colecao', '')
                    })

                # Criar DataFrame para este projeto
                if dados_tarefas:
                    df_projeto = pd.DataFrame(dados_tarefas)
                    colunas_data = ['Inicio', 'Fim']
                    for col in colunas_data:
                        if col in df_projeto.columns:
                            df_projeto[col] = pd.to_datetime(df_projeto[col], errors='coerce').dt.strftime('%d/%m/%Y')
                    df_projeto = df_projeto.fillna('')
                else:
                    df_projeto = pd.DataFrame(columns=['Tarefas', 'Responsável', 'Inicio', 'Fim', 'Duração', 'Dias Úteis', 'Coleção'])

                sheet_name = projeto_nome[:31].replace('/', '_').replace('\\', '_').replace('?', '_').replace('*', '_').replace('[', '_').replace(']', '_')

                # Converter 'Dias Úteis' para inteiro se possível
                if 'Dias Úteis' in df_projeto.columns:
                    df_projeto['Dias Úteis'] = pd.to_numeric(df_projeto['Dias Úteis'], errors='coerce').astype('Int64')

                # Escrever DataFrame na planilha
                df_projeto.to_excel(writer, sheet_name=sheet_name, index=False)

                # Ajustar largura das colunas automaticamente e formatar 'Dias Úteis' como número
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(df_projeto.columns):
                    max_len = max(
                        [len(str(val)) for val in df_projeto[col].values] + [len(str(col))]
                    )
                    worksheet.set_column(idx, idx, max_len + 2)

                # Se existir coluna 'Dias Úteis', formatar como número
                if 'Dias Úteis' in df_projeto.columns:
                    col_idx = df_projeto.columns.get_loc('Dias Úteis')
                    num_format = writer.book.add_format({'num_format': '0'})
                    worksheet.set_column(col_idx, col_idx, None, num_format)

        output.seek(0)


        # Nome do arquivo no formato solicitado: 'Relatório Projetos DD-MM-AAAA  HH:MM:SS.xlsx'
        timestamp = datetime.now().strftime('%d-%m-%Y  %Hh%M')
        filename = f'Relatório Projetos {timestamp}.xlsx'

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Erro na exportação Excel: {e}")
        import traceback
        traceback.print_exc()
        from flask import jsonify
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500


@relatorio_bp.route('/datas-conflitantes')
@login_required
def datas_conflitantes():
    # Página para identificar e mostrar datas conflitantes no sistema
    try:
        # Buscar usuários para o filtro
        try:
            usuarios_data = supabase.table('usuarios').select('id, nome').execute()
            usuarios = usuarios_data.data if usuarios_data.data else []
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            usuarios = []

        # Verificar se há filtro de responsáveis (aceita ID numérico ou string/UUID)
        responsaveis_ids = [rid for rid in request.args.getlist('responsaveis') if rid]
        responsavel_tarefa1_ids = [rid for rid in request.args.getlist('responsavel_tarefa1') if rid]
        responsavel_tarefa2_ids = [rid for rid in request.args.getlist('responsavel_tarefa2') if rid]

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
            print(f"Erro ao buscar projetos: {e}")
            projetos = []

        try:
            tarefas_data = supabase.table('tarefas').select('id, nome, data_inicio, data_fim, projeto_id, usuario_id, status, ordem').execute()
            tarefas = tarefas_data.data if tarefas_data.data else []
        except Exception as e:
            print(f"Erro ao buscar tarefas: {e}")
            tarefas = []

        # Filtrar tarefas concluídas para os filtros de responsáveis
        tarefas_ativas = [tarefa for tarefa in tarefas
                         if tarefa.get('status', '').lower() not in ['concluída', 'concluida', 'concluído', 'concluido']]

        # Detectar conflitos
        conflitos = detectar_conflitos_datas(projetos, tarefas)

        # Aplicar filtro de responsáveis geral
        if responsaveis_ids:
            responsaveis_normalizados = [normalizar_resp(rid) for rid in responsaveis_ids]
            responsaveis_normalizados = [rid for rid in responsaveis_normalizados if rid is not None]
            if responsaveis_normalizados:
                conflitos = filtrar_conflitos_por_responsaveis(conflitos, responsaveis_normalizados, tarefas_ativas)

        # Filtro independente para tarefa 1
        if responsavel_tarefa1_ids:
            tarefa1_normalizados = [normalizar_resp(rid) for rid in responsavel_tarefa1_ids]
            tarefa1_normalizados = [rid for rid in tarefa1_normalizados if rid is not None]
            if tarefa1_normalizados:
                conflitos['tarefas_sobrepostas'] = [c for c in conflitos['tarefas_sobrepostas'] if c.get('tarefa1_responsavel') in tarefa1_normalizados]
                conflitos['tarefas_sobrepostas_entre_projetos'] = [c for c in conflitos['tarefas_sobrepostas_entre_projetos'] if c.get('tarefa1_responsavel') in tarefa1_normalizados]

        # Filtro independente para tarefa 2
        if responsavel_tarefa2_ids:
            tarefa2_normalizados = [normalizar_resp(rid) for rid in responsavel_tarefa2_ids]
            tarefa2_normalizados = [rid for rid in tarefa2_normalizados if rid is not None]
            if tarefa2_normalizados:
                conflitos['tarefas_sobrepostas'] = [c for c in conflitos['tarefas_sobrepostas'] if c.get('tarefa2_responsavel') in tarefa2_normalizados]
                conflitos['tarefas_sobrepostas_entre_projetos'] = [c for c in conflitos['tarefas_sobrepostas_entre_projetos'] if c.get('tarefa2_responsavel') in tarefa2_normalizados]

        return render_template('datas_conflitantes.html',
                             conflitos=conflitos,
                             usuarios=usuarios,
                             responsaveis_selecionados=responsaveis_ids,
                             calcular_conflitos=calcular_conflitos)

    except Exception as e:
        print(f"Erro na página de datas conflitantes: {e}")
        import traceback
        traceback.print_exc()
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
                             calcular_conflitos=False,
                             erro=str(e))


def detectar_conflitos_datas(projetos, tarefas):
    # Detecta diversos tipos de conflitos de datas no sistema
    from datetime import datetime

    def formatar_data_brasileira(data_iso):
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

    # Filtrar tarefas concluídas - não considerar para conflitos
    tarefas_ativas = [tarefa for tarefa in tarefas
                     if tarefa.get('status', '').lower() not in ['concluída', 'concluida', 'concluído', 'concluido']]

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

    for tarefa in tarefas_ativas:
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
                            'descricao': f"Tarefa programada de {formatar_data_brasileira(tarefa_inicio)} a {formatar_data_brasileira(tarefa_fim)}, mas projeto vai de {formatar_data_brasileira(projeto_inicio)} a {formatar_data_brasileira(projeto_fim)}"
                        })
                except (ValueError, AttributeError) as e:
                    conflitos['datas_invalidas'].append({
                        'tipo': 'Data inválida em tarefa',
                        'tarefa_nome': tarefa.get('nome', 'N/A'),
                        'tarefa_id': tarefa.get('id'),
                        'projeto_nome': projeto_dict.get(projeto_id, {}).get('nome', 'N/A'),
                        'descricao': f"Erro ao processar datas: {str(e)}"
                    })

    # 3. Tarefas sobrepostas no mesmo projeto
    tarefas_por_projeto = {}
    for tarefa in tarefas_ativas:
        projeto_id = tarefa.get('projeto_id')
        if projeto_id:
            if projeto_id not in tarefas_por_projeto:
                tarefas_por_projeto[projeto_id] = []
            tarefas_por_projeto[projeto_id].append(tarefa)

    for projeto_id, tarefas_projeto in tarefas_por_projeto.items():
        if len(tarefas_projeto) > 1:
            tarefas_projeto.sort(key=lambda x: x.get('data_inicio', ''))

            for i in range(len(tarefas_projeto)):
                for j in range(i + 1, len(tarefas_projeto)):
                    tarefa1 = tarefas_projeto[i]
                    tarefa2 = tarefas_projeto[j]

                    tarefa1_inicio = tarefa1.get('data_inicio')
                    tarefa1_fim = tarefa1.get('data_fim')
                    tarefa2_inicio = tarefa2.get('data_inicio')
                    tarefa2_fim = tarefa2.get('data_fim')

                    if tarefa1_inicio and tarefa1_fim and tarefa2_inicio and tarefa2_fim:
                        try:
                            t1_inicio = datetime.strptime(tarefa1_inicio.split('T')[0], '%Y-%m-%d')
                            t1_fim = datetime.strptime(tarefa1_fim.split('T')[0], '%Y-%m-%d')
                            t2_inicio = datetime.strptime(tarefa2_inicio.split('T')[0], '%Y-%m-%d')
                            t2_fim = datetime.strptime(tarefa2_fim.split('T')[0], '%Y-%m-%d')

                            # Verifica se há sobreposição
                            if t1_inicio <= t2_fim and t2_inicio <= t1_fim:
                                conflitos['tarefas_sobrepostas'].append({
                                    'tipo': 'Tarefas sobrepostas no mesmo projeto',
                                    'projeto_nome': projeto_dict.get(projeto_id, {}).get('nome', 'N/A'),
                                    'projeto_id': projeto_id,
                                    'tarefa1_nome': tarefa1.get('nome', 'N/A'),
                                    'tarefa1_id': tarefa1.get('id'),
                                    'tarefa1_responsavel': tarefa1.get('usuario_id'),
                                    'tarefa1_inicio': formatar_data_brasileira(tarefa1_inicio),
                                    'tarefa1_fim': formatar_data_brasileira(tarefa1_fim),
                                    'tarefa2_nome': tarefa2.get('nome', 'N/A'),
                                    'tarefa2_id': tarefa2.get('id'),
                                    'tarefa2_responsavel': tarefa2.get('usuario_id'),
                                    'tarefa2_inicio': formatar_data_brasileira(tarefa2_inicio),
                                    'tarefa2_fim': formatar_data_brasileira(tarefa2_fim),
                                    'descricao': f"Tarefa '{tarefa1.get('nome', 'N/A')}' ({formatar_data_brasileira(tarefa1_inicio)} - {formatar_data_brasileira(tarefa1_fim)}) conflita com '{tarefa2.get('nome', 'N/A')}' ({formatar_data_brasileira(tarefa2_inicio)} - {formatar_data_brasileira(tarefa2_fim)})"
                                })
                        except (ValueError, AttributeError) as e:
                            conflitos['datas_invalidas'].append({
                                'tipo': 'Erro ao comparar tarefas',
                                'tarefa_nome': f"{tarefa1.get('nome', 'N/A')} vs {tarefa2.get('nome', 'N/A')}",
                                'projeto_nome': projeto_dict.get(projeto_id, {}).get('nome', 'N/A'),
                                'descricao': f"Erro ao comparar datas: {str(e)}"
                            })

    # 4. Tarefas sobrepostas entre projetos diferentes (mesmo responsável)
    tarefas_por_responsavel = {}
    for tarefa in tarefas_ativas:
        responsavel_id = tarefa.get('usuario_id')
        if responsavel_id:
            if responsavel_id not in tarefas_por_responsavel:
                tarefas_por_responsavel[responsavel_id] = []
            tarefas_por_responsavel[responsavel_id].append(tarefa)

    for responsavel_id, tarefas_resp in tarefas_por_responsavel.items():
        if len(tarefas_resp) > 1:
            tarefas_resp.sort(key=lambda x: x.get('data_inicio', ''))

            for i in range(len(tarefas_resp)):
                for j in range(i + 1, len(tarefas_resp)):
                    tarefa1 = tarefas_resp[i]
                    tarefa2 = tarefas_resp[j]

                    # Só verifica se são de projetos diferentes
                    if tarefa1.get('projeto_id') != tarefa2.get('projeto_id'):
                        tarefa1_inicio = tarefa1.get('data_inicio')
                        tarefa1_fim = tarefa1.get('data_fim')
                        tarefa2_inicio = tarefa2.get('data_inicio')
                        tarefa2_fim = tarefa2.get('data_fim')

                        if tarefa1_inicio and tarefa1_fim and tarefa2_inicio and tarefa2_fim:
                            try:
                                t1_inicio = datetime.strptime(tarefa1_inicio.split('T')[0], '%Y-%m-%d')
                                t1_fim = datetime.strptime(tarefa1_fim.split('T')[0], '%Y-%m-%d')
                                t2_inicio = datetime.strptime(tarefa2_inicio.split('T')[0], '%Y-%m-%d')
                                t2_fim = datetime.strptime(tarefa2_fim.split('T')[0], '%Y-%m-%d')

                                # Verifica se há sobreposição
                                if t1_inicio <= t2_fim and t2_inicio <= t1_fim:
                                    conflitos['tarefas_sobrepostas_entre_projetos'].append({
                                        'tipo': 'Tarefas sobrepostas entre projetos diferentes',
                                        'responsavel_id': responsavel_id,
                                        'tarefa1_nome': tarefa1.get('nome', 'N/A'),
                                        'tarefa1_id': tarefa1.get('id'),
                                        'tarefa1_responsavel': tarefa1.get('usuario_id'),
                                        'tarefa1_projeto': projeto_dict.get(tarefa1.get('projeto_id'), {}).get('nome', 'N/A'),
                                        'tarefa1_inicio': formatar_data_brasileira(tarefa1_inicio),
                                        'tarefa1_fim': formatar_data_brasileira(tarefa1_fim),
                                        'tarefa2_nome': tarefa2.get('nome', 'N/A'),
                                        'tarefa2_id': tarefa2.get('id'),
                                        'tarefa2_responsavel': tarefa2.get('usuario_id'),
                                        'tarefa2_projeto': projeto_dict.get(tarefa2.get('projeto_id'), {}).get('nome', 'N/A'),
                                        'tarefa2_inicio': formatar_data_brasileira(tarefa2_inicio),
                                        'tarefa2_fim': formatar_data_brasileira(tarefa2_fim),
                                        'descricao': f"Responsável sobrecarregado: '{tarefa1.get('nome', 'N/A')}' no projeto '{projeto_dict.get(tarefa1.get('projeto_id'), {}).get('nome', 'N/A')}' conflita com '{tarefa2.get('nome', 'N/A')}' no projeto '{projeto_dict.get(tarefa2.get('projeto_id'), {}).get('nome', 'N/A')}'"
                                    })
                            except (ValueError, AttributeError) as e:
                                conflitos['datas_invalidas'].append({
                                    'tipo': 'Erro ao comparar tarefas entre projetos',
                                    'tarefa_nome': f"{tarefa1.get('nome', 'N/A')} vs {tarefa2.get('nome', 'N/A')}",
                                    'projeto_nome': f"{projeto_dict.get(tarefa1.get('projeto_id'), {}).get('nome', 'N/A')} vs {projeto_dict.get(tarefa2.get('projeto_id'), {}).get('nome', 'N/A')}",
                                    'descricao': f"Erro ao comparar datas entre projetos: {str(e)}"
                                })

    return conflitos


def filtrar_conflitos_por_responsaveis(conflitos, responsaveis_ids, tarefas):
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
        if tarefa_id:
            resp = tarefa_responsavel(tarefa_id)
            if resp in responsaveis_set:
                conflitos_filtrados['datas_invalidas'].append(conflito)

    return conflitos_filtrados