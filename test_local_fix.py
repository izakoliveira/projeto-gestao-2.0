#!/usr/bin/env python3
"""
Teste da Correção Local
"""

from app_producao import app

def test_fix():
    print("🔍 Testando correção da rota principal...")
    
    with app.test_client() as client:
        # Testar rota principal
        resp = client.get('/')
        print(f"Status da rota '/': {resp.status_code}")
        
        if resp.status_code == 302:
            location = resp.headers.get('Location', 'N/A')
            print(f"Redirecionamento para: {location}")
        elif resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', 'N/A')
            print(f"Content-Type: {content_type}")
            if 'json' in content_type:
                print("Ainda retornando JSON - problema não resolvido")
            else:
                print("Retornando HTML - OK")
        
        # Testar outras rotas
        routes_to_test = ['/health', '/status', '/login']
        for route in routes_to_test:
            try:
                resp = client.get(route)
                print(f"Rota '{route}': {resp.status_code}")
            except Exception as e:
                print(f"Rota '{route}': Erro - {e}")

if __name__ == '__main__':
    test_fix()