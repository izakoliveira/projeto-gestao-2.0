#!/usr/bin/env python
"""
Script para testar se as seleções múltiplas estão funcionando corretamente
após o filtro ser aplicado.
"""

import requests
import sys
import time
from urllib.parse import urlencode, parse_qs

def test_multiple_selection():
    """Testa se as seleções múltiplas são mantidas após o filtro"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testando seleções múltiplas...")
    
    # 1. Primeiro, obter a página inicial para ver os projetos disponíveis
    print("\n1️⃣ Obtendo lista de projetos...")
    try:
        response = requests.get(f"{base_url}/projetos")
        if response.status_code == 200:
            print("✅ Página inicial carregada com sucesso")
        else:
            print(f"❌ Erro ao carregar página inicial: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    # 2. Simular uma requisição com múltiplos projetos selecionados
    print("\n2️⃣ Testando filtro com múltiplos projetos...")
    
    # Parâmetros simulando múltiplas seleções
    params = {
        'nome': ['Projeto Teste 1', 'Projeto Teste 2'],  # Múltiplos projetos
        'status': ['pendente', 'em progresso']  # Múltiplos status
    }
    
    # Usar getlist para simular formulário HTML
    query_string = urlencode(params, doseq=True)
    print(f"📝 Query string: {query_string}")
    
    try:
        response = requests.get(f"{base_url}/projetos?{query_string}")
        if response.status_code == 200:
            print("✅ Filtro aplicado com sucesso")
            
            # Verificar se a resposta contém as seleções
            content = response.text
            
            # Procurar por 'selected' nas opções
            selected_count = content.count('selected')
            print(f"📊 Opções marcadas como 'selected': {selected_count}")
            
            if selected_count > 0:
                print("✅ Seleções estão sendo mantidas!")
                return True
            else:
                print("⚠️ Nenhuma seleção foi mantida")
                return False
        else:
            print(f"❌ Erro no filtro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição de filtro: {e}")
        return False

def test_excel_export():
    """Testa se o export Excel funciona com múltiplos projetos"""
    
    print("\n3️⃣ Testando export Excel...")
    
    base_url = "http://localhost:5000"
    
    # Dados para o export
    export_data = {
        "gantt_base64": "test_base64_data",
        "tipo_id": "",
        "projeto_ids": [1, 2],  # Múltiplos IDs
        "status": ["pendente", "em progresso"],
        "colecao": [],
        "data_inicio": "",
        "data_fim": ""
    }
    
    try:
        response = requests.post(
            f"{base_url}/relatorio/gantt_excel",
            json=export_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Export Excel executado com sucesso")
            print(f"📄 Tipo de conteúdo: {response.headers.get('content-type', 'N/A')}")
            print(f"💾 Tamanho do arquivo: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Erro no export Excel: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição de export: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes das correções de seleções múltiplas...")
    
    success = True
    
    # Teste 1: Seleções múltiplas
    if not test_multiple_selection():
        success = False
    
    # Teste 2: Export Excel
    if not test_excel_export():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("As correções estão funcionando corretamente.")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("Verifique os logs acima para mais detalhes.")
    
    sys.exit(0 if success else 1)