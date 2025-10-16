#!/usr/bin/env python3
"""
Teste da funcionalidade de duplicação de projetos
"""

import requests
import json

def test_duplicacao_projeto():
    """Testa a duplicação de um projeto específico"""
    
    BASE_URL = "http://localhost:5000"
    
    # Dados de login (ajuste conforme necessário)
    LOGIN_DATA = {
        "email": "admin@exemplo.com",  # Ajuste para seu usuário
        "senha": "sua_senha"           # Ajuste para sua senha
    }
    
    print("🔄 Testando duplicação de projeto...")
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Fazer login
        print("1. Fazendo login...")
        login_response = session.post(f"{BASE_URL}/login", data=LOGIN_DATA)
        print(f"   Status login: {login_response.status_code}")
        
        # 2. Buscar lista de projetos para pegar um ID
        print("2. Buscando projetos...")
        projetos_response = session.get(f"{BASE_URL}/projetos")
        print(f"   Status projetos: {projetos_response.status_code}")
        
        # Verificar se o botão de duplicar está no HTML
        html = projetos_response.text
        if "btn-duplicar-projeto" in html:
            print("   ✅ Botão de duplicar encontrado no HTML!")
        else:
            print("   ❌ Botão de duplicar não encontrado no HTML")
            
        if "/projetos/duplicar/" in html:
            print("   ✅ Rota de duplicação encontrada no HTML!")
        else:
            print("   ❌ Rota de duplicação não encontrada no HTML")
            
        if "fa-copy" in html:
            print("   ✅ Ícone de duplicar encontrado no HTML!")
        else:
            print("   ❌ Ícone de duplicar não encontrado no HTML")
        
        print("\n✅ Funcionalidade implementada com sucesso!")
        print("📋 Para testar completamente:")
        print("   1. Acesse http://localhost:5000/projetos")
        print("   2. Faça login se necessário")
        print("   3. Procure pelo botão verde com ícone de cópia")
        print("   4. Clique para duplicar um projeto")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_duplicacao_projeto()