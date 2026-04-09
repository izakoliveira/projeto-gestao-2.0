from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
import os
from supabase_client import get_user_by_id, SUPABASE_URL, SUPABASE_KEY, headers
import json
import requests

RESTRICOES_PATH = 'restricoes.json'

# Função para carregar restrições do banco de dados
def carregar_restricoes():
    """
    Carrega restrições de todos os usuários do banco de dados.
    Retorna um dicionário: {user_id: {restr_criar_projeto: bool, ...}}
    Fallback para arquivo JSON se banco não estiver disponível.
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/usuarios?select=*"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200 and response.json():
            usuarios = response.json()
            restricoes = {}
            campos_restricao = [
                'restr_criar_projeto', 'restr_editar_projeto', 'restr_excluir_projeto',
                'restr_criar_tarefa', 'restr_editar_tarefa', 'restr_excluir_tarefa',
                'restr_editar_responsavel', 'restr_editar_duracao', 'restr_editar_datas',
                'restr_editar_predecessoras', 'restr_editar_nome_tarefa', 'restr_editar_status_tarefa',
                'notificar_projeto', 'email_projeto', 'notificar_tarefa', 'email_tarefa'
            ]
            
            for usuario in usuarios:
                user_id = str(usuario['id'])
                restricoes[user_id] = {}
                
                # Copiar campos de restrição
                for campo in campos_restricao:
                    restricoes[user_id][campo] = usuario.get(campo, False)
                
                # Manter campos de identificação
                restricoes[user_id]['nome'] = usuario.get('nome')
                restricoes[user_id]['email'] = usuario.get('email')
            
            return restricoes
    except Exception as e:
        print(f"Erro ao carregar restrições do banco: {e}")
        # Fallback para arquivo local
        try:
            with open(RESTRICOES_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    return {}

# Função para salvar restrições no banco de dados
def salvar_restricoes(restricoes):
    """
    Salva restrições no banco de dados.
    Recebe dicionário: {user_id: {restr_criar_projeto: bool, ...}}
    Também salva no arquivo JSON como backup.
    """
    try:
        sucesso_total = 0
        erro_total = 0
        
        for user_id, dados in restricoes.items():
            # Preparar dados de restrição (apenas campos booleanos)
            campos_restricao = [
                'restr_criar_projeto', 'restr_editar_projeto', 'restr_excluir_projeto',
                'restr_criar_tarefa', 'restr_editar_tarefa', 'restr_excluir_tarefa',
                'restr_editar_responsavel', 'restr_editar_duracao', 'restr_editar_datas',
                'restr_editar_predecessoras', 'restr_editar_nome_tarefa', 'restr_editar_status_tarefa',
                'notificar_projeto', 'email_projeto', 'notificar_tarefa', 'email_tarefa'
            ]
            
            dados_update = {}
            for campo in campos_restricao:
                if campo in dados:
                    dados_update[campo] = bool(dados[campo])
            
            # Atualizar no banco
            if dados_update:
                try:
                    url = f"{SUPABASE_URL}/rest/v1/usuarios?id=eq.{user_id}"
                    response = requests.patch(url, json=dados_update, headers=headers)
                    
                    if response.status_code in [200, 204]:
                        print(f"✓ Restrições salvas para usuário {user_id}")
                        sucesso_total += 1
                    else:
                        print(f"✗ Erro ao salvar restrições para {user_id}: {response.status_code} - {response.text}")
                        erro_total += 1
                except Exception as e:
                    print(f"✗ Exceção ao salvar restrições para {user_id}: {e}")
                    erro_total += 1
        
        print(f"[INFO] Salvamento concluído: {sucesso_total} sucessos, {erro_total} erros")
        
        # Backup em arquivo JSON
        with open(RESTRICOES_PATH, 'w') as f:
            json.dump(restricoes, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Erro ao salvar restrições: {e}")
        # Fallback para salvar apenas no arquivo
        try:
            with open(RESTRICOES_PATH, 'w') as f:
                json.dump(restricoes, f, indent=2)
            return True
        except Exception:
            return False

# Função para checar se uma funcionalidade está restrita para o usuário atual
def funcionalidade_restrita(nome_restricao):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('user_email') == 'izak.gomes59@gmail.com':
                return f(*args, **kwargs)
            restricoes = carregar_restricoes()
            usuario_id = session.get('user_id')
            restricoes_usuario = restricoes.get(str(usuario_id), {}) if usuario_id else {}
            if restricoes_usuario.get(f'restr_{nome_restricao}', False):
                flash('Acesso restrito para esta funcionalidade.')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorador para login obrigatório
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Verificar se é uma requisição AJAX/API
            if request.is_json or request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Usuario nao autenticado'}), 401
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para apenas admin izak
def apenas_admin_izak(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_session():
            # Verificar se é uma requisição AJAX
            from flask import request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'}), 403
            
            flash('Acesso negado. Apenas administradores podem acessar esta página.')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function 

# Helper: verifica se o usuário atual é admin baseado em variáveis de ambiente
def is_admin_session():
    try:
        # 1) Preferir flag vinda da sessão (carregada do BD no login). Se existir, respeitar True ou False.
        if 'is_admin' in session:
            return bool(session.get('is_admin'))
        
        # 1.1) Se o usuário está logado mas a flag não existe (sessão antiga), buscar na tabela usuarios_admin
        if session.get('user_id'):
            try:
                print(f"[DEBUG] Verificando admin para user_id: {session.get('user_id')}")
                # Usar requests diretamente como no resto do código
                from supabase_client import SUPABASE_URL, SUPABASE_KEY, headers
                url = f"{SUPABASE_URL}/rest/v1/usuarios_admin?select=*&usuario_id=eq.{session.get('user_id')}&ativo=eq.true"
                resp = requests.get(url, headers=headers)
                print(f"[DEBUG] Admin check status: {resp.status_code}")
                
                if resp.status_code == 200:
                    admin_data = resp.json()
                    print(f"[DEBUG] Admin check result: {admin_data}")
                    
                    if admin_data and len(admin_data) > 0:
                        session['is_admin'] = True
                        session['admin_nivel'] = admin_data[0].get('nivel_acesso', 'admin')
                        print(f"[DEBUG] Admin encontrado: {admin_data[0]}")
                        return True
                    else:
                        session['is_admin'] = False
                        print("[DEBUG] Admin não encontrado")
                        return False
                else:
                    print(f"[DEBUG] Erro na query: {resp.text}")
                    session['is_admin'] = False
                    return False
            except Exception as e:
                print(f"[DEBUG] Erro ao verificar admin: {e}")
                pass
        
        # 2) Fallback por variáveis de ambiente (emergencial)
        admin_email = os.getenv('ADMIN_EMAIL', 'izak.gomes59@gmail.com')
        admin_user_id = os.getenv('ADMIN_USER_ID', 'd0d784bd-f2bb-44b2-8096-5c10ec4d57be')
        if session.get('user_email') == admin_email:
            return True
        if session.get('user_id') and str(session.get('user_id')) == str(admin_user_id):
            return True
        return False
    except Exception:
        return False


def get_admin_nivel():
    """Retorna o nível de acesso do admin atual (admin, super_admin, master) ou None se não for admin"""
    try:
        if is_admin_session():
            # Se já está em sessão
            if 'admin_nivel' in session:
                return session.get('admin_nivel')
            
            # Buscar no banco
            if session.get('user_id'):
                from supabase_client import SUPABASE_URL, SUPABASE_KEY, headers
                import requests
                url = f"{SUPABASE_URL}/rest/v1/usuarios_admin?select=nivel_acesso&usuario_id=eq.{session.get('user_id')}&ativo=eq.true"
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200:
                    admin_data = resp.json()
                    if admin_data and len(admin_data) > 0:
                        nivel = admin_data[0].get('nivel_acesso', 'admin')
                        session['admin_nivel'] = nivel
                        return nivel
            
            # Fallback: se é admin mas não tem registro na tabela usuarios_admin, considerar admin básico
            return 'admin'
        return None
    except Exception:
        return None


def is_super_admin():
    """Verifica se o usuário é super_admin ou master"""
    nivel = get_admin_nivel()
    return nivel in ['super_admin', 'master']


def is_master_admin():
    """Verifica se o usuário é master"""
    nivel = get_admin_nivel()
    return nivel == 'master'
