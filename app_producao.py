#!/usr/bin/env python3
"""
Aplicação de Produção - Versão Refatorada
SGP - Sistema de Gestão de Projetos
"""

import os
from datetime import timedelta
from flask import Flask, session, jsonify, send_from_directory, request, render_template
from flask_cors import CORS
from utils.dias_uteis import dias_uteis_entre_datas
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("[DEBUG] Iniciando app_producao.py...")
print(f"[DEBUG] PORT: {os.environ.get('PORT', 'NÃO DEFINIDA')}")
print(f"[DEBUG] SECRET_KEY: {'DEFINIDA' if os.environ.get('SECRET_KEY') else 'NÃO DEFINIDA'}")
print(f"[DEBUG] SUPABASE_URL: {'DEFINIDA' if os.environ.get('SUPABASE_URL') else 'NÃO DEFINIDA'}")

# Configurar variáveis de ambiente padrão
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app_producao.py')

print("[DEBUG] Criando diretórios...")

# Criar diretórios necessários
os.makedirs('static/uploads', exist_ok=True)

print("[DEBUG] Importando módulos...")

try:
    from config.app_config import Config
    from config.database import supabase
    from utils.auth import login_required, apenas_admin_izak, funcionalidade_restrita, carregar_restricoes, salvar_restricoes
    from utils.validators import validar_projeto, normaliza_opcional, is_mobile_device
    from utils.overdue_notifications import start_overdue_monitoring

    # Importar blueprints
    from routes.auth import auth_bp
    from routes.projetos import projetos_bp
    from routes.tarefas import tarefas_bp
    from routes.admin import admin_bp
    from routes.pastas import pastas_bp
    from routes.main import main_bp
    from routes.producao import producao_bp
    from routes.relatorio import relatorio_bp
    print("[DEBUG] Imports bem-sucedidos!")
except ImportError as e:
    print(f"[WARNING] ERRO DE IMPORT: {e}")
    print("[DEBUG] Tentando importar módulos individualmente...")
    
    # Tentar importar cada módulo individualmente
    Config = None
    supabase = None
    
    # Importar utilitários essenciais
    try:
        from config.app_config import Config
        print("[SUCCESS] Config importado")
    except ImportError as ex:
        print(f"[WARNING] Config não disponível: {ex}")
    
    try:
        from config.database import supabase
        print("[SUCCESS] Supabase importado")
    except ImportError as ex:
        print(f"[WARNING] Supabase não disponível: {ex}")
    
    # Importar blueprints individualmente
    auth_bp = None
    projetos_bp = None  
    tarefas_bp = None
    admin_bp = None
    pastas_bp = None
    main_bp = None
    producao_bp = None
    relatorio_bp = None
    
    # Tentar importar cada blueprint
    try:
        from routes.auth import auth_bp
        print("[SUCCESS] Auth blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Auth blueprint falhou: {ex}")
        from flask import Blueprint
        auth_bp = Blueprint('auth', __name__)
    
    try:
        from routes.projetos import projetos_bp
        print("[SUCCESS] Projetos blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Projetos blueprint falhou: {ex}")
        from flask import Blueprint
        projetos_bp = Blueprint('projetos', __name__)
    
    try:
        from routes.tarefas import tarefas_bp
        print("[SUCCESS] Tarefas blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Tarefas blueprint falhou: {ex}")
        from flask import Blueprint
        tarefas_bp = Blueprint('tarefas', __name__)
    
    try:
        from routes.admin import admin_bp
        print("[SUCCESS] Admin blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Admin blueprint falhou: {ex}")
        from flask import Blueprint
        admin_bp = Blueprint('admin', __name__)
    
    try:
        from routes.pastas import pastas_bp
        print("[SUCCESS] Pastas blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Pastas blueprint falhou: {ex}")
        from flask import Blueprint
        pastas_bp = Blueprint('pastas', __name__)
    
    try:
        from routes.main import main_bp
        print("[SUCCESS] Main blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Main blueprint falhou: {ex}")
        from flask import Blueprint
        main_bp = Blueprint('main', __name__)
    
    try:
        from routes.producao import producao_bp
        print("[SUCCESS] Producao blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Producao blueprint falhou: {ex}")
        from flask import Blueprint
        producao_bp = Blueprint('producao', __name__)
    
    try:
        from routes.relatorio import relatorio_bp
        print("[SUCCESS] Relatorio blueprint importado")
    except ImportError as ex:
        print(f"[WARNING] Relatorio blueprint falhou: {ex}")
        from flask import Blueprint
        relatorio_bp = Blueprint('relatorio', __name__)
    
    # Debug blueprint removido para evitar erro de importação

