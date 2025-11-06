from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from supabase_client import get_user_by_email, create_user
from utils.auth import is_admin_session, login_required
from utils.auth import carregar_restricoes
from config.database import SUPABASE_URL, SUPABASE_KEY
import json
import requests
import bcrypt

RESTRICOES_PATH = 'restricoes.json'

# Headers para requisições Supabase
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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
        
        # Bloquear login de usuários simples (email termina com @sistema.local)
        if user and user['email'].endswith('@sistema.local'):
            flash('Este usuário não tem permissão para fazer login.')
            return render_template('login.html')
        
        if user:
            print('Hash salvo:', user['senha_hash'])
            print('Senha digitada:', senha)
            # Garantir que a senha seja uma string
            senha_str = str(senha) if senha is not None else ""
            print('Verificação:', check_password_hash(user['senha_hash'], senha_str))
        if user and check_password_hash(user['senha_hash'], str(senha) if senha is not None else ""):
            # Configurar sessão como permanente SEMPRE (por padrão) para evitar deslogamentos
            session.permanent = True
            
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            session['user_email'] = user['email']
            # Flag de admin baseada no banco (campo is_admin). Não usar fallback aqui para respeitar o BD.
            session['is_admin'] = bool(user.get('is_admin', False))
            
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

@auth_bp.route('/alterar_senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Rota para usuário alterar sua própria senha"""
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual', '').strip()
        senha_nova = request.form.get('senha_nova', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()
        
        # Validações
        if not senha_atual or not senha_nova or not confirmar_senha:
            flash('Todos os campos são obrigatórios.')
            return render_template('alterar_senha.html')
        
        if senha_nova != confirmar_senha:
            flash('A nova senha e a confirmação não coincidem.')
            return render_template('alterar_senha.html')
        
        if len(senha_nova) < 6:
            flash('A nova senha deve ter no mínimo 6 caracteres.')
            return render_template('alterar_senha.html')
        
        # Verificar senha atual
        usuario_id = session.get('user_id')
        usuario_email = session.get('user_email')
        
        usuario = get_user_by_email(usuario_email)
        if not usuario:
            flash('Erro ao carregar dados do usuário.')
            return render_template('alterar_senha.html')
        
        # Verificar se a senha atual está correta
        if not check_password_hash(usuario['senha_hash'], senha_atual):
            flash('Senha atual incorreta.')
            return render_template('alterar_senha.html')
        
        # Gerar novo hash
        try:
            senha_nova_hash = bcrypt.hashpw(senha_nova.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Atualizar no banco
            url = f"{SUPABASE_URL}/rest/v1/usuarios?id=eq.{usuario_id}"
            dados_update = {
                'senha_hash': senha_nova_hash
            }
            
            response = requests.patch(url, json=dados_update, headers=headers)
            
            if response.status_code in [200, 204]:
                flash('Senha alterada com sucesso!')
                print(f"✓ Senha alterada para usuário {usuario_id}")
                return redirect(url_for('main.dashboard'))
            else:
                flash(f'Erro ao alterar senha: {response.status_code}')
                print(f"✗ Erro ao alterar senha: {response.text}")
        except Exception as e:
            flash(f'Erro ao alterar senha: {str(e)}')
            print(f"Exceção ao alterar senha: {e}")
    
    return render_template('alterar_senha.html')
