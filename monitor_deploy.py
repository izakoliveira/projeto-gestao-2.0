#!/usr/bin/env python3
"""
Monitor Contínuo - Aguardar Deploy
"""

import requests
import time
from datetime import datetime

def monitor_deploy():
    url = 'https://sistema-gestao-projetos-2-0.onrender.com'
    
    print('🔄 MONITORAMENTO CONTÍNUO DO DEPLOY')
    print('   Pressione Ctrl+C para parar')
    print('=' * 60)
    
    check_count = 0
    
    while check_count < 20:  # Máximo 20 tentativas (10 minutos)
        check_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f'\n⏰ [{timestamp}] Verificação {check_count}/20:')
        
        try:
            # Testar health check
            resp = requests.get(f'{url}/health', timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Verificar se é app mínimo
                if 'app' in data and data['app'] == 'minimal':
                    print('🎉 SUCCESS! APP MÍNIMO ESTÁ FUNCIONANDO!')
                    print(f'   Response: {data}')
                    
                    # Testar outras rotas
                    test_routes = ['/', '/test']
                    for route in test_routes:
                        try:
                            r = requests.get(f'{url}{route}', timeout=5)
                            print(f'   {route}: {r.status_code}')
                        except:
                            print(f'   {route}: Error')
                    
                    print('\n✅ DEPLOY CONCLUÍDO COM SUCESSO!')
                    return True
                else:
                    print('   ⚠️ Ainda app antigo - aguardando...')
            else:
                print(f'   ❌ Status: {resp.status_code}')
                
        except Exception as e:
            print(f'   ❌ Erro: {e}')
        
        # Aguardar 30 segundos
        if check_count < 20:
            print('   💤 Aguardando 30s...')
            time.sleep(30)
    
    print('\n⏰ Timeout atingido (10 minutos)')
    print('   Deploy pode ter falhado ou demorado mais que esperado')
    print('   Verifique os logs no dashboard do Render')
    return False

if __name__ == '__main__':
    try:
        monitor_deploy()
    except KeyboardInterrupt:
        print('\n🛑 Monitoramento interrompido pelo usuário')