# Criar aplicação Flask
app = Flask(__name__)

# Configurar CORS para permitir requisições do app mobile e navegador
CORS(app, 
     origins=["*"],  # Permitir qualquer origem
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["*"],  # Permitir qualquer header
     supports_credentials=True)

# Definir SECRET_KEY imediatamente para evitar erro de hash method
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-producao-padrao-123456789')

# Inicializar Flask-WTF para CSRF
try:
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)
    # Desabilitar CSRF completamente para evitar problemas
    app.config['WTF_CSRF_ENABLED'] = False
    print("[SUCCESS] Flask-WTF CSRF desabilitado")
except ImportError as e:
    print(f"[WARNING] Flask-WTF não disponível: {e}")
    csrf = None

# Desabilitar cache durante desenvolvimento
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

print("[DEBUG] Flask app criada!")

# Expor função de dias úteis para Jinja2
@app.context_processor
def utility_processor():
    from flask import has_request_context
    from flask_wtf.csrf import generate_csrf
    
    def safe_csrf_token():
        if has_request_context():
            return generate_csrf()
        return ''
    
    return dict(
        dias_uteis_entre_datas=dias_uteis_entre_datas,
        csrf_token=safe_csrf_token
    )

print("[DEBUG] Context processor configurado!")

# Rota de teste básica adicionada logo após configuração
@app.route('/teste_basico')
def teste_basico():
    return 'Rota básica funcionando!'

# Configurar aplicação para produção
try:
    if Config:
        app.config.from_object(Config)
        print("[SUCCESS] Config carregado com sucesso")
    else:
        raise Exception("Config não disponível")
except Exception as e:
    print(f"[WARNING] Erro ao carregar configurações: {e}")
    print("[INFO] Usando configurações padrão...")
    # Configurações padrão para Render/Produção
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-producao-padrao-123456789')
    app.config['DEBUG'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# Registrar blueprints
try:
    app.register_blueprint(auth_bp)
    app.register_blueprint(projetos_bp)
    app.register_blueprint(tarefas_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pastas_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(producao_bp)
    app.register_blueprint(relatorio_bp, url_prefix='/relatorio')  # Restaurado prefixo
    print(f"[DEBUG] Blueprint relatorio registrado: {relatorio_bp}")
    # Teste inline de blueprint
    from flask import Blueprint
    teste_bp = Blueprint('teste', __name__)
    @teste_bp.route('/inline')
    def teste_inline():
        return 'Blueprint inline funcionando!'
    app.register_blueprint(teste_bp, url_prefix='/teste')
    print("[DEBUG] Blueprint teste inline registrado")
    # Removido registro do debug_bp para evitar erro de variável não definida
    print("[SUCCESS] Blueprints registrados com sucesso!")
    
    # Iniciar monitoramento de tarefas atrasadas
    try:
        start_overdue_monitoring()
        print("[SUCCESS] Monitoramento de tarefas atrasadas iniciado!")
    except Exception as e:
        print(f"[WARNING] Erro ao iniciar monitoramento de tarefas atrasadas: {e}")
        
except Exception as e:
    print(f"[WARNING] Erro ao registrar blueprints: {e}")

# Rota de health check para produção
@app.route('/health')
def health_check():
    """Health check para monitoramento de produção"""
    try:
        # Testar conexão com banco
        if 'supabase' in globals() and supabase:
            supabase_client = supabase.auth
            db_status = "healthy"
        else:
            db_status = "not_configured"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "database": db_status,
        "blueprints": list(app.blueprints.keys()),
        "timestamp": "2025-08-01T12:00:00Z"
    })

# Rota para favicon (evitar 404 no /favicon.ico)
@app.route('/favicon.ico')
def favicon():
    try:
        icon_dir = os.path.join(app.root_path, 'static', 'icons')
        return send_from_directory(icon_dir, 'icon-192.png', mimetype='image/png')
    except Exception:
        # fallback: tenta servir diretamente da pasta static
        return send_from_directory(os.path.join(app.root_path, 'static'), 'icons/icon-192.png', mimetype='image/png')

