"""
Utilitários de autenticação e autorização
=========================================
"""

from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
from werkzeug.security import check_password_hash
from app.config.database import get_supabase
from supabase_client import get_user_by_email, create_user, get_all_users

def login_required(f):
    """Decorador para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def apenas_admin_izak(f):
    """Decorador para verificar se o usuário é o admin Izak"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_email') != 'izak.gomes59@gmail.com':
            flash('Acesso negado. Apenas administradores podem acessar esta página.')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def funcionalidade_restrita(nome_restricao):
    """Decorador para verificar restrições de funcionalidade"""
    from app.utils.restricoes import carregar_restricoes
    
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
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validar_login(email, senha):
    """Valida as credenciais do usuário"""
    user = get_user_by_email(email)
    if user and check_password_hash(user['senha_hash'], str(senha) if senha is not None else ""):
        return user
    return None

def criar_sessao_usuario(user):
    """Cria a sessão do usuário"""
    session['user_id'] = user['id']
    session['user_nome'] = user['nome']
    session['user_email'] = user['email']

def limpar_sessao():
    """Limpa a sessão do usuário"""
    session.clear() 