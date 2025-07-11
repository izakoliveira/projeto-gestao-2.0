import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, flash, make_response, url_for, jsonify, render_template_string
from supabase import create_client, Client
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from supabase_client import get_user_by_email, create_user, get_all_users
import requests
from functools import wraps
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
from urllib.parse import quote

# Carrega as variáveis do .env
load_dotenv()

# Inicializa Flask
app = Flask(__name__)

# Carregar a chave secreta do arquivo .env
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Verifica se a chave secreta foi carregada corretamente
if not app.secret_key:
    raise Exception("FLASK_SECRET_KEY não definida no arquivo .env")

# Conecta ao Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise Exception("SUPABASE_URL ou SUPABASE_KEY não definidas no arquivo .env")

supabase: Client = create_client(url, key)

# Testando a conexão com o Supabase
try:
    supabase_client = supabase.auth
    print("Conectado com sucesso ao Supabase!")
except Exception as e:
    print(f"Erro ao conectar com o Supabase: {e}")

RESTRICOES_PATH = 'restricoes.json'

# Função para carregar restrições
def carregar_restricoes():
    try:
        with open(RESTRICOES_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

# Função para salvar restrições
def salvar_restricoes(restricoes):
    with open(RESTRICOES_PATH, 'w') as f:
        json.dump(restricoes, f)

# Função para checar se uma funcionalidade está restrita para o usuário atual
def funcionalidade_restrita(nome_restricao):
    if session.get('user_nome') == 'izak.gomes59@gmail.com':
        return False
    restricoes = carregar_restricoes()
    return restricoes.get(nome_restricao, False)

# Função de validação de projeto
def validar_projeto(nome, data_inicio, data_fim):
    if not nome:
        return "O nome do projeto é obrigatório!"
    
    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        if data_inicio > data_fim:
            return "A data de início não pode ser posterior à data de término."
    except ValueError:
        return "As datas devem estar no formato AAAA-MM-DD."

    return None  # Se tudo estiver ok

# Definir o decorador login_required antes das rotas que o utilizam
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para acesso exclusivo do Izak
def apenas_admin_izak(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_email') != 'izak.gomes59@gmail.com':
            flash('Acesso restrito a administradores.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Rota principal (Home)
@app.route('/')
def index():
    return redirect('/dashboard')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        senha = request.form['senha']
        lembrar = 'lembrar' in request.form

        user = get_user_by_email(email)
        print("Usuário retornado:", user)
        if user:
            print('Hash salvo:', user['senha_hash'])
            print('Senha digitada:', senha)
            print('Verificação:', check_password_hash(user['senha_hash'], senha))
        if user and check_password_hash(user['senha_hash'], senha):
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            session['user_email'] = user['email']
            # Se quiser implementar o "lembrar-me", pode usar cookies aqui
            return redirect('/dashboard')
        else:
            flash('E-mail ou senha inválidos.')
    return render_template('login.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect('/login'))
    resp.delete_cookie('user_id')  # Remove o cookie de "lembrar-me" ao sair
    return resp

# Rota de listagem de projetos com filtros
@app.route('/projetos', methods=['GET', 'POST'])
@login_required
def projetos():
    usuario_id = session['user_id']
    nome = request.args.get('nome', '')  # Nome do projeto
    status = request.args.get('status', '')  # Status da tarefa
    data_inicio = request.args.get('data_inicio', '')  # Data de início
    data_fim = request.args.get('data_fim', '')  # Data de término

    if session.get('user_email') == 'izak.gomes59@gmail.com':
        # Admin vê todos os projetos
        query = supabase.table("projetos").select("*")
        if nome:
            query = query.ilike('nome', f'%{nome}%')
        if data_inicio:
            query = query.gte('data_inicio', data_inicio)
        if data_fim:
            query = query.lte('data_fim', data_fim)
        projetos = query.execute().data
    else:
        # Usuário comum vê apenas projetos autorizados
        resp = supabase.table("projetos_usuarios_visiveis").select("projeto_id").eq("usuario_id", usuario_id).execute()
        projetos_ids_visiveis = [r['projeto_id'] for r in resp.data]
        if projetos_ids_visiveis:
            query = supabase.table("projetos").select("*").in_("id", projetos_ids_visiveis)
            if nome:
                query = query.ilike('nome', f'%{nome}%')
            if data_inicio:
                query = query.gte('data_inicio', data_inicio)
            if data_fim:
                query = query.lte('data_fim', data_fim)
            projetos = query.execute().data
        else:
            projetos = []

    tarefas_filtradas = []
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    projeto_ids = [projeto['id'] for projeto in projetos]
    if projeto_ids:
        ids_str = ','.join([f'"{pid}"' for pid in projeto_ids])
        url = f"{SUPABASE_URL}/rest/v1/tarefas?projeto_id=in.({ids_str})"
        if status:
            # Codificar o status para URL (tratar espaços e caracteres especiais)
            status_encoded = quote(status)
            url += f"&status=eq.{status_encoded}"
        resp = requests.get(url, headers=headers)
        tarefas_filtradas = resp.json() if resp.status_code == 200 else []
        # Filtro de colecao (múltiplo)
        colecao_list = request.args.getlist('colecao')
        if colecao_list:
            tarefas_filtradas = [t for t in tarefas_filtradas if t.get('colecao') in colecao_list]
        
        # Filtrar projetos que têm tarefas com os filtros aplicados (status e/ou coleção)
        if status or colecao_list:
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

    for projeto in projetos:
        if projeto.get('data_inicio'):
            try:
                projeto['data_inicio'] = datetime.strptime(projeto['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                pass
        if projeto.get('data_fim'):
            try:
                projeto['data_fim'] = datetime.strptime(projeto['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                pass
    for tarefa in tarefas_filtradas:
        data_inicio_raw = tarefa.get('data_inicio')
        data_fim_raw = tarefa.get('data_fim')
        tarefa['data_inicio_iso'] = ''
        tarefa['data_fim_iso'] = ''
        if data_inicio_raw:
            try:
                if '-' in data_inicio_raw:
                    dt_inicio = datetime.strptime(data_inicio_raw, '%Y-%m-%d')
                else:
                    dt_inicio = datetime.strptime(data_inicio_raw, '%d/%m/%Y')
                tarefa['data_inicio_iso'] = dt_inicio.strftime('%Y-%m-%d')
                tarefa['data_inicio'] = dt_inicio.strftime('%d/%m/%Y')
            except Exception:
                tarefa['data_inicio_iso'] = data_inicio_raw
        if data_fim_raw:
            try:
                if '-' in data_fim_raw:
                    dt_fim = datetime.strptime(data_fim_raw, '%Y-%m-%d')
                else:
                    dt_fim = datetime.strptime(data_fim_raw, '%d/%m/%Y')
                tarefa['data_fim_iso'] = dt_fim.strftime('%Y-%m-%d')
                tarefa['data_fim'] = dt_fim.strftime('%d/%m/%Y')
            except Exception:
                tarefa['data_fim_iso'] = data_fim_raw
    if tarefas_filtradas:
        projeto_ids_tarefas = list(set([t.get('projeto_id') for t in tarefas_filtradas if t.get('projeto_id')]))
        if projeto_ids_tarefas:
            projetos_resp = supabase.table("projetos").select("id, nome").in_("id", projeto_ids_tarefas).execute()
            projetos_dict = {p['id']: p['nome'] for p in projetos_resp.data}
        else:
            projetos_dict = {}
        usuario_ids_tarefas = list(set([t.get('usuario_id') for t in tarefas_filtradas if t.get('usuario_id')]))
        if usuario_ids_tarefas:
            usuarios_resp = supabase.table("usuarios").select("id, nome").in_("id", usuario_ids_tarefas).execute()
            usuarios_dict = {u['id']: u['nome'] for u in usuarios_resp.data}
        else:
            usuarios_dict = {}
        for tarefa in tarefas_filtradas:
            tarefa['projeto_nome'] = projetos_dict.get(tarefa.get('projeto_id'), 'Projeto não encontrado')
            tarefa['usuario_nome'] = usuarios_dict.get(tarefa.get('usuario_id'), 'Não designado')
    for projeto in projetos:
        projeto['tarefas'] = []
        for t in tarefas_filtradas:
            if t.get('projeto_id') == projeto['id']:
                t_copia = t.copy()
                di = t_copia.get('data_inicio_iso')
                df = t_copia.get('data_fim_iso')
                def data_valida(dt):
                    try:
                        if not dt or dt in ('None', '0000-00-00', ''):
                            return False
                        ano = int(dt[:4])
                        return 2000 <= ano <= 2100
                    except Exception:
                        return False
                if data_valida(di) and data_valida(df):
                    try:
                        dt_inicio = datetime.strptime(di, '%Y-%m-%d')
                        dt_fim = datetime.strptime(df, '%Y-%m-%d')
                        duration = (dt_fim - dt_inicio).days + 1
                        t_copia['duration'] = duration
                        projeto['tarefas'].append(t_copia)
                    except Exception:
                        pass
        gantt_data = []
        gantt_links = []
        for t in projeto['tarefas']:
            gantt_data.append({
                'id': t['id'],
                'text': t.get('nome', ''),
                'start_date': t.get('data_inicio_iso', ''),
                'duration': t.get('duration', 1),
                'progress': 0
            })
            preds = t.get('predecessoras')
            if preds:
                preds_list = [p.strip() for p in preds.split(';') if p.strip()]
                for idx, pred in enumerate(preds_list):
                    pred_id = pred.split('FS')[0].split('SS')[0].split('FF')[0].split('SF')[0]
                    if pred_id:
                        gantt_links.append({
                            'id': f"{t['id']}_{idx}",
                            'source': pred_id,
                            'target': t['id'],
                            'type': '0'
                        })
        projeto['gantt_data'] = gantt_data
        projeto['gantt_links'] = gantt_links
    gantt_geral_data = []
    cor_projetos = {}
    tarefas_unicas = supabase.table('tarefas_unicas').select('nome, ordem').order('ordem').execute().data
    ordem_tarefas = {t['nome']: t['ordem'] for t in tarefas_unicas}
    todas_tarefas = []
    for projeto in projetos:
        if projeto.get('tarefas'):
            for tarefa in projeto['tarefas']:
                tarefa_copia = tarefa.copy()
                tarefa_copia['projeto_origem'] = projeto['nome']
                todas_tarefas.append(tarefa_copia)
    todas_tarefas.sort(key=lambda t: ordem_tarefas.get(t['nome'], 9999))
    if not todas_tarefas:
        print('[DEBUG] Nenhuma tarefa encontrada, criando dados de exemplo')
        gantt_geral_data = [
            {
                'id': 'projeto_geral',
                'name': 'Projeto Geral',
                'start': '2025-01-01',
                'end': '2025-01-25',
                'progress': 0,
                'dependencies': '',
                'custom_class': 'project-group',
                'type': 'project'
            },
            {
                'id': '1',
                'name': 'Tarefa de Exemplo 1',
                'start': '2025-01-01',
                'end': '2025-01-15',
                'progress': 50,
                'dependencies': '',
                'custom_class': 'status-pendente',
                'projeto_origem': 'Projeto Geral',
                'type': 'task',
                'ordem': 1
            }
        ]
    else:
        # Definir cores únicas para cada projeto
        cor_idx = 0
        cores = [
            '#ffc107', '#17a2b8', '#28a745', '#fd7e14', '#6f42c1', '#e83e8c', '#20c997', '#007bff', '#dc3545', '#343a40'
        ]
        for t in todas_tarefas:
            projeto_nome = t.get('projeto_origem', 'Projeto não encontrado')
            if projeto_nome not in cor_projetos:
                cor_projetos[projeto_nome] = cores[cor_idx % len(cores)]
                cor_idx += 1
        for t in todas_tarefas:
            gantt_geral_data.append({
                'id': t.get('id'),
                'name': t.get('nome'),
                'start': t.get('data_inicio_iso'),
                'end': t.get('data_fim_iso'),
                'progress': 0,
                'dependencies': '',
                'custom_class': 'status-pendente',
                'projeto_origem': t.get('projeto_origem'),
                'type': 'task',
                'ordem': ordem_tarefas.get(t.get('nome'), 9999),
                'bar_color': cor_projetos[t.get('projeto_origem', 'Projeto não encontrado')],
                'colecao': t.get('colecao', '')
            })
    # Buscar todas as coleções disponíveis no banco (não apenas das tarefas filtradas)
    try:
        # Buscar todas as coleções distintas do banco
        url_colecoes = f"{SUPABASE_URL}/rest/v1/tarefas?select=colecao&colecao=not.is.null"
        resp_colecoes = requests.get(url_colecoes, headers=headers)
        if resp_colecoes.status_code == 200:
            todas_tarefas_colecao = resp_colecoes.json()
            colecoes = sorted(set(
                (str(t.get('colecao', '') or '').strip())
                for t in todas_tarefas_colecao
                if (str(t.get('colecao', '') or '').strip())
            ))
        else:
            # Fallback: usar apenas das tarefas filtradas
            colecoes = sorted(set(
                (str(t.get('colecao', '') or '').strip())
                for t in tarefas_filtradas
                if (str(t.get('colecao', '') or '').strip())
            ))
    except Exception:
        # Fallback: usar apenas das tarefas filtradas
        colecoes = sorted(set(
            (str(t.get('colecao', '') or '').strip())
            for t in tarefas_filtradas
            if (str(t.get('colecao', '') or '').strip())
        ))
    return render_template('projetos_gantt_basico.html', projetos=projetos, gantt_geral_data=gantt_geral_data, projects_colors=cor_projetos, colecoes=colecoes)

# Rota de criação de projeto
@app.route('/projetos/criar', methods=['GET', 'POST'])
@login_required
def criar_projeto():
    if funcionalidade_restrita('restr_criar_projeto'):
        flash('Acesso restrito para criar projetos.')
        return redirect(url_for('projetos'))
    usuario_id = session['user_id']
    usuario_email = session.get('user_nome', '')

    if request.method == 'POST':
        print('usuario_id:', usuario_id)
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']

        # Validação de dados
        erro = validar_projeto(nome, data_inicio, data_fim)
        if erro:
            flash(erro)
            return render_template('novo_projeto.html')  # Exibe o formulário novamente com o erro

        try:
            # Inserindo o projeto no banco de dados
            data = {
                "nome": nome,
                "descricao": descricao,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "usuario_id": usuario_id
            }
            print('Dados do projeto:', data)
            resp = supabase.table("projetos").insert(data).execute()
            print('Resposta do Supabase:', resp)
            if hasattr(resp, 'data') and resp.data:
                flash("Projeto criado com sucesso!")
                return redirect('/projetos')
            else:
                flash(f"Erro ao criar o projeto: {resp}")
        except Exception as e:
            flash(f"Erro ao criar o projeto: {str(e)}")
            print(f"Erro ao criar o projeto: {e}")
            return render_template('novo_projeto.html')  # Exibe o formulário em caso de erro

    return render_template('novo_projeto.html')  # Exibe o formulário de criação de projeto

# Rota de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email'].strip().lower()
        senha = request.form['senha']
        if get_user_by_email(email):
            flash('E-mail já cadastrado.')
            return render_template('cadastro.html')
        senha_hash = generate_password_hash(senha)
        print("Dados enviados para o Supabase:", {
            "nome": nome,
            "email": email,
            "senha_hash": senha_hash
        })
        # Usar a função utilitária para criar usuário
        sucesso = create_user(nome, email, senha_hash)
        if sucesso:
            flash('Cadastro realizado com sucesso! Faça login.')
            return redirect(url_for('login'))
        else:
            flash("Erro ao cadastrar usuário. Tente novamente mais tarde.")
    return render_template('cadastro.html')

# Detalhes do projeto
@app.route('/projetos/<uuid:projeto_id>')
@login_required
def detalhes_projeto(projeto_id):
    resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).single().execute()
    projeto = resp.data if hasattr(resp, 'data') else None
    if not projeto:
        flash("Projeto não encontrado.")
        return redirect('/projetos')
    # Buscar as tarefas do projeto via requests puro
    SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
    url = f"{SUPABASE_URL}/rest/v1/tarefas?projeto_id=eq.{projeto_id}&order=ordem"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    tarefas = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tarefas = response.json()
        else:
            flash(f"Erro ao buscar tarefas: {response.text}")
    except Exception as e:
        flash(f"Erro ao buscar tarefas: {str(e)}")
    # Buscar informações dos usuários para as tarefas (mantém via supabase-py)
    if tarefas:
        usuario_ids = list(set([tarefa.get('usuario_id') for tarefa in tarefas if tarefa.get('usuario_id')]))
        if usuario_ids:
            usuarios_resp = supabase.table("usuarios").select("id, nome, email").in_("id", usuario_ids).execute()
            usuarios_dict = {usuario['id']: usuario for usuario in usuarios_resp.data}
            for tarefa in tarefas:
                if tarefa.get('usuario_id') and tarefa['usuario_id'] in usuarios_dict:
                    tarefa['usuarios'] = usuarios_dict[tarefa['usuario_id']]
                else:
                    tarefa['usuarios'] = None
    try:
        projeto['data_inicio'] = datetime.strptime(projeto['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')
        projeto['data_fim'] = datetime.strptime(projeto['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')
    except Exception as e:
        projeto['data_inicio'] = ''
        projeto['data_fim'] = ''
    for tarefa in tarefas:
        if tarefa.get('data_inicio'):
            try:
                dt_inicio = datetime.strptime(tarefa['data_inicio'], '%Y-%m-%d')
                tarefa['data_inicio'] = dt_inicio.strftime('%d/%m/%Y')
                tarefa['data_inicio_iso'] = dt_inicio.strftime('%Y-%m-%d')
            except Exception:
                tarefa['data_inicio'] = ''
                tarefa['data_inicio_iso'] = ''
        else:
            tarefa['data_inicio'] = ''
            tarefa['data_inicio_iso'] = ''
        if tarefa.get('data_fim'):
            try:
                dt_fim = datetime.strptime(tarefa['data_fim'], '%Y-%m-%d')
                tarefa['data_fim'] = dt_fim.strftime('%d/%m/%Y')
                tarefa['data_fim_iso'] = dt_fim.strftime('%Y-%m-%d')
            except Exception:
                tarefa['data_fim'] = ''
                tarefa['data_fim_iso'] = ''
        else:
            tarefa['data_fim'] = ''
            tarefa['data_fim_iso'] = ''
        tarefa['data_inicio_calculada'] = False
        tarefa['data_fim_calculada'] = False
        preds = tarefa.get('predecessoras')
        if preds:
            preds_list = [p.strip() for p in preds.split(';') if p.strip()]
            for pred in preds_list:
                if 'FS' in pred or 'SS' in pred:
                    tarefa['data_inicio_calculada'] = True
                if 'FF' in pred or 'SF' in pred:
                    tarefa['data_fim_calculada'] = True
    def extrair_links(tarefas):
        links = []
        for tarefa in tarefas:
            pred_str = tarefa.get('predecessoras')
            if pred_str:
                preds = [p.strip() for p in pred_str.split(';') if p.strip()]
                for pred in preds:
                    links.append({
                        "id": f"{pred}_{tarefa['id']}",
                        "source": pred,
                        "target": tarefa['id'],
                        "type": "0"
                    })
        return links
    all_links = extrair_links(tarefas)
    def tarefas_para_gantt(tarefas):
        tarefas_gantt = []
        for t in tarefas:
            tarefas_gantt.append({
                "id": t["id"],
                "text": t.get("nome", ""),
                "start_date": t.get("data_inicio_iso", ""),
                "duration": t.get("duracao", 1),
            })
        return tarefas_gantt
    tarefas_gantt = tarefas_para_gantt(tarefas)
    usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
    usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    # --- NOVO: lógica de permissões ---
    usuario_email = session.get('user_email')
    usuario_id = session.get('user_id')
    is_admin = usuario_email == 'izak.gomes59@gmail.com'
    is_owner = projeto.get('usuario_id') == usuario_id
    restricoes = carregar_restricoes()
    restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
    pode_editar_projeto = is_admin or is_owner or not restricoes_usuario.get('restr_editar_projeto', False)
    pode_editar_tarefa = is_admin or is_owner or not restricoes_usuario.get('restr_editar_tarefa', False)
    pode_criar_tarefa = is_admin or is_owner or not restricoes_usuario.get('restr_criar_tarefa', False)
    pode_excluir_tarefa = is_admin or is_owner or not restricoes_usuario.get('restr_excluir_tarefa', False)
    pode_editar_responsavel = is_admin or is_owner or not restricoes_usuario.get('restr_editar_responsavel', False)
    pode_editar_duracao = is_admin or is_owner or not restricoes_usuario.get('restr_editar_duracao', False)
    pode_editar_data_inicio = is_admin or is_owner or not restricoes_usuario.get('restr_editar_data_inicio', False)
    pode_editar_data_termino = is_admin or is_owner or not restricoes_usuario.get('restr_editar_data_termino', False)
    pode_editar_predecessoras = is_admin or is_owner or not restricoes_usuario.get('restr_editar_predecessoras', False)
    pode_editar_nome_tarefa = is_admin or is_owner or not restricoes_usuario.get('restr_editar_nome_tarefa', False)
    # --- FIM NOVO ---
    return render_template(
        'detalhes_projeto.html',
        projeto=projeto,
        tarefas=tarefas,
        tarefas_gantt=tarefas_gantt,
        all_links=all_links,
        usuarios=usuarios,
        pode_editar_projeto=pode_editar_projeto,
        pode_editar_tarefa=pode_editar_tarefa,
        pode_criar_tarefa=pode_criar_tarefa,
        pode_excluir_tarefa=pode_excluir_tarefa,
        pode_editar_responsavel=pode_editar_responsavel,
        pode_editar_duracao=pode_editar_duracao,
        pode_editar_data_inicio=pode_editar_data_inicio,
        pode_editar_data_termino=pode_editar_data_termino,
        pode_editar_predecessoras=pode_editar_predecessoras,
        pode_editar_nome_tarefa=pode_editar_nome_tarefa,
        is_admin=is_admin,
        is_owner=is_owner
    )

# Editar projeto
@app.route('/projetos/editar/<uuid:projeto_id>', methods=['GET', 'POST'])
@login_required
def editar_projeto(projeto_id):
    if funcionalidade_restrita('restr_editar_projeto'):
        flash('Acesso restrito para editar projetos.')
        return redirect(url_for('projetos'))
    resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).single().execute()
    projeto = resp.data if hasattr(resp, 'data') else None
    if not projeto:
        flash("Projeto não encontrado.")
        return redirect('/projetos')
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        print('Atualizando projeto:', projeto_id)
        print('Novos dados:', nome, descricao, data_inicio, data_fim)
        update_resp = supabase.table("projetos").update({
            "nome": nome,
            "descricao": descricao,
            "data_inicio": data_inicio,
            "data_fim": data_fim
        }).eq("id", str(projeto_id)).execute()
        print('Resposta do update:', update_resp)
        flash("Projeto atualizado com sucesso!")
        return redirect(f'/projetos/{projeto_id}')
    return render_template('editar_projeto.html', projeto=projeto)

# Excluir projeto
@app.route('/projetos/excluir/<uuid:projeto_id>', methods=['POST'])
@login_required
def excluir_projeto(projeto_id):
    if funcionalidade_restrita('restr_excluir_projeto'):
        flash('Acesso restrito para excluir projetos.')
        return redirect(url_for('projetos'))
    supabase.table("projetos").delete().eq("id", str(projeto_id)).execute()
    flash("Projeto excluído com sucesso!")
    return redirect('/projetos')

# Função utilitária para normalizar campos opcionais
def normaliza_opcional(valor):
    return valor if valor not in [None, ''] else None

# Rota para criar uma nova tarefa vinculada a um projeto
@app.route('/tarefas/criar/<uuid:projeto_id>', methods=['GET', 'POST'])
@login_required
def criar_tarefa(projeto_id):
    # Buscar projeto para checar dono
    resp = supabase.table("projetos").select("usuario_id").eq("id", str(projeto_id)).single().execute()
    projeto = resp.data if hasattr(resp, 'data') else None
    usuario_email = session.get('user_email')
    usuario_id = session.get('user_id')
    is_admin = usuario_email == 'izak.gomes59@gmail.com'
    is_owner = projeto and projeto.get('usuario_id') == usuario_id
    restricoes = carregar_restricoes()
    restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
    pode_criar_tarefa = is_admin or is_owner or (restricoes_usuario.get('restr_criar_tarefa') == True)
    if not pode_criar_tarefa:
        flash('Acesso restrito para criar tarefas.')
        return redirect(f'/projetos/{projeto_id}')
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        status = request.form.get('status', 'pendente')
        if status not in ['pendente', 'em_andamento', 'concluida']:
            status = 'pendente'
        usuario_designado = normaliza_opcional(request.form.get('usuario_id'))
        usuario_id = session['user_id']
        predecessoras = request.form.getlist('predecessoras')
        predecessoras_str = normaliza_opcional(','.join(predecessoras) if predecessoras else None)
        duracao = normaliza_opcional(request.form.get('duracao'))
        colecao = request.form.get('colecao')

        dados_tarefa = {
            "nome": nome,
            "descricao": descricao,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "status": status,
            "projeto_id": str(projeto_id),
            "usuario_id": usuario_designado,
            "predecessoras": predecessoras_str,
            "duracao": duracao,
            "colecao": colecao
        }
        print("[DEBUG] Dados enviados para o Supabase (tarefa):", dados_tarefa)
        # Inserção via requests puro
        SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
        url = f"{SUPABASE_URL}/rest/v1/tarefas"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        import requests
        resp = requests.post(url, headers=headers, json=dados_tarefa)
        if resp.status_code not in [200, 201]:
            flash(f"Erro ao criar tarefa: {resp.text}")
        else:
            flash("Tarefa criada com sucesso!")
        return redirect(request.referrer or f'/projetos/{projeto_id}')
    # Buscar o projeto, usuários e tarefas do projeto
    resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).single().execute()
    projeto = resp.data if hasattr(resp, 'data') else None
    usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
    usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    tarefas_resp = supabase.table("tarefas").select("id, nome").eq("projeto_id", str(projeto_id)).execute()
    tarefas_projeto = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []
    return render_template('criar_tarefa.html', projeto=projeto, projeto_id=projeto_id, usuarios=usuarios, tarefas_projeto=tarefas_projeto)

# Rota para editar uma tarefa
@app.route('/tarefas/editar/<uuid:tarefa_id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(tarefa_id):
    if request.method == 'GET':
        # Buscar dados da tarefa
        SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
        url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        import requests
        resp = requests.get(url, headers=headers)
        tarefa = resp.json()[0] if resp.status_code == 200 and resp.json() else None
        if not tarefa:
            flash("Tarefa não encontrada.")
            return redirect(request.referrer or '/')
        # Buscar lista de usuários para atribuição
        usuarios_resp = requests.get(f"{SUPABASE_URL}/rest/v1/usuarios", headers=headers)
        usuarios = usuarios_resp.json() if usuarios_resp.status_code == 200 else []
        return render_template('editar_tarefa.html', tarefa=tarefa, usuarios=usuarios)
    else:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            nome = data.get('nome')
            data_inicio = data.get('data_inicio')
            data_fim = data.get('data_fim')
            status = data.get('status', 'pendente')
            if status not in ['pendente', 'em progresso', 'concluída']:
                status = 'pendente'
            usuario_id = normaliza_opcional(data.get('usuario_id'))
            dados_update = {
                "nome": nome,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "status": status,
                "usuario_id": usuario_id
            }
            if 'colecao' in data:
                dados_update["colecao"] = data.get('colecao')
            if 'predecessoras' in data:
                dados_update["predecessoras"] = normaliza_opcional(data.get('predecessoras'))
            if 'duracao' in data:
                dados_update["duracao"] = normaliza_opcional(data.get('duracao'))
            SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
            SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
            url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            import requests
            resp = requests.patch(url, headers=headers, json=dados_update)
            if resp.status_code not in [200, 204]:
                return jsonify({"sucesso": False, "erro": resp.text}), 400
            return jsonify({"sucesso": True})
        else:
            nome = request.form['nome']
            data_inicio = request.form.get('data_inicio')
            data_fim = request.form.get('data_fim')
            status = request.form.get('status', 'pendente')
            if status not in ['pendente', 'em progresso', 'concluída']:
                status = 'pendente'
            usuario_id = normaliza_opcional(request.form.get('usuario_id'))
            dados_update = {
                "nome": nome,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "status": status,
                "usuario_id": usuario_id
            }
            if 'colecao' in request.form:
                dados_update["colecao"] = request.form.get('colecao')
            if 'predecessoras' in request.form:
                dados_update["predecessoras"] = normaliza_opcional(request.form.get('predecessoras'))
            if 'duracao' in request.form:
                dados_update["duracao"] = normaliza_opcional(request.form.get('duracao'))
            SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
            SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
            url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            import requests
            resp = requests.patch(url, headers=headers, json=dados_update)
            if resp.status_code not in [200, 204]:
                flash(f"Erro ao editar tarefa: {resp.text}")
            else:
                flash("Tarefa editada com sucesso!")
            return redirect(request.referrer or '/')

# Rota para excluir uma tarefa
@app.route('/tarefas/excluir/<uuid:tarefa_id>', methods=['POST'])
@login_required
def excluir_tarefa(tarefa_id):
    if funcionalidade_restrita('restr_excluir_tarefa'):
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"sucesso": False, "erro": "Acesso restrito para excluir tarefas."}), 403
        else:
            flash('Acesso restrito para excluir tarefas.')
            return redirect(url_for('projetos'))
    
    # Buscar a tarefa para obter o projeto_id
    tarefa_resp = supabase.table("tarefas").select("projeto_id").eq("id", str(tarefa_id)).single().execute()
    tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None

    if not tarefa:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"sucesso": False, "erro": "Tarefa não encontrada."}), 404
        else:
            flash("Tarefa não encontrada.")
            return redirect('/projetos')

    # Excluir a tarefa via requests puro
    SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
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

# Rota para marcar tarefa como concluída
@app.route('/tarefas/concluir/<uuid:tarefa_id>', methods=['POST'])
@login_required
def concluir_tarefa(tarefa_id):
    # Buscar a tarefa para obter o projeto_id
    tarefa_resp = supabase.table("tarefas").select("projeto_id").eq("id", str(tarefa_id)).single().execute()
    tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None
    
    if not tarefa:
        flash("Tarefa não encontrada.")
        return redirect('/projetos')
    
    # Marcar como concluída
    supabase.table("tarefas").update({
        "status": "concluida"
    }).eq("id", str(tarefa_id)).execute()
    
    flash("Tarefa marcada como concluída!")
    return redirect(f'/tarefas/{tarefa["projeto_id"]}')

# Rota do dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    usuario_id = session['user_id']
    
    # Buscar estatísticas dos projetos
    projetos_resp = supabase.table("projetos").select("*").eq("usuario_id", usuario_id).execute()
    projetos = projetos_resp.data if hasattr(projetos_resp, 'data') else []
    
    # Buscar estatísticas das tarefas
    tarefas_resp = supabase.table("tarefas").select("*").execute()
    tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []
    
    # Filtrar tarefas que pertencem aos projetos do usuário
    projeto_ids = [projeto['id'] for projeto in projetos]
    tarefas = [tarefa for tarefa in tarefas if tarefa.get('projeto_id') in projeto_ids]
    
    # Buscar informações dos projetos para as tarefas
    if tarefas:
        projeto_ids_tarefas = list(set([tarefa.get('projeto_id') for tarefa in tarefas if tarefa.get('projeto_id')]))
        if projeto_ids_tarefas:
            projetos_resp_tarefas = supabase.table("projetos").select("id, nome").in_("id", projeto_ids_tarefas).execute()
            projetos_dict = {projeto['id']: projeto for projeto in projetos_resp_tarefas.data}
            
            # Adicionar informações do projeto a cada tarefa
            for tarefa in tarefas:
                if tarefa.get('projeto_id') and tarefa['projeto_id'] in projetos_dict:
                    tarefa['projetos'] = projetos_dict[tarefa['projeto_id']]
                else:
                    tarefa['projetos'] = None
    
    # Calcular estatísticas
    total_projetos = len(projetos)
    projetos_em_andamento = len([p for p in projetos if p.get('status') == 'em progresso'])
    projetos_concluidos = len([p for p in projetos if p.get('status') == 'concluída'])
    
    total_tarefas = len(tarefas)
    tarefas_pendentes = len([t for t in tarefas if t.get('status') == 'pendente'])
    tarefas_em_andamento = len([t for t in tarefas if t.get('status') == 'em progresso'])
    tarefas_concluidas = len([t for t in tarefas if t.get('status') == 'concluída'])
    
    # Projetos recentes (últimos 5)
    projetos_recentes = sorted(projetos, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    # Tarefas recentes (últimas 5)
    tarefas_recentes = sorted(tarefas, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    # Formatar datas
    for projeto in projetos_recentes:
        if projeto.get('data_inicio'):
            projeto['data_inicio'] = datetime.strptime(projeto['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')
        if projeto.get('data_fim'):
            projeto['data_fim'] = datetime.strptime(projeto['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')
    
    for tarefa in tarefas_recentes:
        if tarefa.get('data_inicio'):
            tarefa['data_inicio'] = datetime.strptime(tarefa['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')
        if tarefa.get('data_fim'):
            tarefa['data_fim'] = datetime.strptime(tarefa['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')
    
    return render_template('dashboard.html', 
                         total_projetos=total_projetos,
                         projetos_em_andamento=projetos_em_andamento,
                         projetos_concluidos=projetos_concluidos,
                         total_tarefas=total_tarefas,
                         tarefas_pendentes=tarefas_pendentes,
                         tarefas_em_andamento=tarefas_em_andamento,
                         tarefas_concluidas=tarefas_concluidas,
                         projetos_recentes=projetos_recentes,
                         tarefas_recentes=tarefas_recentes)

@app.route('/tarefas/status/<uuid:tarefa_id>/<novo_status>', methods=['POST'])
@login_required
def atualizar_status_tarefa(tarefa_id, novo_status):
    # Buscar a tarefa para obter o projeto_id, nome, usuario_id
    tarefa_resp = supabase.table("tarefas").select("projeto_id, nome, usuario_id").eq("id", str(tarefa_id)).single().execute()
    tarefa = tarefa_resp.data if hasattr(tarefa_resp, 'data') else None

    if not tarefa:
        flash("Tarefa não encontrada.")
        return redirect('/projetos')

    # Buscar nome do projeto
    projeto_nome = ""
    projeto_resp = supabase.table("projetos").select("nome").eq("id", tarefa["projeto_id"]).single().execute()
    if hasattr(projeto_resp, 'data') and projeto_resp.data:
        projeto_nome = projeto_resp.data.get('nome', '')
    # Buscar nome do responsável
    responsavel_nome = ""
    if tarefa.get('usuario_id'):
        usuario_resp = supabase.table("usuarios").select("nome").eq("id", tarefa["usuario_id"]).single().execute()
        if hasattr(usuario_resp, 'data') and usuario_resp.data:
            responsavel_nome = usuario_resp.data.get('nome', '')
    # Atualizar status via requests puro
    SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
    url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    dados_update = {"status": novo_status}
    response = requests.patch(url, headers=headers, json=dados_update)
    print("[DEBUG] Status code PATCH status:", response.status_code)
    print("[DEBUG] Resposta PATCH status:", response.text)
    if response.status_code not in [200, 204]:
        flash(f"Erro ao atualizar status: {response.text}")
    else:
        flash("Status da tarefa atualizado com sucesso!")
        # Enviar notificação ao admin
        assunto = f"Status da tarefa alterado: {tarefa['nome']}"
        mensagem = f"<p><b>Tarefa:</b> {tarefa['nome']}<br>"
        mensagem += f"<b>Novo status:</b> {novo_status.title()}<br>"
        mensagem += f"<b>Projeto:</b> {projeto_nome}<br>"
        mensagem += f"<b>Responsável:</b> {responsavel_nome or 'Não designado'}</p>"
        enviar_email_admin(assunto, mensagem)
    return redirect(f'/projetos/{tarefa["projeto_id"]}')

# Tela de administração de restrições
@app.route('/admin/restricoes', methods=['GET', 'POST'])
@apenas_admin_izak
@login_required
def admin_restricoes():
    usuarios = get_all_users()
    usuario_id = request.form.getlist('usuario_id') if request.method == 'POST' else request.args.getlist('usuario_id')
    restricoes = carregar_restricoes()
    restricoes_usuario = restricoes.get(usuario_id[0], {}) if usuario_id else {}
    # Buscar todos os projetos para o painel de permissões de visualização
    projetos = supabase.table("projetos").select("id, nome").execute().data or []
    print('[DEBUG] Lista de projetos para admin_restricoes:', projetos)
    projeto_id = request.args.get('projeto_id') or request.form.get('projeto_id')
    usuarios_visiveis = []
    if projeto_id:
        resp = supabase.table("projetos_usuarios_visiveis").select("usuario_id").eq("projeto_id", projeto_id).execute()
        usuarios_visiveis = [r['usuario_id'] for r in resp.data]
    if request.method == 'POST' and request.form.get('form_tipo') == 'visualizacao_projeto' and projeto_id:
        usuarios_selecionados = request.form.getlist('usuarios')
        supabase.table("projetos_usuarios_visiveis").delete().eq("projeto_id", projeto_id).execute()
        for uid in usuarios_selecionados:
            supabase.table("projetos_usuarios_visiveis").insert({"projeto_id": projeto_id, "usuario_id": uid}).execute()
        flash('Permissões de visualização atualizadas!')
        usuarios_visiveis = usuarios_selecionados
    if request.method == 'POST' and usuario_id and (not request.form.get('form_tipo') or request.form.get('form_tipo') == 'restricoes'):
        novas_restricoes = {
            'restr_criar_projeto': bool(request.form.get('restr_criar_projeto')),
            'restr_editar_projeto': bool(request.form.get('restr_editar_projeto')),
            'restr_excluir_projeto': bool(request.form.get('restr_excluir_projeto')),
            'restr_criar_tarefa': bool(request.form.get('restr_criar_tarefa')),
            'restr_editar_tarefa': bool(request.form.get('restr_editar_tarefa')),
            'restr_excluir_tarefa': bool(request.form.get('restr_excluir_tarefa')),
            'restr_editar_responsavel': bool(request.form.get('restr_editar_responsavel')),
            'restr_editar_duracao': bool(request.form.get('restr_editar_duracao')),
            'restr_editar_data_inicio': bool(request.form.get('restr_editar_data_inicio')),
            'restr_editar_data_termino': bool(request.form.get('restr_editar_data_termino')),
            'restr_editar_predecessoras': bool(request.form.get('restr_editar_predecessoras')),
            'restr_editar_nome_tarefa': bool(request.form.get('restr_editar_nome_tarefa')),
        }
        for uid in usuario_id:
            restricoes[uid] = novas_restricoes
        salvar_restricoes(restricoes)
        restricoes_usuario = novas_restricoes
        flash('Restrições salvas com sucesso!')
    return render_template('admin_restricoes.html', restricoes=restricoes_usuario, usuarios=usuarios, usuario_id=usuario_id, projetos=projetos, projeto_id=projeto_id, usuarios_visiveis=usuarios_visiveis)

@app.route('/admin/usuarios_visiveis_projeto')
@apenas_admin_izak
@login_required
def usuarios_visiveis_projeto():
    projeto_id = request.args.get('projeto_id')
    if not projeto_id:
        return jsonify({'usuarios_visiveis': []})
    resp = supabase.table("projetos_usuarios_visiveis").select("usuario_id").eq("projeto_id", projeto_id).execute()
    usuarios_visiveis = [r['usuario_id'] for r in resp.data]
    return jsonify({'usuarios_visiveis': usuarios_visiveis})

def enviar_email_admin(assunto, mensagem):
    admin_email = os.getenv('ADMIN_EMAIL')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    if not all([admin_email, smtp_server, smtp_user, smtp_pass]):
        print('Configuração de e-mail incompleta. Notificação não enviada.')
        return
    # Garantir que todas as variáveis são string
    admin_email = str(admin_email)
    smtp_server = str(smtp_server)
    smtp_user = str(smtp_user)
    smtp_pass = str(smtp_pass)
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = admin_email
    msg['Subject'] = assunto
    msg.attach(MIMEText(mensagem, 'html'))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, admin_email, msg.as_string())
        print('Notificação enviada para o administrador.')
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')

@app.route('/projetos/<uuid:projeto_id>/criar_tarefa_rapida', methods=['POST'])
@login_required
def criar_tarefa_rapida(projeto_id):
    data = request.get_json()
    nome = data.get('nome')
    predecessoras = data.get('predecessoras')
    data_inicio = data.get('data_inicio')
    data_fim = data.get('data_fim')
    status = data.get('status', 'pendente')
    if status not in ['pendente', 'em progresso', 'concluída']:
        status = 'pendente'
    # Corrigir datas vazias para None
    if not data_inicio:
        data_inicio = None
    if not data_fim:
        data_fim = None
    # Buscar o maior valor de ordem para o projeto
    SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    import requests
    try:
        url_ordem = f"{SUPABASE_URL}/rest/v1/tarefas?projeto_id=eq.{projeto_id}&select=ordem&order=ordem.desc&limit=1"
        resp_ordem = requests.get(url_ordem, headers=headers)
        maior_ordem = 0
        if resp_ordem.status_code == 200 and resp_ordem.json():
            maior_ordem = resp_ordem.json()[0].get('ordem') or 0
        nova_ordem = (maior_ordem or 0) + 1
    except Exception as e:
        print('[DEBUG] Erro ao buscar maior ordem:', e)
        nova_ordem = 1
    # Montar dados para o Supabase
    dados_tarefa = {
        "nome": nome,
        "descricao": "",
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "status": status,
        "projeto_id": str(projeto_id),
        "usuario_id": None,
        "predecessoras": predecessoras,
        "ordem": nova_ordem
    }
    print('[DEBUG] Dados enviados para o Supabase:', dados_tarefa)
    url = f"{SUPABASE_URL}/rest/v1/tarefas"
    resp = requests.post(url, headers=headers, json=dados_tarefa)
    print('[DEBUG] Status code:', resp.status_code)
    print('[DEBUG] Resposta do Supabase:', resp.text)
    if resp.status_code not in [200, 201]:
        return jsonify({"sucesso": False, "erro": resp.text}), 400
    
    # Se a resposta estiver vazia (comum no Supabase), buscar a tarefa criada
    tarefa = None
    if resp.text.strip():
        try:
            tarefa = resp.json()[0] if resp.json() else None
        except:
            pass
    
    # Se não conseguiu pegar a tarefa da resposta, buscar pelo nome
    if not tarefa:
        try:
            print('[DEBUG] Tentando buscar tarefa criada pelo nome...')
            # Buscar a tarefa recém-criada pelo nome
            url_busca = f"{SUPABASE_URL}/rest/v1/tarefas?nome=eq.{nome}&projeto_id=eq.{projeto_id}"
            print('[DEBUG] URL de busca:', url_busca)
            resp_busca = requests.get(url_busca, headers=headers)
            print('[DEBUG] Status da busca:', resp_busca.status_code)
            print('[DEBUG] Resposta da busca:', resp_busca.text)
            if resp_busca.status_code == 200 and resp_busca.json():
                tarefa = resp_busca.json()[0]
                print('[DEBUG] Tarefa encontrada na busca:', tarefa)
            else:
                print('[DEBUG] Nenhuma tarefa encontrada na busca')
        except Exception as e:
            print('[DEBUG] Erro ao buscar tarefa criada:', e)
    
    if not tarefa:
        print('[DEBUG] Nenhuma tarefa encontrada, retornando erro')
        return jsonify({"sucesso": False, "erro": "Erro ao criar tarefa."}), 400
    # Após criar a tarefa, buscar o valor atualizado de 'ordem' da tarefa criada
    if not tarefa or 'ordem' not in tarefa or not tarefa['ordem']:
        # Buscar pelo id da tarefa criada
        try:
            tarefa_id = tarefa['id'] if tarefa else None
            if tarefa_id:
                url_busca = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
                resp_busca = requests.get(url_busca, headers=headers)
                if resp_busca.status_code == 200 and resp_busca.json():
                    tarefa = resp_busca.json()[0]
        except Exception as e:
            print('[DEBUG] Erro ao buscar tarefa criada para pegar ordem:', e)
    # Renderizar HTML da nova linha (editável) igual ao template
    usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
    usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
    html_linha = render_template_string('''
    <tr>
        <td class="drag-handle" style="cursor: grab; text-align:center; font-size:1.3em; color:#888;">&#9776;</td>
        <td class="numero-tarefa">{{ tarefa.ordem or '' }}</td>
        <td><input type="text" class="form-control form-control-sm" value="{{ tarefa.nome }}" data-id="{{ tarefa.id }}" name="nome"></td>
        <td class="predecessoras-td">
            <button type="button" class="btn btn-outline-secondary btn-sm btn-predecessora" onclick="abrirModalPredecessora(this)"><i class="fas fa-link"></i></button>
            <input type="text" class="form-control form-control-sm" value="{{ tarefa.predecessoras or '' }}" data-id="{{ tarefa.id }}" name="predecessoras" placeholder="Ex: 2FS+2d" onchange="onPredecessorasEdit(this)" onkeyup="onPredecessorasEdit(this)">
        </td>
        <td><input type="date" class="form-control form-control-sm" value="{{ tarefa.data_inicio or '' }}" data-id="{{ tarefa.id }}" name="data_inicio" oninput="onInicioOuFimEdit(this)"></td>
        <td><input type="date" class="form-control form-control-sm" value="{{ tarefa.data_fim or '' }}" data-id="{{ tarefa.id }}" name="data_fim" oninput="onInicioOuFimEdit(this);onDuracaoOuFimEdit(this)"></td>
        <td><input type="number" class="form-control form-control-sm" name="duracao" min="1" value="{{ tarefa.duracao or '' }}" oninput="onDuracaoOuFimEdit(this)" onblur="onInicioOuDuracaoEdit(this);salvarLinhaTarefa(this.closest('tr').querySelector('.btn-success'))"></td>
        <td>
            <select class="form-select form-select-sm" data-id="{{ tarefa.id }}" name="status">
                <option value="pendente" {% if tarefa.status == 'pendente' %}selected{% endif %}>Pendente</option>
                <option value="em progresso" {% if tarefa.status == 'em progresso' %}selected{% endif %}>Em Progresso</option>
                <option value="concluída" {% if tarefa.status == 'concluída' %}selected{% endif %}>Concluída</option>
            </select>
        </td>
        <td>
            <select class="form-select form-select-sm" name="usuario_id" data-id="{{ tarefa.id }}">
                <option value="" {% if not tarefa.usuario_id %}selected{% endif %}>Sem responsável</option>
                {% for usuario in usuarios %}
                <option value="{{ usuario.id }}" {% if tarefa.usuario_id==usuario.id %}selected{% endif %}>{{ usuario.email }}</option>
                {% endfor %}
            </select>
        </td>
        <td>
            <button class="btn btn-success btn-sm" onclick="salvarLinhaTarefa(this)"><i class="fas fa-save"></i></button>
            <button class="btn btn-danger btn-sm" onclick="excluirTarefa(this)"><i class="fas fa-trash"></i></button>
        </td>
    </tr>
    ''', tarefa=tarefa, usuarios=usuarios)
    return jsonify({"sucesso": True, "html_linha": html_linha})

@app.before_request
def intercept_unauthorized_ajax():
    if not session.get('user_id'):
        # Só intercepta se for AJAX (fetch) e não for a rota de login
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if request.endpoint not in ['login', 'static']:
                return jsonify({"sucesso": False, "erro": "Sessão expirada, faça login novamente."}), 401

@app.route('/tarefas/atualizar_ordem', methods=['POST'])
@login_required
def atualizar_ordem_tarefas():
    data = request.get_json()
    lista_ids = data.get('ids')
    if not lista_ids or not isinstance(lista_ids, list):
        return jsonify({'sucesso': False, 'erro': 'Lista de IDs não enviada.'}), 400
    SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    # Atualiza cada tarefa com o novo valor de ordem
    sucesso = True
    erros = []
    for idx, tarefa_id in enumerate(lista_ids):
        url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
        payload = {"ordem": idx + 1}
        resp = requests.patch(url, headers=headers, json=payload)
        if resp.status_code not in (200, 204):
            sucesso = False
            erros.append({"id": tarefa_id, "erro": resp.text})
    if sucesso:
        return jsonify({'sucesso': True})
    else:
        return jsonify({'sucesso': False, 'erros': erros}), 500

@app.route('/gantt-teste')
def gantt_teste():
    # Dados de exemplo para projetos e tarefas
    projetos = [
        {'id': 1, 'nome': 'Projeto A', 'descricao': 'Exemplo A', 'status': 'Concluído', 'data_inicio': '2025-03-01', 'data_fim': '2025-06-30'},
        {'id': 2, 'nome': 'Projeto B', 'descricao': 'Exemplo B', 'status': 'Em Progresso', 'data_inicio': '2025-04-15', 'data_fim': '2025-09-10'},
    ]
    gantt_geral_data = [
        {'name': 'Tarefa 1', 'start': '2025-03-01', 'end': '2025-04-15', 'projeto_nome': 'Projeto A', 'status': 'pendente', 'ordem': 1},
        {'name': 'Tarefa 2', 'start': '2025-04-16', 'end': '2025-06-30', 'projeto_nome': 'Projeto A', 'status': 'em-progresso', 'ordem': 2},
        {'name': 'Tarefa 3', 'start': '2025-04-20', 'end': '2025-09-10', 'projeto_nome': 'Projeto B', 'status': 'concluida', 'ordem': 3},
    ]
    return render_template('projetos_gantt_basico.html', projetos=projetos, gantt_geral_data=gantt_geral_data)

if __name__ == '__main__':
    app.run(debug=True)