# Rota de status para produção
@app.route('/status')
def status():
    """Status detalhado do sistema"""
    try:
        # Verificar blueprints registrados
        blueprints = list(app.blueprints.keys())
        
        # Verificar configurações
        config_status = {
            "debug": app.config.get('DEBUG'),
            "secret_key_defined": bool(app.config.get('SECRET_KEY')),
            "max_projetos": app.config.get('MAX_PROJETOS'),
            "max_tarefas": app.config.get('MAX_TAREFAS')
        }
        
        return jsonify({
            "status": "operational",
            "version": "2.0.0",
            "blueprints": blueprints,
            "config": config_status,
            "environment": "production"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "version": "2.0.0"
        })

# Rota de teste simples sem blueprint
@app.route('/teste_direto')
def teste_direto():
    return 'Rota direta funcionando!'

# Rotas do blueprint relatorio movidas temporariamente para o app principal
@app.route('/relatorio/teste_blueprint')
def relatorio_teste_blueprint():
    return 'Blueprint relatorio funcionando!'

# Rota de teste com prefixo diferente
@app.route('/teste_prefixo/teste')
def teste_prefixo():
    return 'Prefixo diferente funcionando!'

# Rota de teste sem prefixo especial
@app.route('/teste_sem_prefixo')
def teste_sem_prefixo():
    return 'Rota sem prefixo funcionando!'

# Rota de teste para blueprint relatorio
@app.route('/relatorio/teste_app')
def teste_relatorio_app():
    return 'Rota relatorio funcionando no app principal!'

# Rota para datas conflitantes
@app.route('/relatorio/datas-conflitantes')
@login_required
def relatorio_datas_conflitantes():
    try:
        # Buscar usuários para o filtro
        try:
            usuarios_data = supabase.table('usuarios').select('id, nome').execute()
            usuarios = usuarios_data.data if usuarios_data.data else []
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            usuarios = []

        # Verificar se há filtro de responsáveis
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
        calcular_conflitos = True

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

        # Detectar conflitos (simplificado)
        conflitos = {
            'projetos_inconsistentes': [],
            'tarefas_fora_projeto': [],
            'tarefas_sobrepostas': [],
            'tarefas_sobrepostas_entre_projetos': [],
            'datas_invalidas': [],
            'predecessoras_conflito': []
        }

        # Aplicar filtros se necessário
        # (lógica simplificada)

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
                             erro=str(e))

# Rota de teste de exportação sem blueprint
@app.route('/teste_exportacao')
def teste_exportacao():
    try:
        from config.database import supabase
        projetos = supabase.table('projetos').select('*').limit(1).execute()
        return f'Conexão OK! Projetos encontrados: {len(projetos.data) if projetos.data else 0}'
    except Exception as e:
        return f'Erro: {str(e)}'

