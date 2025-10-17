#!/usr/bin/env python3
"""
Teste Detalhado da Aplicação no Render
"""

import requests
import json

def test_detailed():
    url = 'https://sistema-gestao-projetos-2-0.onrender.com'
    
    print('🔍 TESTE DETALHADO DA APLICAÇÃO NO RENDER')
    print('=' * 60)
    
    # Testar health
    print('1. ❤️ HEALTH CHECK DETALHADO:')
    try:
        resp = requests.get(f'{url}/health', timeout=10)
        print(f'   Status Code: {resp.status_code}')
        print(f'   Response Time: {resp.elapsed.total_seconds():.2f}s')
        if resp.status_code == 200:
            data = resp.json()
            print('   Response:')
            print(json.dumps(data, indent=4))
        else:
            print(f'   Error: {resp.text}')
    except Exception as e:
        print(f'   Erro: {e}')
    
    print('\n2. 📊 STATUS DETALHADO:')
    try:
        resp = requests.get(f'{url}/status', timeout=10)
        print(f'   Status Code: {resp.status_code}')
        print(f'   Response Time: {resp.elapsed.total_seconds():.2f}s')
        if resp.status_code == 200:
            data = resp.json()
            print('   Response:')
            print(json.dumps(data, indent=4))
        else:
            print(f'   Error: {resp.text}')
    except Exception as e:
        print(f'   Erro: {e}')
    
    print('\n3. 🏠 HOME PAGE:')
    try:
        resp = requests.get(url, timeout=10)
        print(f'   Status Code: {resp.status_code}')
        print(f'   Response Time: {resp.elapsed.total_seconds():.2f}s')
        content_type = resp.headers.get('Content-Type', 'N/A')
        print(f'   Content-Type: {content_type}')
        print(f'   Content Length: {len(resp.content)} bytes')
        
        if 'json' in content_type:
            print('   Response JSON:')
            print(json.dumps(resp.json(), indent=4))
        else:
            print('   Response (primeiros 300 chars):')
            print(resp.text[:300])
            print('   ...')
    except Exception as e:
        print(f'   Erro: {e}')
    
    print('\n4. 🔐 TESTE DE ROTAS ADICIONAIS:')
    test_routes = ['/login', '/dashboard', '/projetos', '/admin']
    for route in test_routes:
        try:
            resp = requests.get(f'{url}{route}', timeout=5, allow_redirects=False)
            print(f'   {route}: {resp.status_code}')
        except Exception as e:
            print(f'   {route}: Error - {e}')
    
    print('\n' + '=' * 60)
    print('✅ TESTE CONCLUÍDO!')

if __name__ == '__main__':
    test_detailed()