#!/usr/bin/env python3

import requests

print("🔍 TESTANDO REDIRECIONAMENTOS E AUTENTICAÇÃO")
print("="*45)

try:
    session = requests.Session()
    
    # Primeiro, verificar se há redirecionamento
    response = session.get('http://localhost:5000/projetos', allow_redirects=False, timeout=10)
    print(f"1️⃣ Status sem seguir redirecionamentos: {response.status_code}")
    
    if response.status_code in [301, 302, 303, 307, 308]:
        print(f"   🔀 Redirecionado para: {response.headers.get('Location', 'N/A')}")
        
        # Seguir o redirecionamento
        response = session.get('http://localhost:5000/projetos', timeout=10)
        print(f"2️⃣ Status após seguir redirecionamento: {response.status_code}")
    
    # Verificar se chegou na página de login
    if 'login' in response.url.lower() or 'signin' in response.url.lower():
        print("   🔐 Redirecionado para página de login!")
        print(f"   URL final: {response.url}")
        
        # Tentar acessar a página de login para fazer login
        print("\n3️⃣ Tentando fazer login automático...")
        
        # Primeiro pegar a página de login para tokens CSRF
        login_page = session.get('http://localhost:5000/auth/login', timeout=10)
        print(f"   Login page status: {login_page.status_code}")
        
    elif response.status_code == 200:
        print("   ✅ Acesso direto permitido!")
        
        # Verificar o conteúdo
        content = response.text
        if len(content) < 1000:
            print(f"   ⚠️  Conteúdo muito pequeno ({len(content)} chars), pode ser página vazia")
            print(f"   Primeiras 300 chars: {content[:300]}")
        else:
            print(f"   ✅ Conteúdo normal ({len(content)} chars)")
            
            # Procurar projetos
            if 'projeto' in content.lower():
                print("   ✅ Palavra 'projeto' encontrada no conteúdo")
            else:
                print("   ❌ Palavra 'projeto' NÃO encontrada")
                
    else:
        print(f"   ❌ Erro: {response.status_code}")
        print(f"   Content: {response.text[:200] if response.text else 'Vazio'}")

except Exception as e:
    print(f"❌ Erro: {e}")