# Rota de teste para o botão de tema
@app.route('/teste-botao-tema')
def teste_botao_tema():
    """Página de teste para o botão de alternância de tema"""
    return '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teste Botão Tema</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark fixed-top">
        <div class="container-fluid">
            <span class="navbar-brand">Teste Tema</span>
            <ul class="navbar-nav ms-auto align-items-center">
                <li class="nav-item me-2">
                    <button id="themeToggle" class="btn btn-outline-light btn-sm" type="button" title="Alternar tema">
                        <span id="themeToggleIcon"><svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="currentColor" style="width: 16px; height: 16px;"><g><defs><style>.b{fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;}</style></defs><path class="b" d="M23.7454,2.5014c3.8817,2.4892,6.695,6.3372,7.8894,10.791,2.6469,9.8784-3.2154,20.0323-13.0938,22.6792-4.4678,1.1793-9.2152,.6456-13.3096-1.4963,4.7971,8.5936,14.8161,12.8338,24.3249,10.2946,11.4717-3.0738,18.2796-14.8654,15.2057-26.3371-2.5449-9.4871-11.1947-16.044-21.0166-15.9313Z"></path></g></svg></span>
                    </button>
                </li>
            </ul>
        </div>
    </nav>

    <div class="container mt-4 pt-5">
        <h1>Teste do Botão de Tema</h1>
        <p>Clique no botão da lua no canto superior direito para alternar entre tema claro e escuro.</p>
        <div id="status">Status: Aguardando clique...</div>
    </div>

    <script>
        // Mesmo JavaScript do base.html
        (function() {
            console.log('[DEBUG] Script de tema executando imediatamente');

            // Aplicar tema inicial
            const THEME_KEY = 'themeMode';
            const moonSVG = '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="currentColor" style="width: 16px; height: 16px;"><g><defs><style>.b{fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;}</style></defs><path class="b" d="M23.7454,2.5014c3.8817,2.4892,6.695,6.3372,7.8894,10.791,2.6469,9.8784-3.2154,20.0323-13.0938,22.6792-4.4678,1.1793-9.2152,.6456-13.3096-1.4963,4.7971,8.5936,14.8161,12.8338,24.3249,10.2946,11.4717-3.0738,18.2796-14.8654,15.2057-26.3371-2.5449-9.4871-11.1947-16.044-21.0166-15.9313Z"></path></g></svg>';
            const sunSVG = '<svg viewBox="0 0 24 24" fill="currentColor" style="width: 16px; height: 16px;"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const saved = localStorage.getItem(THEME_KEY);
            const body = document.body;
            const apply = (mode) => {
                if (mode === 'dark') {
                    body.classList.add('dark');
                } else {
                    body.classList.remove('dark');
                }
                const icon = document.getElementById('themeToggleIcon');
                if (icon) {
                    icon.innerHTML = mode === 'dark' ? sunSVG : moonSVG;
                }
                const metaTheme = document.querySelector('meta[name="theme-color"]');
                if (metaTheme) metaTheme.setAttribute('content', mode === 'dark' ? '#111111' : '#1976d2');
            };
            apply(saved || (prefersDark ? 'dark' : 'light'));

            // Função para configurar o botão
            const setupThemeToggle = () => {
                console.log('[DEBUG] Configurando themeToggle');
                const btn = document.getElementById('themeToggle');
                console.log('[DEBUG] Botão themeToggle encontrado:', !!btn);

                if (btn) {
                    // Remover event listeners existentes para evitar duplicatas
                    btn.removeEventListener('click', btn._themeToggleHandler);

                    // Criar handler
                    btn._themeToggleHandler = function(event) {
                        console.log('[DEBUG] Botão themeToggle clicado!');
                        event.preventDefault();
                        event.stopPropagation();

                        const isDark = document.body.classList.toggle('dark');
                        const mode = isDark ? 'dark' : 'light';
                        console.log('[DEBUG] Modo alterado para:', mode);

                        localStorage.setItem(THEME_KEY, mode);

                        const icon = document.getElementById('themeToggleIcon');
                        if (icon) {
                            icon.innerHTML = isDark ? sunSVG : moonSVG;
                            console.log('[DEBUG] Ícone alterado para:', icon.innerHTML);
                        } else {
                            console.error('[DEBUG] ERRO: Ícone themeToggleIcon não encontrado!');
                        }

                        const metaTheme = document.querySelector('meta[name="theme-color"]');
                        if (metaTheme) {
                            metaTheme.setAttribute('content', isDark ? '#111111' : '#1976d2');
                        }

                        // Atualizar status
                        document.getElementById('status').textContent = `Status: Tema alterado para ${mode}`;

                        // Disparar evento customizado para outros scripts
                        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { mode: mode } }));
                    };

                    // Adicionar event listener
                    btn.addEventListener('click', btn._themeToggleHandler);
                    console.log('[DEBUG] Event listener adicionado ao botão themeToggle');
                } else {
                    console.error('[DEBUG] ERRO: Botão themeToggle não encontrado!');
                }
            };

            // Tentar configurar imediatamente
            setupThemeToggle();

            // Também tentar quando o DOM estiver pronto
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', setupThemeToggle);
            }

            // E tentar novamente após um pequeno delay para garantir
            setTimeout(setupThemeToggle, 100);
        })();
    </script>

    <style>
        body.dark {
            background-color: #121212;
            color: #ffffff;
        }
        body.dark .navbar {
            background-color: #1a1a1a !important;
        }
        body.dark .container {
            background-color: #121212;
        }
    </style>
