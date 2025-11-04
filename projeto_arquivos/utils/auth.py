from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
import os
from supabase_client import get_user_by_id
import json

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
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para apenas admin izak
def apenas_admin_izak(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_session():
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
        # 1.1) Se o usuário está logado mas a flag não existe (sessão antiga), buscar no BD e salvar em sessão
        if session.get('user_id'):
            try:
                usuario = get_user_by_id(str(session.get('user_id')))
                if usuario is not None and 'is_admin' in usuario:
                    session['is_admin'] = bool(usuario.get('is_admin', False))
                    return session['is_admin']
            except Exception:
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