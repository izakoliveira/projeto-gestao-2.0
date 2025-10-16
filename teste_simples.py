#!/usr/bin/env python3
# Teste simples e direto

import requests

try:
    print("🧪 Testando /projetos_teste_sem_auth...")
    response = requests.get('http://localhost:5000/projetos_teste_sem_auth', timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Página carregada!")
        content = response.text
        
        # Verificar resultados críticos
        if '2509 - WORLD SET' in content and '2025-09-12' in content:
            print("✅ SUCESSO: Projeto 2509 mostra data 2025-09-12!")
        
        if '2606 - WORLD JUN' in content and '2026-06-12' in content:
            print("✅ SUCESSO: Projeto 2606 mostra data 2026-06-12!")
        
        if 'None' in content:
            print("❌ Ainda tem 'None' na página")
        
        print("\nConteúdo da página:")
        print("="*40)
        print(content[:1000] + "..." if len(content) > 1000 else content)
    
    elif response.status_code == 404:
        print("❌ Erro 404 - Rota não encontrada")
    else:
        print(f"❌ Erro {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"❌ Erro de conexão: {e}")