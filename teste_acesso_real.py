#!/usr/bin/env python3

import requests
import time

print("🔍 TESTANDO ACESSO DIRETO À PÁGINA")
print("="*40)

try:
    # Aguardar um momento para a app estar pronta
    time.sleep(1)
    
    # Teste 1: Sem filtros (deveria mostrar todos os projetos e suas datas de lançamento)
    print("1️⃣ Testando /projetos SEM filtros:")
    response = requests.get('http://localhost:5000/projetos', timeout=10)
    print(f"   Status: {response.status_code}")
    
    # Procurar pelos projetos específicos
    content = response.text
    
    if '2509 - WORLD SET' in content:
        print("   ✅ Projeto 2509 encontrado")
        # Procurar pela data ou None próximo ao projeto
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '2509 - WORLD SET' in line:
                # Procurar nas próximas 10 linhas
                for j in range(i, min(i+10, len(lines))):
                    if 'None' in lines[j]:
                        print("   ❌ Ainda mostra 'None' para data de lançamento")
                        break
                    elif '2025-09-12' in lines[j] or '12/09/2025' in lines[j]:
                        print("   ✅ Mostra data de lançamento corretamente!")
                        break
                else:
                    print("   ❓ Não encontrou 'None' nem data nas linhas seguintes")
                break
    else:
        print("   ❌ Projeto 2509 NÃO encontrado")
    
    if '2606 - WORLD JUN' in content:
        print("   ✅ Projeto 2606 encontrado")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '2606 - WORLD JUN' in line:
                for j in range(i, min(i+10, len(lines))):
                    if 'None' in lines[j]:
                        print("   ❌ Ainda mostra 'None' para data de lançamento")
                        break
                    elif '2026-06-12' in lines[j] or '12/06/2026' in lines[j]:
                        print("   ✅ Mostra data de lançamento corretamente!")
                        break
                else:
                    print("   ❓ Não encontrou 'None' nem data nas linhas seguintes")
                break
    else:
        print("   ❌ Projeto 2606 NÃO encontrado")

except Exception as e:
    print(f"❌ Erro no teste: {e}")

print("\n🔍 Aguardando logs do Flask para aparecer...")
time.sleep(2)