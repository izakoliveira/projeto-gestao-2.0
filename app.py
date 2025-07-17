import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, flash, make_response, url_for, jsonify, render_template_string, abort
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
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            senha = data.get('senha')
            lembrar = data.get('lembrar', False)
        else:
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha')
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
            usuario_id_tarefa = tarefa.get('usuario_id')
            print('[DEBUG] usuario_id tarefa:', tarefa.get('id'), usuario_id_tarefa)
            if not usuario_id_tarefa or usuario_id_tarefa == '' or usuario_id_tarefa is None:
                tarefa['usuario_nome'] = 'Não designado'
            else:
                tarefa['usuario_nome'] = usuarios_dict.get(usuario_id_tarefa, 'Não designado')
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
        gantt_geral_data = []
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
        if request.is_json:
            data = request.get_json()
            nome = data.get('nome')
            descricao = data.get('descricao', '')
            data_inicio = data.get('data_inicio')
            data_fim = data.get('data_fim')
        else:
            nome = request.form.get('nome')
            descricao = request.form.get('descricao', '')
            data_inicio = request.form.get('data_inicio')
            data_fim = request.form.get('data_fim')

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

    # --- NOVO: Gerar dados para Gantt customizado ---
    gantt_geral_data = []
    cor_projetos = {}
    cores = [
        '#ffc107', '#17a2b8', '#28a745', '#fd7e14', '#6f42c1', '#e83e8c', '#20c997', '#007bff', '#dc3545', '#343a40'
    ]
    
    # Buscar ordem das tarefas
    tarefas_unicas = supabase.table('tarefas_unicas').select('nome, ordem').order('ordem').execute().data
    ordem_tarefas = {t['nome']: t['ordem'] for t in tarefas_unicas}
    
    # Processar tarefas para o Gantt customizado
    for t in tarefas:
        if t.get('data_inicio_iso') and t.get('data_fim_iso'):
            # Definir cor única para o projeto
            projeto_nome = projeto.get('nome', 'Projeto não encontrado')
            if projeto_nome not in cor_projetos:
                cor_projetos[projeto_nome] = cores[len(cor_projetos) % len(cores)]
            
            gantt_geral_data.append({
                'id': t.get('id'),
                'name': t.get('nome'),
                'start': t.get('data_inicio_iso'),
                'end': t.get('data_fim_iso'),
                'progress': 0,
                'dependencies': '',
                'custom_class': 'status-pendente',
                'projeto_origem': projeto_nome,
                'type': 'task',
                'ordem': ordem_tarefas.get(t.get('nome'), 9999),
                'bar_color': cor_projetos[projeto_nome],
                'colecao': t.get('colecao', ''),
                'status': t.get('status', 'pendente')
            })
    
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
        gantt_geral_data=gantt_geral_data,
        projects_colors=cor_projetos,
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
    # Excluir todas as tarefas vinculadas ao projeto
    supabase.table("tarefas").delete().eq("projeto_id", str(projeto_id)).execute()
    # Excluir todas as permissões de visualização vinculadas ao projeto
    supabase.table("projetos_usuarios_visiveis").delete().eq("projeto_id", str(projeto_id)).execute()
    # Agora excluir o projeto
    resp = supabase.table("projetos").delete().eq("id", str(projeto_id)).execute()
    print('[DEBUG] Resposta ao tentar excluir projeto:', vars(resp))
    # Tenta extrair informações úteis
    status_code = getattr(resp, 'status_code', None)
    text = getattr(resp, 'text', None)
    data = getattr(resp, 'data', None)
    if status_code and status_code not in [200, 204]:
        flash(f"Erro ao excluir projeto: {text or resp}")
    elif data is not None and not data:
        flash("Projeto não foi excluído. Verifique se não há dependências ou restrições no banco.")
    else:
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
        if request.is_json:
            data = request.get_json()
            nome = data.get('nome')
            descricao = data.get('descricao', '')
            data_inicio = data.get('data_inicio')
            data_fim = data.get('data_fim')
            status = data.get('status', 'pendente')
            usuario_designado = normaliza_opcional(data.get('usuario_id'))
            predecessoras = data.get('predecessoras') or []
            predecessoras_str = normaliza_opcional(','.join(predecessoras) if isinstance(predecessoras, list) else predecessoras)
            duracao = normaliza_opcional(data.get('duracao'))
            colecao = data.get('colecao')
        else:
            nome = request.form.get('nome')
            descricao = request.form.get('descricao', '')
            data_inicio = request.form.get('data_inicio')
            data_fim = request.form.get('data_fim')
            status = request.form.get('status', 'pendente')
            usuario_designado = normaliza_opcional(request.form.get('usuario_id'))
            predecessoras = request.form.getlist('predecessoras')
            predecessoras_str = normaliza_opcional(','.join(predecessoras) if predecessoras else None)
            duracao = normaliza_opcional(request.form.get('duracao'))
            colecao = request.form.get('colecao')

        # Corrigir datas vazias ou só espaços para None
        if not data_inicio or not str(data_inicio).strip():
            data_inicio = None
        if not data_fim or not str(data_fim).strip():
            data_fim = None

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
            # Enviar e-mail ao responsável, se houver
            if usuario_designado:
                # Buscar e-mail e nome do responsável
                usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", usuario_designado).single().execute()
                if hasattr(usuario_resp, 'data') and usuario_resp.data:
                    responsavel_nome = usuario_resp.data.get('nome', '')
                    responsavel_email = usuario_resp.data.get('email', '')
                    # Buscar nome do projeto
                    projeto_nome = None
                    projeto_resp = supabase.table("projetos").select("nome").eq("id", str(projeto_id)).single().execute()
                    if hasattr(projeto_resp, 'data') and projeto_resp.data:
                        projeto_nome = projeto_resp.data.get('nome', '')
                    # Montar e enviar o e-mail
                    assunto = f"Nova tarefa atribuída: {nome}"
                    mensagem = f"<p>Olá, <b>{responsavel_nome}</b>!</p>"
                    mensagem += f"<p>Você foi designado para a tarefa <b>{nome}</b> no projeto <b>{projeto_nome or projeto_id}</b>.</p>"
                    if data_inicio:
                        mensagem += f"<p><b>Início:</b> {data_inicio}</p>"
                    if data_fim:
                        mensagem += f"<p><b>Prazo:</b> {data_fim}</p>"
                    mensagem += f"<p>Descrição: {descricao or '-'}<br>Status: {status.title()}</p>"
                    # Função de envio adaptada
                    smtp_server = os.getenv('SMTP_SERVER')
                    smtp_port = int(os.getenv('SMTP_PORT', 587))
                    smtp_user = os.getenv('SMTP_USER')
                    smtp_pass = os.getenv('SMTP_PASS')
                    if all([responsavel_email, smtp_server, smtp_user, smtp_pass]):
                        from email.mime.text import MIMEText
                        from email.mime.multipart import MIMEMultipart
                        import smtplib
                        msg = MIMEMultipart()
                        msg['From'] = smtp_user
                        msg['To'] = responsavel_email
                        msg['Subject'] = assunto
                        msg.attach(MIMEText(mensagem, 'html'))
                        try:
                            with smtplib.SMTP(smtp_server, smtp_port) as server:
                                server.starttls()
                                server.login(smtp_user, smtp_pass)
                                server.sendmail(smtp_user, responsavel_email, msg.as_string())
                            print(f'E-mail enviado para {responsavel_email}')
                        except Exception as e:
                            print(f'Erro ao enviar e-mail para responsável: {e}')
                            flash(f'Erro ao enviar e-mail para o responsável: {e}', 'danger')
                    # --- Notificação interna ---
                    try:
                        notif_msg = f'Você foi designado para a tarefa "{nome}" no projeto "{projeto_nome or projeto_id}".'
                        print('[DEBUG] Notificação: projeto_id =', projeto_id)
                        # --- Validação robusta de projeto_id ---
                        if not (isinstance(projeto_id, str) and len(projeto_id) == 36 and '-' in projeto_id):
                            projeto_id = None
                        print('[DEBUG] Notificação: projeto_id =', repr(projeto_id))
                        notificacao = {
                            'mensagem': notif_msg,
                            'tipo': 'designacao'
                        }
                        if projeto_id:
                            notificacao['projeto_id'] = projeto_id
                        if usuario_designado:
                            notificacao['usuario_id'] = usuario_designado
                        supabase.table('notificacoes').insert(notificacao).execute()
                    except Exception as e:
                        print(f'Erro ao criar notificação interna: {e}')
        return redirect(f'/projetos/{projeto_id}')
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
    print('\n--- INÍCIO editar_tarefa ---')
    print('Método:', request.method)
    print('Headers:', dict(request.headers))
    print('Content-Type:', request.content_type)
    print('is_json:', request.is_json)
    try:
        print('request.get_json:', request.get_json(silent=True))
    except Exception as e:
        print('Erro ao ler get_json:', e)
    print('request.form:', request.form)
    print('request.data:', request.data)
    print('request.args:', request.args)
    print('--- FIM DIAGNÓSTICO INICIAL ---\n')
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
        # --- NOVO BLOCO: buscar dados conforme o tipo de requisição ---
        if request.is_json:
            dados = request.get_json()
        else:
            dados = request.form
        # Buscar responsável anterior ANTES de atualizar
        tarefa_antiga_resp = supabase.table("tarefas").select("usuario_id, data_inicio, data_fim, projeto_id").eq("id", str(tarefa_id)).single().execute()
        usuario_id_antigo = tarefa_antiga_resp.data.get('usuario_id') if hasattr(tarefa_antiga_resp, 'data') and tarefa_antiga_resp.data else None
        data_inicio_antigo = tarefa_antiga_resp.data.get('data_inicio') if hasattr(tarefa_antiga_resp, 'data') and tarefa_antiga_resp.data else None
        data_fim_antigo = tarefa_antiga_resp.data.get('data_fim') if hasattr(tarefa_antiga_resp, 'data') and tarefa_antiga_resp.data else None
        projeto_id = tarefa_antiga_resp.data.get('projeto_id') if hasattr(tarefa_antiga_resp, 'data') and tarefa_antiga_resp.data else None
        # Validação robusta de projeto_id
        if not (isinstance(projeto_id, str) and len(projeto_id) == 36 and '-' in projeto_id):
            projeto_id = None
        nome = dados.get('nome') or ''
        data_inicio = dados.get('data_inicio') or ''
        data_fim = dados.get('data_fim') or ''
        status = dados.get('status', 'pendente') or 'pendente'
        usuario_id = normaliza_opcional(dados.get('usuario_id')) or ''
        dados_update = {
            "nome": nome,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "status": status
        }
        if usuario_id:
            dados_update["usuario_id"] = usuario_id
        else:
            dados_update["usuario_id"] = None
        if 'colecao' in dados:
            dados_update["colecao"] = dados.get('colecao') or ''
        if 'predecessoras' in dados:
            dados_update["predecessoras"] = normaliza_opcional(dados.get('predecessoras')) or ''
        if 'duracao' in dados:
            dados_update["duracao"] = normaliza_opcional(dados.get('duracao')) or ''
        SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
        SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ""
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
        # Enviar e-mail se o responsável foi alterado ou designado
        if usuario_id and usuario_id != usuario_id_antigo:
            usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", usuario_id).single().execute()
            if hasattr(usuario_resp, 'data') and usuario_resp.data:
                responsavel_nome = usuario_resp.data.get('nome', '')
                responsavel_email = usuario_resp.data.get('email', '')
                tarefa_nome = nome
                projeto_nome = None
                if projeto_id:
                    projeto_resp = supabase.table("projetos").select("nome").eq("id", str(projeto_id)).single().execute()
                    if hasattr(projeto_resp, 'data') and projeto_resp.data:
                        projeto_nome = projeto_resp.data.get('nome', '')
                assunto = f"Nova tarefa atribuída: {tarefa_nome}"
                mensagem = f"<p>Olá, <b>{responsavel_nome}</b>!</p>"
                mensagem += f"<p>Você foi designado para a tarefa <b>{tarefa_nome}</b> no projeto <b>{projeto_nome or projeto_id}</b>.</p>"
                mensagem += f"<p>Status: {status.title()}</p>"
                smtp_server = os.getenv('SMTP_SERVER') or ''
                smtp_port = int(os.getenv('SMTP_PORT', 587))
                smtp_user = os.getenv('SMTP_USER') or ''
                smtp_pass = os.getenv('SMTP_PASS') or ''
                if all([responsavel_email, smtp_server, smtp_user, smtp_pass]):
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart
                    import smtplib
                    msg = MIMEMultipart()
                    msg['From'] = smtp_user
                    msg['To'] = responsavel_email
                    msg['Subject'] = assunto
                    msg.attach(MIMEText(mensagem, 'html'))
                    try:
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(smtp_user, smtp_pass)
                            server.sendmail(smtp_user, responsavel_email, msg.as_string())
                        print(f'E-mail enviado para {responsavel_email}')
                    except Exception as e:
                        print(f'Erro ao enviar e-mail para responsável: {e}')
                        flash(f'Erro ao enviar e-mail para o responsável: {e}', 'danger')
                # --- Notificação interna ---
                try:
                    notif_msg = f'Você foi designado para a tarefa "{tarefa_nome}" no projeto "{projeto_nome or projeto_id}".'
                    print('[DEBUG] Notificação: projeto_id =', projeto_id)
                    notificacao = {
                        'mensagem': notif_msg,
                        'tipo': 'designacao'
                    }
                    if projeto_id:
                        notificacao['projeto_id'] = projeto_id
                    if usuario_id:
                        notificacao['usuario_id'] = usuario_id
                    supabase.table('notificacoes').insert(notificacao).execute()
                except Exception as e:
                    print(f'Erro ao criar notificação interna: {e}')
        # Enviar e-mail se o responsável foi removido
        if usuario_id_antigo and not usuario_id:
            usuario_resp = supabase.table("usuarios").select("nome, email").eq("id", usuario_id_antigo).single().execute()
            if hasattr(usuario_resp, 'data') and usuario_resp.data:
                responsavel_nome = usuario_resp.data.get('nome', '')
                responsavel_email = usuario_resp.data.get('email', '')
                tarefa_nome = nome
                projeto_nome = None
                if projeto_id:
                    projeto_resp = supabase.table("projetos").select("nome").eq("id", str(projeto_id)).single().execute()
                    if hasattr(projeto_resp, 'data') and projeto_resp.data:
                        projeto_nome = projeto_resp.data.get('nome', '')
                assunto = f"Você foi removido da tarefa: {tarefa_nome}"
                mensagem = f"<p>Olá, <b>{responsavel_nome}</b>!</p>"
                mensagem += f"<p>Você não é mais o responsável pela tarefa <b>{tarefa_nome}</b> no projeto <b>{projeto_nome or projeto_id}</b>.</p>"
                if data_inicio_antigo:
                    mensagem += f"<p><b>Início:</b> {data_inicio_antigo}</p>"
                if data_fim_antigo:
                    mensagem += f"<p><b>Prazo:</b> {data_fim_antigo}</p>"
                smtp_server = os.getenv('SMTP_SERVER') or ''
                smtp_port = int(os.getenv('SMTP_PORT', 587))
                smtp_user = os.getenv('SMTP_USER') or ''
                smtp_pass = os.getenv('SMTP_PASS') or ''
                if all([responsavel_email, smtp_server, smtp_user, smtp_pass]):
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart
                    import smtplib
                    msg = MIMEMultipart()
                    msg['From'] = smtp_user
                    msg['To'] = responsavel_email
                    msg['Subject'] = assunto
                    msg.attach(MIMEText(mensagem, 'html'))
                    try:
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(smtp_user, smtp_pass)
                            server.sendmail(smtp_user, responsavel_email, msg.as_string())
                        print(f'E-mail enviado para {responsavel_email} (removido)')
                    except Exception as e:
                        print(f'Erro ao enviar e-mail para responsável removido: {e}')
                        flash(f'Erro ao enviar e-mail para o responsável removido: {e}', 'danger')
                # --- Notificação interna de remoção ---
                try:
                    notif_msg = f'Você não é mais o responsável pela tarefa "{tarefa_nome}" no projeto "{projeto_nome or projeto_id}".'
                    print('[DEBUG] Notificação (remoção): projeto_id =', projeto_id)
                    notificacao = {
                        'mensagem': notif_msg,
                        'tipo': 'remocao'
                    }
                    if projeto_id:
                        notificacao['projeto_id'] = projeto_id
                    if usuario_id_antigo:
                        notificacao['usuario_id'] = usuario_id_antigo
                    print('[DEBUG] Notificação (remoção) - projeto_id:', projeto_id)
                    print('[DEBUG] Notificação (remoção) - usuario_id_antigo:', usuario_id_antigo)
                    print('[DEBUG] Notificação (remoção) - notificacao dict:', notificacao)
                    resp_notif = supabase.table('notificacoes').insert(notificacao).execute()
                    print('[DEBUG] Resposta Supabase insert notificação:', getattr(resp_notif, 'data', None), getattr(resp_notif, 'error', None))
                except Exception as e:
                    print(f'Erro ao criar notificação interna de remoção: {e}')
        return jsonify({"sucesso": True})

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
    usuario_email = session.get('user_email')
    # Admin vê todos os projetos
    if usuario_email == 'izak.gomes59@gmail.com':
        projetos_resp = supabase.table("projetos").select("*").execute()
        projetos = projetos_resp.data if hasattr(projetos_resp, 'data') else []
    else:
        # Usuário comum vê apenas projetos autorizados
        resp = supabase.table("projetos_usuarios_visiveis").select("projeto_id").eq("usuario_id", usuario_id).execute()
        projetos_ids_visiveis = [r['projeto_id'] for r in resp.data]
        if projetos_ids_visiveis:
            projetos_resp = supabase.table("projetos").select("*").in_("id", projetos_ids_visiveis).execute()
            projetos = projetos_resp.data if hasattr(projetos_resp, 'data') else []
        else:
            projetos = []
    # Buscar estatísticas das tarefas
    tarefas_resp = supabase.table("tarefas").select("*").execute()
    tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []
    # Filtrar tarefas que pertencem aos projetos visíveis
    projeto_ids = [projeto['id'] for projeto in projetos]
    tarefas = [tarefa for tarefa in tarefas if tarefa.get('projeto_id') in projeto_ids]
    # Buscar informações dos projetos para as tarefas
    if tarefas:
        projeto_ids_tarefas = list(set([tarefa.get('projeto_id') for tarefa in tarefas if tarefa.get('projeto_id')]))
        if projeto_ids_tarefas:
            projetos_resp_tarefas = supabase.table("projetos").select("id, nome").in_("id", projeto_ids_tarefas).execute()
            projetos_dict = {projeto['id']: projeto for projeto in projetos_resp_tarefas.data}
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
        # Enviar notificação ao responsável se a tarefa foi concluída
        if novo_status in ['concluida', 'concluída'] and tarefa.get('usuario_id'):
            try:
                usuario_id = tarefa['usuario_id']
                tarefa_nome = tarefa['nome']
                projeto_id = tarefa['projeto_id']  # Corrigido: garantir que projeto_id está definido
                projeto_nome = projeto_nome or projeto_id
                notif_msg = f'A tarefa "{tarefa_nome}" no projeto "{projeto_nome}" foi marcada como concluída.'
                print('[DEBUG] Notificação: projeto_id =', projeto_id)
                # --- Validação robusta de projeto_id ---
                if not (isinstance(projeto_id, str) and len(projeto_id) == 36 and '-' in projeto_id):
                    projeto_id = None
                print('[DEBUG] Notificação: projeto_id =', repr(projeto_id))
                notificacao = {
                    'mensagem': notif_msg,
                    'tipo': 'conclusao'
                }
                if projeto_id:
                    notificacao['projeto_id'] = projeto_id
                if usuario_id:
                    notificacao['usuario_id'] = usuario_id
                supabase.table('notificacoes').insert(notificacao).execute()
            except Exception as e:
                print(f'Erro ao criar notificação interna de conclusão: {e}')
        # Enviar notificação ao admin (já existente)
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
            'restr_editar_datas': bool(request.form.get('restr_editar_datas')),
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
    admin_email = os.getenv('ADMIN_EMAIL') or ''
    smtp_server = os.getenv('SMTP_SERVER') or ''
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER') or ''
    smtp_pass = os.getenv('SMTP_PASS') or ''
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
            <button class="btn btn-warning btn-sm" onclick="editarTarefa(this)"><i class="fas fa-edit"></i></button>
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
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ""
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

