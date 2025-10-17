#!/usr/bin/env python3
"""
Teste de Funcionalidade - Comparar app_producao vs render_app
Sistema de Gestão de Projetos v2.0.0
"""

import os
import sys
from datetime import timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_functionality():
    """Testar se ambas as aplicações funcionam igual"""
    
    print("🔍 Testando funcionalidade das aplicações...")
    
    # Teste 1: Import app_producao
    try:
        from app_producao import app as app_prod
        blueprints_prod = list(app_prod.blueprints.keys())
        print(f"✅ app_producao.py: {len(blueprints_prod)} blueprints")
        print(f"   Blueprints: {blueprints_prod}")
    except Exception as e:
        print(f"❌ Erro app_producao.py: {e}")
        return False
    
    # Teste 2: Import render_app  
    try:
        from render_app import app as app_render
        blueprints_render = list(app_render.blueprints.keys())
        print(f"✅ render_app.py: {len(blueprints_render)} blueprints")
        print(f"   Blueprints: {blueprints_render}")
    except Exception as e:
        print(f"❌ Erro render_app.py: {e}")
        return False
    
    # Teste 3: Comparar blueprints
    if set(blueprints_prod) == set(blueprints_render):
        print("✅ Blueprints idênticos entre as duas aplicações!")
    else:
        print("⚠️ Diferença nos blueprints:")
        missing_render = set(blueprints_prod) - set(blueprints_render)
        extra_render = set(blueprints_render) - set(blueprints_prod)
        if missing_render:
            print(f"   Faltando em render_app: {missing_render}")
        if extra_render:
            print(f"   Extra em render_app: {extra_render}")
    
    # Teste 4: Testar rotas principais
    print("\n🔗 Testando rotas principais...")
    
    # Testar app_producao
    with app_prod.test_client() as client:
        resp_health = client.get('/health')
        resp_status = client.get('/status')
        resp_main = client.get('/')
        
        print(f"app_producao - /health: {resp_health.status_code}")
        print(f"app_producao - /status: {resp_status.status_code}")  
        print(f"app_producao - /: {resp_main.status_code}")
    
    # Testar render_app
    with app_render.test_client() as client:
        resp_health = client.get('/health')
        resp_status = client.get('/status')
        resp_main = client.get('/')
        
        print(f"render_app - /health: {resp_health.status_code}")
        print(f"render_app - /status: {resp_status.status_code}")
        print(f"render_app - /: {resp_main.status_code}")
    
    print("\n🎯 Teste concluído!")
    return True

if __name__ == '__main__':
    test_app_functionality()