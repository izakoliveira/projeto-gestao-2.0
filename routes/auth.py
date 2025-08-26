from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from supabase_client import get_user_by_email, create_user
from utils.auth import is_admin_session
from utils.auth import carregar_restricoes
import json

RESTRICOES_PATH = 'restricoes.json'

# Criar blueprint para autenticação
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
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

        user = get_user_by_email(email)
        print("Usuário retornado:", user)
        if user:
            print('Hash salvo:', user['senha_hash'])
            print('Senha digitada:', senha)
            # Garantir que a senha seja uma string
            senha_str = str(senha) if senha is not None else ""
            print('Verificação:', check_password_hash(user['senha_hash'], senha_str))
        if user and check_password_hash(user['senha_hash'], str(senha) if senha is not None else ""):
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            session['user_email'] = user['email']
            # Flag de admin baseada no banco (campo is_admin). Não usar fallback aqui para respeitar o BD.
            session['is_admin'] = bool(user.get('is_admin', False))
            # Se quiser implementar o "lembrar-me", pode usar cookies aqui
            return redirect('/dashboard')
        else:
            flash('E-mail ou senha inválidos.')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Rota de logout"""
    session.clear()
    return redirect('/login')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Rota de cadastro de usuários"""
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
            # --- NOVO: adicionar restrições padrão para o novo usuário ---
            # Buscar o usuário recém-criado para pegar o id
            novo_usuario = get_user_by_email(email)
            if novo_usuario and 'id' in novo_usuario:
                restricoes = carregar_restricoes()
                restricoes_padrao = {
                    'restr_criar_projeto': False,
                    'restr_editar_projeto': False,
                    'restr_excluir_projeto': False,
                    'restr_criar_tarefa': False,
                    'restr_editar_tarefa': False,
                    'restr_excluir_tarefa': False,
                    'restr_editar_responsavel': False,
                    'restr_editar_duracao': False,
                    'restr_editar_datas': False,
                    'restr_editar_predecessoras': False,
                    'restr_editar_nome_tarefa': False
                }
                restricoes[str(novo_usuario['id'])] = restricoes_padrao
                with open(RESTRICOES_PATH, 'w') as f:
                    json.dump(restricoes, f)
            # --- FIM NOVO ---
            flash('Cadastro realizado com sucesso! Faça login.')
            return redirect(url_for('auth.login'))
        else:
            flash("Erro ao cadastrar usuário. Tente novamente mais tarde.")
    return render_template('cadastro.html') 