# Teste de conexão SMTP ao iniciar o Flask
try:
    smtp_server = os.getenv('SMTP_SERVER') or ''
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER') or ''
    smtp_pass = os.getenv('SMTP_PASS') or ''
    if all([smtp_server, smtp_port, smtp_user, smtp_pass]):
        import smtplib
        server = smtplib.SMTP(str(smtp_server), int(smtp_port), timeout=10)
        server.starttls()
        server.login(str(smtp_user), str(smtp_pass))
        server.quit()
        print(f"[OK] Conexão SMTP bem-sucedida com {smtp_server}:{smtp_port} usando {smtp_user}")
    else:
        print("[AVISO] Variáveis SMTP não estão totalmente configuradas no .env. Teste de conexão não realizado.")
except Exception as e:
    print(f"[ERRO] Falha ao conectar ao servidor SMTP: {e}")

# --- NOTIFICAÇÕES INTERNAS ---

@app.route('/notificacoes', methods=['POST'])
@login_required
def criar_notificacao():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    mensagem = data.get('mensagem')
    tipo = data.get('tipo')
    if not usuario_id or not mensagem:
        return jsonify({'erro': 'usuario_id e mensagem são obrigatórios.'}), 400
    try:
        resp = supabase.table('notificacoes').insert({
            'usuario_id': usuario_id,
            'mensagem': mensagem,
            'tipo': tipo
        }).execute()
        if hasattr(resp, 'data') and resp.data:
            return jsonify({'sucesso': True, 'notificacao': resp.data[0]}), 201
        else:
            return jsonify({'erro': 'Erro ao criar notificação.'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/notificacoes/<usuario_id>', methods=['GET'])
@login_required
def listar_notificacoes(usuario_id):
    try:
        resp = supabase.table('notificacoes').select('*').eq('usuario_id', usuario_id).order('data_criacao', desc=True).execute()
        notificacoes = resp.data if hasattr(resp, 'data') else []
        return jsonify({'notificacoes': notificacoes})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/notificacoes/<notificacao_id>/ler', methods=['PATCH'])
@login_required
def marcar_notificacao_lida(notificacao_id):
    try:
        resp = supabase.table('notificacoes').update({'lida': True}).eq('id', notificacao_id).execute()
        if hasattr(resp, 'data') and resp.data:
            return jsonify({'sucesso': True, 'notificacao': resp.data[0]})
        else:
            return jsonify({'erro': 'Notificação não encontrada.'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/notificacoes/<usuario_id>/limpar', methods=['DELETE'])
@login_required
def limpar_notificacoes(usuario_id):
    try:
        resp = supabase.table('notificacoes').delete().eq('usuario_id', usuario_id).execute()
        if hasattr(resp, 'data'):
            return jsonify({'sucesso': True, 'removidas': len(resp.data)})
        else:
            return jsonify({'sucesso': True, 'removidas': 0})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
