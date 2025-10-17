#!/usr/bin/env python3
"""
Monitor do App Mínimo no Render
"""

import requests
import time

def test_minimal_app():
    url = 'https://sistema-gestao-projetos-2-0.onrender.com'
    
    print("🔍 TESTANDO APP MÍNIMO NO RENDER")
    print("=" * 50)
    
    endpoints = [
        ('/', 'Página inicial mínima'),
        ('/health', 'Health check básico'),
        ('/test', 'Rota de teste com env vars')
    ]
    
    for endpoint, desc in endpoints:
        try:
            resp = requests.get(f'{url}{endpoint}', timeout=15)
            print(f"✅ {endpoint}: {resp.status_code} ({desc})")
            
            if resp.status_code == 200 and 'json' in resp.headers.get('Content-Type', ''):
                data = resp.json()
                print(f"   Response: {data}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Erro - {e}")
    
    print("\n" + "=" * 50)

if __name__ == '__main__':
    print("Aguardando deploy do app mínimo...")
    time.sleep(10)
    test_minimal_app()