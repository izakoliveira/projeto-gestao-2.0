#!/usr/bin/env python3
"""
Teste Completo de Funcionamento - Simulando Render
"""

import os
import sys
from datetime import timedelta

def test_render_simulation():
    """Simular ambiente do Render localmente"""
    print("🔍 SIMULANDO AMBIENTE RENDER LOCALMENTE")
    print("=" * 60)
    
    # Simular variáveis de ambiente do Render
    render_env = {
        'PORT': '5000',
        'FLASK_ENV': 'production',
        'FLASK_APP': 'app_producao.py',
        'SECRET_KEY': 'render-test-secret-123456789',
        'SUPABASE_URL': 'https://zvdpuxggltqejplybzet.supabase.co',
        'SUPABASE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI'
    }
    
    # Aplicar variáveis de ambiente
    for key, value in render_env.items():
        os.environ[key] = value
        print(f"✅ {key} = {value[:20]}{'...' if len(value) > 20 else ''}")
    
    print("\n🚀 TESTANDO APP COM AMBIENTE RENDER:")
    
    try:
        # Recarregar módulos para aplicar novas env vars
        if 'app_producao' in sys.modules:
            del sys.modules['app_producao']
        
        from app_producao import app
        
        print(f"✅ App carregado com sucesso")
        print(f"   Blueprints: {list(app.blueprints.keys())}")
        print(f"   Secret Key: {'✅ Definida' if app.config.get('SECRET_KEY') else '❌ Não definida'}")
        print(f"   Debug: {app.config.get('DEBUG', 'N/A')}")
        
        # Testar cliente
        print("\n🧪 TESTANDO ROTAS:")
        with app.test_client() as client:
            routes_to_test = [
                ('/', '302 ou 200'),
                ('/health', '200'),
                ('/status', '200'),
                ('/login', '200'),
                ('/dashboard', '302 ou 401'),
                ('/projetos', '302 ou 401')
            ]
            
            for route, expected in routes_to_test:
                try:
                    resp = client.get(route, follow_redirects=False)
                    status = resp.status_code
                    redirect = resp.headers.get('Location', '')
                    
                    if status in [200, 302, 401]:
                        print(f"   ✅ {route}: {status} {redirect[:30] if redirect else ''}")
                    else:
                        print(f"   ⚠️ {route}: {status} (esperado {expected})")
                        
                except Exception as e:
                    print(f"   ❌ {route}: Erro - {e}")
        
        print("\n📊 TESTE DE HEALTH CHECK:")
        with app.test_client() as client:
            resp = client.get('/health')
            if resp.status_code == 200:
                data = resp.get_json()
                print(f"   Status: {data.get('status')}")
                print(f"   Database: {data.get('database')}")
                print(f"   Blueprints: {len(data.get('blueprints', []))}")
            else:
                print(f"   ❌ Health check falhou: {resp.status_code}")
                
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ SIMULAÇÃO CONCLUÍDA!")

if __name__ == '__main__':
    test_render_simulation()