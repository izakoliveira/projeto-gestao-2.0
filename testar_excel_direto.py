#!/usr/bin/env python3
"""
Teste direto da funcionalidade de exportação Excel por projeto
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import requests
from datetime import datetime

def testar_excel_projeto():
    """Testa diretamente a exportação Excel de um projeto específico"""
    print("📊 Testando exportação Excel por projeto...")
    
    # Usar um projeto ID real do sistema
    projeto_id = "b06c31f5-4998-4add-8c6b-fad5ca77e63e"  # 2604 - WORLD ABR
    
    try:
        # Fazer requisição para exportar o Excel
        url = f"http://localhost:5000/relatorio/gantt_excel?projeto_id={projeto_id}"
        print(f"🔗 Requisição: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"📝 Status: {response.status_code}")
        print(f"📝 Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            # Salvar arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"teste_excel_projeto_{timestamp}.xlsx"
            
            with open(nome_arquivo, 'wb') as f:
                f.write(response.content)
                
            print(f"✅ Excel salvo como: {nome_arquivo}")
            print(f"📏 Tamanho do arquivo: {len(response.content)} bytes")
            
            # Verificar se é um arquivo Excel válido
            if len(response.content) > 1000:  # Arquivo Excel deve ter pelo menos 1KB
                print("✅ Arquivo parece ser um Excel válido (>1KB)")
            else:
                print("⚠️  Arquivo muito pequeno, pode não ser válido")
                
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        
    print("📊 Teste concluído!")

if __name__ == '__main__':
    testar_excel_projeto()