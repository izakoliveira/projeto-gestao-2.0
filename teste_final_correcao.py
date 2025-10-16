#!/usr/bin/env python3

import requests
import time

print("🧪 TESTANDO ROTA DE TESTE SEM AUTENTICAÇÃO")
print("="*45)

# Aguardar app estar pronta
time.sleep(2)

try:
    # Teste da nossa nova rota sem autenticação
    print("1️⃣ Testando /projetos_teste_sem_auth SEM filtros...")
    response = requests.get('http://localhost:5000/projetos_teste_sem_auth', timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        print(f"   ✅ Página carregada ({len(content)} chars)")
        
        # Verificar se os projetos aparecem
        if '2509 - WORLD SET' in content:
            print("   ✅ Projeto 2509 encontrado")
            
            # Verificar se a data aparece
            if '2025-09-12' in content:
                print("   ✅ Data de lançamento 2025-09-12 mostrada corretamente!")
            elif 'None' in content:
                print("   ❌ Ainda mostra None para a data")
            else:
                print("   ❓ Data não encontrada no formato esperado")
        
        if '2606 - WORLD JUN' in content:
            print("   ✅ Projeto 2606 encontrado")
            
            if '2026-06-12' in content:
                print("   ✅ Data de lançamento 2026-06-12 mostrada corretamente!")
            elif 'None' in content:
                print("   ❌ Ainda mostra None para a data")
        
        # Mostrar trechos relevantes
        lines = content.split('\n')
        for line in lines:
            if 'Data de lançamento:' in line:
                print(f"   📝 {line.strip()}")
    
    print(f"\n2️⃣ Testando com filtro status=pendente...")
    response = requests.get('http://localhost:5000/projetos_teste_sem_auth?status=pendente', timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200 and '2606 - WORLD JUN' in response.text:
        if '2026-06-12' in response.text:
            print("   ✅ Com filtro pendente: Projeto 2606 mostra data corretamente!")
    
    print(f"\n3️⃣ Testando com filtro status=concluída...")
    response = requests.get('http://localhost:5000/projetos_teste_sem_auth?status=concluída', timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200 and '2509 - WORLD SET' in response.text:
        if '2025-09-12' in response.text:
            print("   ✅ Com filtro concluída: Projeto 2509 mostra data corretamente!")

except Exception as e:
    print(f"❌ Erro: {e}")

print(f"\n📊 CONCLUSÃO:")
print(f"Se os testes acima mostraram as datas corretas,")
print(f"nossa correção da função normalizar() está funcionando!")