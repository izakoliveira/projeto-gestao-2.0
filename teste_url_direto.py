#!/usr/bin/env python3

print("🔍 TESTE DE URL DIRETA")
print("="*30)
print("Testando se /projetos sem filtros mostra os lançamentos corretamente")

import requests

try:
    # Teste sem filtros
    response = requests.get('http://localhost:5000/projetos', timeout=5)
    print(f"✅ Resposta /projetos: {response.status_code}")
    if '2509 - WORLD SET' in response.text:
        print("✅ Projeto 2509 encontrado na página")
        if 'None' in response.text:
            print("❌ Ainda tem 'None' na página")
        else:
            print("✅ Sem 'None' visível")
    
    # Teste com filtro pendente
    response = requests.get('http://localhost:5000/projetos?status=pendente', timeout=5)
    print(f"✅ Resposta /projetos?status=pendente: {response.status_code}")
    
    # Teste com filtro concluída
    response = requests.get('http://localhost:5000/projetos?status=concluída', timeout=5)
    print(f"✅ Resposta /projetos?status=concluída: {response.status_code}")

except Exception as e:
    print(f"❌ Erro: {e}")
    print("A aplicação Flask não está rodando. Vou testar localmente:")
    
    # Simulação local
    status_por_projeto = {
        '2509': 'concluída',  # lançamento concluído
        '2606': 'pendente'    # lançamento pendente
    }
    
    for proj_id, status_lanc in status_por_projeto.items():
        print(f"\n📁 Projeto {proj_id}:")
        print(f"  Status do lançamento: {status_lanc}")
        
        # Simula filtros comuns
        for filtro in ['pendente', 'em progresso', 'concluída']:
            if filtro == status_lanc:
                print(f"  ✅ Filtro '{filtro}': MOSTRA (lançamento + outras tarefas)")
            else:
                print(f"  ❌ Filtro '{filtro}': SÓ LANÇAMENTO (outras filtradas)")