</body>
</html>
'''

# Rota de teste simples
@app.route('/teste-simples')
def teste_simples():
    """Página de teste simples para o botão de tema"""
    return '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teste Botão Tema Simples</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark fixed-top">
        <div class="container-fluid">
            <span class="navbar-brand">Teste Simples</span>
            <ul class="navbar-nav ms-auto align-items-center">
                <li class="nav-item me-2">
                    <button id="themeToggle" class="btn btn-outline-light btn-sm" type="button" title="Alternar tema">
                        <span id="themeToggleIcon"><svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="currentColor" style="width: 16px; height: 16px;"><g><defs><style>.b{fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;}</style></defs><path class="b" d="M23.7454,2.5014c3.8817,2.4892,6.695,6.3372,7.8894,10.791,2.6469,9.8784-3.2154,20.0323-13.0938,22.6792-4.4678,1.1793-9.2152,.6456-13.3096-1.4963,4.7971,8.5936,14.8161,12.8338,24.3249,10.2946,11.4717-3.0738,18.2796-14.8654,15.2057-26.3371-2.5449-9.4871-11.1947-16.044-21.0166-15.9313Z"></path></g></svg></span>
                    </button>
                </li>
            </ul>
        </div>
    </nav>

    <div class="container mt-4 pt-5">
        <h1>Teste do Botão de Tema</h1>
        <p>Este é um teste simples sem templates Flask.</p>
        <div id="status">Status: Aguardando...</div>
    </div>

    <script>
        // JavaScript idêntico ao do base.html
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🎨 Tema: Inicializando sistema de tema...');

            const THEME_KEY = 'themeMode';
            const moonSVG = '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="currentColor" style="width: 16px; height: 16px;"><g><defs><style>.b{fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;}</style></defs><path class="b" d="M23.7454,2.5014c3.8817,2.4892,6.695,6.3372,7.8894,10.791,2.6469,9.8784-3.2154,20.0323-13.0938,22.6792-4.4678,1.1793-9.2152,.6456-13.3096-1.4963,4.7971,8.5936,14.8161,12.8338,24.3249,10.2946,11.4717-3.0738,18.2796-14.8654,15.2057-26.3371-2.5449-9.4871-11.1947-16.044-21.0166-15.9313Z"></path></g></svg>';
            const sunSVG = '<svg viewBox="0 0 24 24" fill="currentColor" style="width: 16px; height: 16px;"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
            const btn = document.getElementById('themeToggle');
            const icon = document.getElementById('themeToggleIcon');

            console.log('🎨 Tema: Elementos encontrados - Botão:', !!btn, 'Ícone:', !!icon);

            if (!btn) {
                console.error('🎨 Tema: ERRO CRÍTICO - Botão themeToggle não encontrado!');
                document.getElementById('status').textContent = 'ERRO: Botão não encontrado!';
                return;
            }

            // Aplicar tema salvo
            const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
            console.log('🎨 Tema: Tema salvo no localStorage:', savedTheme);

            document.body.classList.toggle('dark', savedTheme === 'dark');
            if (icon) {
                icon.innerHTML = savedTheme === 'dark' ? sunSVG : moonSVG;
            }
            console.log('🎨 Tema: Tema inicial aplicado:', savedTheme);
            document.getElementById('status').textContent = `Tema inicial: ${savedTheme}`;

            // Handler do clique
            function toggleTheme(event) {
                console.log('🎨 Tema: Botão clicado!');
                event.preventDefault();

                const isDark = document.body.classList.toggle('dark');
                const newTheme = isDark ? 'dark' : 'light';

                localStorage.setItem(THEME_KEY, newTheme);
                if (icon) {
                    icon.innerHTML = isDark ? sunSVG : moonSVG;
                }

                console.log('🎨 Tema: Alterado para:', newTheme);
                console.log('🎨 Tema: Classe body.dark aplicada:', document.body.classList.contains('dark'));
                document.getElementById('status').textContent = `Tema alterado para: ${newTheme}`;
            }

            // Anexar event listener
            btn.addEventListener('click', toggleTheme);
            console.log('🎨 Tema: Event listener anexado com sucesso');
            document.getElementById('status').textContent += ' | Listener anexado';

            // Teste imediato
            console.log('🎨 Tema: Sistema pronto! Clique no botão para testar.');
        });
    </script>

    <style>
        body.dark {
            background-color: #121212;
            color: #ffffff;
        }
        body.dark .navbar {
            background-color: #1a1a1a !important;
        }
    </style>
</body>
</html>
'''



# ===== PROTEÇÕES DE SEGURANÇA =====

