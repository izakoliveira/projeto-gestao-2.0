#!/usr/bin/env python3
"""
Teste Simples do Render - Verificar Mudanças
"""

import requests
import json

def test_render_changes():
    url = 'https://sistema-gestao-projetos-2-0.onrender.com'
    
    print('🔍 VERIFICANDO SE RENDER ATUALIZOU')
    print('=' * 50)
    
    # Teste 1: Health check
    print('1. Testando /health...')
    try:
        resp = requests.get(f'{url}/health', timeout=15)
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Verificar se é app mínimo
            if 'app' in data:
                print(f'   🎉 APP MÍNIMO DETECTADO! Tipo: {data["app"]}')
                return True
            else:
                print('   ⚠️ Ainda é o app antigo (sem campo "app")')
                print(f'   Versão: {data.get("version", "N/A")}')
        else:
            print(f'   ❌ Erro: {resp.status_code}')
            
    except Exception as e:
        print(f'   ❌ Erro: {e}')
    
    # Teste 2: Página principal
    print('\n2. Testando página principal...')
    try:
        resp = requests.get(url, timeout=15)
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200:
            data = resp.json()
            if 'minimal' in str(data.get('version', '')):
                print('   🎉 PÁGINA PRINCIPAL MÍNIMA!')
                return True
            else:
                print('   ⚠️ Não é app mínimo')
        elif resp.status_code == 404:
            print('   📝 404 - App pode estar reiniciando')
        else:
            print(f'   ❌ Erro inesperado: {resp.status_code}')
            
    except Exception as e:
        print(f'   ❌ Erro: {e}')
    
    # Teste 3: Nova rota /test
    print('\n3. Testando nova rota /test...')
    try:
        resp = requests.get(f'{url}/test', timeout=10)
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200:
            print('   🎉 ROTA /test FUNCIONANDO - APP MÍNIMO ATIVO!')
            data = resp.json()
            print(f'   Response: {data}')
            return True
        elif resp.status_code == 404:
            print('   ⚠️ Rota /test não existe - ainda app antigo')
        else:
            print(f'   ❌ Erro: {resp.status_code}')
            
    except Exception as e:
        print(f'   ❌ Erro: {e}')
    
    print('\n' + '=' * 50)
    print('❌ APP MÍNIMO AINDA NÃO ESTÁ ATIVO')
    print('   Aguarde mais alguns minutos e tente novamente')
    return False

if __name__ == '__main__':
    test_render_changes()