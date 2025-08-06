"""
Rotas de autenticação
=====================
"""

from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import validar_login, criar_sessao_usuario, limpar_sessao
from app.utils.validators import validar_email, validar_senha
from app.utils.restricoes import adicionar_restricoes_padrao
from supabase_client import get_user_by_email, create_user

bp = Blueprint('auth', __name__)

@bp.route('/')
def index():
    """Rota principal - redireciona para dashboard"""
    return redirect('/dashboard')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
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

        # Validação de entrada
        erro_email = validar_email(email)
        if erro_email:
            flash(erro_email)
            return render_template('login.html')
        
        erro_senha = validar_senha(senha)
        if erro_senha:
            flash(erro_senha)
            return render_template('login.html')

        # Validar credenciais
        user = validar_login(email, senha)
        if user:
            criar_sessao_usuario(user)
            # Se quiser implementar o "lembrar-me", pode usar cookies aqui
            return redirect('/dashboard')
        else:
            flash('E-mail ou senha inválidos.')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Rota de logout"""
    limpar_sessao()
    return redirect(url_for('auth.login'))

@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Rota de cadastro de usuários"""
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email'].strip().lower()
        senha = request.form['senha']
        
        # Validações
        erro_email = validar_email(email)
        if erro_email:
            flash(erro_email)
            return render_template('cadastro.html')
        
        erro_senha = validar_senha(senha)
        if erro_senha:
            flash(erro_senha)
            return render_template('cadastro.html')
        
        # Verificar se email já existe
        if get_user_by_email(email):
            flash('E-mail já cadastrado.')
            return render_template('cadastro.html')
        
        # Criar usuário
        senha_hash = generate_password_hash(senha)
        sucesso = create_user(nome, email, senha_hash)
        
        if sucesso:
            # Adicionar restrições padrão para o novo usuário
            novo_usuario = get_user_by_email(email)
            if novo_usuario and 'id' in novo_usuario:
                adicionar_restricoes_padrao(novo_usuario['id'])
            
            flash('Cadastro realizado com sucesso! Faça login.')
            return redirect(url_for('auth.login'))
        else:
            flash("Erro ao cadastrar usuário. Tente novamente mais tarde.")
    
    return render_template('cadastro.html') 