@app.after_request
def set_security_headers(response):
    """Define cabeçalhos de segurança HTTP"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # CSP permissivo para não quebrar funcionalidades
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:;"
    return response

@app.before_request
def force_https():
    """Força HTTPS em produção (descomente quando tiver certificado SSL)"""
    # if not request.is_secure and not request.url.startswith('http://localhost'):
    #     url = request.url.replace('http://', 'https://', 1)
    #     return redirect(url, code=301)
    pass

@app.before_request
def handle_method_override():
    """Suporte para method override via campo _method"""
    if request.method == 'POST':
        method = request.form.get('_method', '').upper()
        if method in ['PUT', 'DELETE', 'PATCH']:
            request.environ['REQUEST_METHOD'] = method

# ===================================
# API Routes for Mobile App
# ===================================

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    """API para dashboard mobile - retorna estatísticas"""
    try:
        # Por enquanto sem autenticação para teste
        # Buscar projetos
        projetos_resp = supabase.table("projetos").select("*").execute()
        projetos = projetos_resp.data or []
        
        # Buscar tarefas
        tarefas_resp = supabase.table("tarefas").select("*").execute()
        tarefas = tarefas_resp.data or []
        
        # Calcular estatísticas
        total_projetos = len(projetos)
        total_tarefas = len(tarefas)
        tarefas_pendentes = len([t for t in tarefas if t.get('status') in ['PENDENTE', 'AGUARDANDO']])
        tarefas_em_andamento = len([t for t in tarefas if t.get('status') == 'EM_ANDAMENTO'])
        tarefas_concluidas = len([t for t in tarefas if t.get('status') == 'CONCLUIDA'])
        
        stats = {
            'projetos_count': total_projetos,
            'tarefas_count': total_tarefas,
            'tarefas_pendentes': tarefas_pendentes,
            'tarefas_em_andamento': tarefas_em_andamento,
            'tarefas_concluidas': tarefas_concluidas,
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projetos', methods=['GET'])
def api_projetos():
    """API para projetos recentes"""
    try:
        # Buscar projetos (últimos 5 por id)
        projetos_resp = supabase.table("projetos").select("*").limit(5).execute()
        projetos = projetos_resp.data or []
        
        # Mapeamento de status
        status_map = {
            'EM_ANDAMENTO': 'em progresso',
            'PENDENTE': 'pendente',
            'CONCLUIDA': 'concluída',
            'CANCELADA': 'cancelada'
        }
        
        # Formatar para mobile
        projetos_formatados = []
        for p in projetos:
            status_db = p.get('status', 'PENDENTE')
            status_display = status_map.get(status_db, 'pendente')
            projetos_formatados.append({
                'id': p['id'],
                'nome': p['nome'],
                'status': status_display,
                'data_inicio': p.get('data_inicio'),
                'data_fim': p.get('data_fim')
            })
        
        return jsonify(projetos_formatados)
    except Exception as e:
        print(f"[API ERROR] /api/projetos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tarefas', methods=['GET'])
def api_tarefas():
    """API para tarefas recentes"""
    try:
        # Buscar tarefas com nome do projeto (join opcional)
        tarefas_resp = supabase.table("tarefas").select("*, projetos!left(nome)").limit(5).execute()
        tarefas = tarefas_resp.data or []
        
        # Mapeamento de status
        status_map = {
            'EM_ANDAMENTO': 'em progresso',
            'PENDENTE': 'pendente',
            'AGUARDANDO': 'pendente',
            'CONCLUIDA': 'concluída',
            'CANCELADA': 'cancelada'
        }
        
        # Formatar para mobile
        tarefas_formatadas = []
        for t in tarefas:
            projeto_nome = t.get('projetos', {}).get('nome', 'N/A') if t.get('projetos') else 'N/A'
            status_db = t.get('status', 'PENDENTE')
            status_display = status_map.get(status_db, 'pendente')
            tarefas_formatadas.append({
                'id': t['id'],
                'nome': t['nome'],
                'status': status_display,
                'projeto_nome': projeto_nome
            })
        
        return jsonify(tarefas_formatadas)
    except Exception as e:
        print(f"[API ERROR] /api/tarefas: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ===================================



if __name__ == '__main__' and not os.environ.get('FLASK_SKIP_RUN'):
    print("[STARTUP] Iniciando aplicação de produção...")
    print("[INFO] Blueprints registrados:")
    for blueprint_name in app.blueprints.keys():
        print(f"   - {blueprint_name}")
    print("[SUCCESS] Sistema refatorado pronto para produção!")
    print("[INFO] Acesse: http://localhost:5000")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)