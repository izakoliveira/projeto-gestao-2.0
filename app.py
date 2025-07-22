import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, flash, make_response, url_for, jsonify, render_template_string, abort
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from supabase_client import get_user_by_email, create_user, get_all_users, get_all_projects, get_project_by_id, create_project, update_project, delete_project, get_all_tasks, get_tasks_by_project, create_task, update_task, delete_task
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
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('user_nome') == 'izak.gomes59@gmail.com':
                return f(*args, **kwargs)
            restricoes = carregar_restricoes()
            usuario_id = session.get('user_id')
            restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
            if restricoes_usuario.get(f'restr_{nome_restricao}', False):
                flash('Acesso restrito para esta funcionalidade.')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
    tipo_id = request.args.get('tipo_id', '')

    if session.get('user_email') == 'izak.gomes59@gmail.com':
        projetos = get_all_projects()
    else:
        # Usuário comum vê apenas projetos autorizados
        resp = requests.get(f"{os.getenv('SUPABASE_URL')}/rest/v1/projetos_usuarios_visiveis?usuario_id=eq.{usuario_id}", headers={
            "apikey": os.getenv('SUPABASE_KEY'),
            "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
            "Content-Type": "application/json"
        })
        projetos_ids_visiveis = [r['projeto_id'] for r in resp.json()] if resp.status_code == 200 else []
        if projetos_ids_visiveis:
            projetos = [p for p in get_all_projects() if p['id'] in projetos_ids_visiveis]
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
    # Buscar todas as coleções disponíveis apenas das tarefas filtradas (não do banco inteiro)
            colecoes = sorted(set(
                (str(t.get('colecao', '') or '').strip())
                for t in tarefas_filtradas
                if (str(t.get('colecao', '') or '').strip())
            ))
    # Buscar todos os tipos de projeto para exibir o nome da pasta
    tipos = supabase.table('tipos_projeto').select('id, nome').execute().data or []
    tipos = [t for t in tipos if t['nome'].lower() not in ['calendarios', 'tarefas diarias']]
    tipos_dict = {t['id']: t['nome'] for t in tipos}
    for projeto in projetos:
        projeto['tipo_nome'] = tipos_dict.get(projeto.get('tipo_id'), '-')
    return render_template('projetos_gantt_basico.html', projetos=projetos, gantt_geral_data=gantt_geral_data, projects_colors=cor_projetos, colecoes=colecoes, tipos=tipos)

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
            return render_template('novo_projeto.html')

        try:
            data = {
                "nome": nome,
                "descricao": descricao,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "usuario_id": usuario_id
            }
            sucesso = create_project(data)
            if sucesso:
                flash("Projeto criado com sucesso!")
                return redirect('/projetos')
            else:
                flash(f"Erro ao criar o projeto.")
        except Exception as e:
            flash(f"Erro ao criar o projeto: {str(e)}")
            return render_template('novo_projeto.html')

    return render_template('novo_projeto.html')

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

# Exemplo para editar projeto:
@app.route('/projetos/editar/<uuid:projeto_id>', methods=['GET', 'POST'])
@login_required
@funcionalidade_restrita('editar_projeto')
def editar_projeto(projeto_id):
    tipos = []  # Adapte para buscar tipos se necessário
    usuario_id = session.get('user_id')
    usuario_email = session.get('user_email')
    is_admin = usuario_email == 'izak.gomes59@gmail.com'
    projeto = get_project_by_id(projeto_id)
    if not projeto or (not is_admin and projeto.get('usuario_id') != usuario_id):
        flash('Acesso restrito: apenas o dono do projeto ou admin pode editar.')
        return redirect(url_for('projetos'))
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        tipo_id = request.form.get('tipo_id')
        update_data = {
            "nome": nome,
            "descricao": descricao,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "tipo_id": tipo_id
        }
        update_project(projeto_id, update_data)
        flash("Projeto atualizado com sucesso!")
        voltar_para = request.form.get('voltar_para')
        if voltar_para:
            return redirect(voltar_para)
        return redirect(f'/projetos/{projeto_id}')
    return render_template('editar_projeto.html', projeto=projeto, tipos=tipos)

# Exemplo para excluir projeto:
@app.route('/projetos/excluir/<uuid:projeto_id>', methods=['POST'])
@login_required
def excluir_projeto(projeto_id):
    usuario_id = session.get('user_id')
    usuario_email = session.get('user_email')
    is_admin = usuario_email == 'izak.gomes59@gmail.com'
    projeto = get_project_by_id(projeto_id)
    if not projeto or (not is_admin and projeto.get('usuario_id') != usuario_id):
        flash('Acesso restrito: apenas o dono do projeto ou admin pode excluir.')
        return redirect(url_for('projetos'))
    delete_project(projeto_id)
    flash("Projeto excluído com sucesso!")
    return redirect('/projetos')

# Exemplo para criar tarefa:
@app.route('/tarefas/criar/<uuid:projeto_id>', methods=['GET', 'POST'])
@login_required
def criar_tarefa(projeto_id):
    usuario_id = session.get('user_id')
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        data['projeto_id'] = str(projeto_id)
        sucesso = create_task(data)
        if sucesso:
            flash('Tarefa criada com sucesso!')
            return redirect(f'/projetos/{projeto_id}')
        else:
            flash('Erro ao criar tarefa.')
    # ... buscar dados para o formulário ...
    return render_template('criar_tarefa.html')

# Exemplo para editar tarefa:
@app.route('/tarefas/editar/<uuid:tarefa_id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(tarefa_id):
    tarefa = get_tasks_by_project(tarefa_id)
    if request.method == 'POST':
        data = request.form.to_dict()
        sucesso = update_task(tarefa_id, data)
        if sucesso:
            flash('Tarefa atualizada com sucesso!')
            return redirect(f'/projetos/{tarefa[0]["projeto_id"]}')
        else:
            flash('Erro ao atualizar tarefa.')
    # ... buscar dados para o formulário ...
    return render_template('editar_tarefa.html', tarefa=tarefa)

# Exemplo para excluir tarefa:
@app.route('/tarefas/excluir/<uuid:tarefa_id>', methods=['POST'])
@login_required
def excluir_tarefa(tarefa_id):
    sucesso = delete_task(tarefa_id)
    if sucesso:
        flash('Tarefa excluída com sucesso!')
    else:
        flash('Erro ao excluir tarefa.')
    return redirect(request.referrer or '/projetos')

# Detalhes do projeto
@app.route('/projetos/<uuid:projeto_id>')
@login_required
def detalhes_projeto(projeto_id):
    projeto = get_project_by_id(projeto_id)
    if not projeto:
        flash("Projeto não encontrado.")
        return redirect('/projetos')
    # Buscar as tarefas do projeto
    tarefas = get_tasks_by_project(projeto_id)
    # ... restante da função ...

# ... restante do código permanece igual ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
