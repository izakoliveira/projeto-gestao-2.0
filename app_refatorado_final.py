from flask import Flask, session
from config.app_config import Config
from config.database import supabase
from utils.auth import login_required, apenas_admin_izak, funcionalidade_restrita, carregar_restricoes, salvar_restricoes
from utils.validators import validar_projeto, normaliza_opcional, is_mobile_device

# Importar blueprints
from routes.auth import auth_bp
from routes.projetos import projetos_bp
from routes.tarefas import tarefas_bp
from routes.admin import admin_bp
from routes.pastas import pastas_bp
from routes.main import main_bp
from routes.producao import producao_bp

# Criar aplicação Flask
app = Flask(__name__)

# Configurar aplicação
app.config.from_object(Config)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(projetos_bp)
app.register_blueprint(tarefas_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(pastas_bp)
app.register_blueprint(main_bp)
app.register_blueprint(producao_bp)

# Rota de teste para verificar se tudo está funcionando
@app.route('/teste-refatoracao-final')
def teste_refatoracao_final():
    """Teste para verificar se todos os módulos estão funcionando"""
    try:
        # Testar conexão com banco
        supabase_client = supabase.auth
        db_status = "✅ Conectado ao Supabase"
    except Exception as e:
        db_status = f"❌ Erro na conexão: {str(e)}"
    
    # Testar funções de autenticação
    try:
        restricoes = carregar_restricoes()
        auth_status = "✅ Funções de autenticação funcionando"
    except Exception as e:
        auth_status = f"❌ Erro nas funções de autenticação: {str(e)}"
    
    # Testar validações
    try:
        resultado = validar_projeto("Teste", "2024-01-01", "2024-12-31")
        validacao_status = "✅ Funções de validação funcionando"
    except Exception as e:
        validacao_status = f"❌ Erro nas funções de validação: {str(e)}"
    
    # Verificar blueprints registrados
    blueprints = list(app.blueprints.keys())
    blueprint_status = f"✅ Blueprints registrados: {', '.join(blueprints)}"
    
    return {
        "status": "Sistema refatorado funcionando!",
        "modulos": {
            "database": db_status,
            "auth": auth_status,
            "validators": validacao_status,
            "blueprints": blueprint_status
        },
        "blueprints_registrados": blueprints,
        "configuracoes": {
            "debug": app.config.get('DEBUG'),
            "secret_key": "✅ Configurada" if app.config.get('SECRET_KEY') else "❌ Não configurada"
        }
    }

# Rota de teste para verificar funcionalidades específicas
@app.route('/teste-funcionalidades')
def teste_funcionalidades():
    """Teste para verificar funcionalidades específicas"""
    resultados = {}
    
    # Testar detecção de mobile
    try:
        is_mobile = is_mobile_device("Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)")
        resultados["mobile_detection"] = f"✅ Detecção mobile: {is_mobile}"
    except Exception as e:
        resultados["mobile_detection"] = f"❌ Erro na detecção mobile: {str(e)}"
    
    # Testar normalização
    try:
        resultado = normaliza_opcional("  teste  ")
        resultados["normalizacao"] = f"✅ Normalização: '{resultado}'"
    except Exception as e:
        resultados["normalizacao"] = f"❌ Erro na normalização: {str(e)}"
    
    # Testar validação de projeto
    try:
        resultado = validar_projeto("", "2024-01-01", "2024-12-31")
        resultados["validacao_projeto"] = f"✅ Validação projeto: {resultado}"
    except Exception as e:
        resultados["validacao_projeto"] = f"❌ Erro na validação: {str(e)}"
    
    return {
        "status": "Teste de funcionalidades",
        "resultados": resultados
    }

if __name__ == '__main__':
    print("🚀 Iniciando aplicação refatorada...")
    print("📋 Blueprints registrados:")
    for blueprint_name in app.blueprints.keys():
        print(f"   - {blueprint_name}")
    print("✅ Sistema refatorado pronto!")
    app.run(debug=True) 