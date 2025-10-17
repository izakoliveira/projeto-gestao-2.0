#!/usr/bin/env python3
"""
Diagnóstico Local vs Render
Sistema de Gestão de Projetos v2.0.0
"""

import os
import sys
from datetime import datetime

def diagnostic_check():
    """Diagnóstico completo do ambiente"""
    print("🔍 DIAGNÓSTICO COMPLETO - LOCAL vs RENDER")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Verificar Python
    print("1. 🐍 PYTHON:")
    print(f"   Versão: {sys.version}")
    print(f"   Executável: {sys.executable}")
    print()
    
    # 2. Verificar variáveis de ambiente
    print("2. 🔧 VARIÁVEIS DE AMBIENTE:")
    env_vars = [
        'FLASK_ENV', 'FLASK_APP', 'SECRET_KEY', 
        'SUPABASE_URL', 'SUPABASE_KEY', 'PORT'
    ]
    for var in env_vars:
        value = os.environ.get(var, 'NÃO DEFINIDA')
        masked_value = value[:10] + "..." if len(str(value)) > 10 else value
        print(f"   {var}: {masked_value}")
    print()
    
    # 3. Testar imports principais
    print("3. 📦 IMPORTS:")
    imports_to_test = [
        ('flask', 'Flask'),
        ('dotenv', 'load_dotenv'),
        ('supabase', 'create_client'),
        ('requests', 'requests'),
        ('datetime', 'datetime')
    ]
    
    for module, item in imports_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
    print()
    
    # 4. Testar estrutura de arquivos
    print("4. 📁 ESTRUTURA DE ARQUIVOS:")
    required_files = [
        'app_producao.py',
        'render_app.py',
        'requirements_producao.txt',
        'render.yaml',
        'gunicorn.conf.py',
        'config/database.py',
        'routes/main.py',
        'utils/dias_uteis.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} - AUSENTE")
    print()
    
    # 5. Testar aplicação local
    print("5. 🚀 TESTE DA APLICAÇÃO:")
    try:
        # Testar app_producao
        from app_producao import app as app_prod
        blueprints_prod = list(app_prod.blueprints.keys())
        print(f"   ✅ app_producao.py: {len(blueprints_prod)} blueprints")
        print(f"      {blueprints_prod}")
        
        # Testar client
        with app_prod.test_client() as client:
            health_resp = client.get('/health')
            print(f"   ✅ /health: {health_resp.status_code}")
            
            if health_resp.status_code == 200:
                data = health_resp.get_json()
                print(f"      Database: {data.get('database', 'N/A')}")
                print(f"      Blueprints: {len(data.get('blueprints', []))}")
    except Exception as e:
        print(f"   ❌ Erro ao testar aplicação: {e}")
    print()
    
    # 6. Verificar dependências
    print("6. 📋 DEPENDÊNCIAS:")
    try:
        with open('requirements_producao.txt', 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"   Total: {len(deps)} dependências")
            for dep in deps[:5]:  # Mostrar apenas as primeiras 5
                print(f"   - {dep}")
            if len(deps) > 5:
                print(f"   ... e mais {len(deps) - 5}")
    except Exception as e:
        print(f"   ❌ Erro ao ler requirements: {e}")
    print()
    
    print("=" * 60)
    print("✅ DIAGNÓSTICO CONCLUÍDO!")
    print()
    print("📌 PRÓXIMOS PASSOS:")
    print("1. Verifique se todas as dependências estão OK")
    print("2. Execute o monitor_render.py com a URL do seu app")
    print("3. Compare os logs do Render com este diagnóstico")

if __name__ == "__main__":
    diagnostic_check()