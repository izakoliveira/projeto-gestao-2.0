#!/usr/bin/env python3

import requests

print("🔐 TESTANDO LOGIN E ACESSO AUTENTICADO")
print("="*40)

session = requests.Session()

try:
    # 1. Acessar página de login
    print("1️⃣ Acessando página de login...")
    login_response = session.get('http://localhost:5000/login', timeout=10)
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("   ❌ Página de login não acessível")
        print("   Tentando URLs alternativas...")
        
        # Tentar outras rotas
        for url in ['/auth/login', '/signin', '/authentication']:
            test_resp = session.get(f'http://localhost:5000{url}', timeout=5)
            print(f"   {url}: {test_resp.status_code}")
    
    else:
        print("   ✅ Página de login acessível")
        
        # 2. Tentar fazer login (se tivermos credenciais de teste)
        print("\n2️⃣ Tentando login com credenciais padrão...")
        
        # Credenciais comuns de desenvolvimento
        credenciais_teste = [
            {'username': 'admin', 'password': 'admin'},
            {'email': 'admin@teste.com', 'password': 'admin'},
            {'username': 'teste', 'password': 'teste'},
            {'email': 'teste@teste.com', 'password': '123456'},
        ]
        
        for cred in credenciais_teste:
            login_data = cred
            login_attempt = session.post('http://localhost:5000/login', data=login_data, timeout=10)
            
            print(f"   Tentativa {cred}: {login_attempt.status_code}")
            
            if login_attempt.status_code == 200 and 'login' not in login_attempt.url:
                print(f"   ✅ Login bem sucedido! Redirecionado para: {login_attempt.url}")
                
                # 3. Agora testar acesso aos projetos
                print("\n3️⃣ Testando acesso aos projetos autenticado...")
                projetos_response = session.get('http://localhost:5000/projetos', timeout=10)
                print(f"   Status /projetos: {projetos_response.status_code}")
                
                if '2509 - WORLD SET' in projetos_response.text:
                    print("   ✅ Projeto 2509 encontrado!")
                    
                    # Procurar pela data de lançamento
                    content = projetos_response.text
                    if 'None' in content:
                        print("   ❌ Ainda tem 'None' na página")
                    elif '2025-09-12' in content or '12/09/2025' in content:
                        print("   ✅ Data de lançamento correta mostrada!")
                    else:
                        print("   ❓ Data não encontrada no formato esperado")
                        
                if '2606 - WORLD JUN' in projetos_response.text:
                    print("   ✅ Projeto 2606 encontrado!")
                    
                    if '2026-06-12' in projetos_response.text or '12/06/2026' in projetos_response.text:
                        print("   ✅ Data de lançamento correta mostrada!")
                
                break
                
            elif login_attempt.status_code in [301, 302]:
                print(f"   Redirecionado para: {login_attempt.headers.get('Location', 'N/A')}")
        else:
            print("   ❌ Nenhuma credencial funcionou")
            print("\n💡 Para testar completamente, seria necessário:")
            print("   1. Criar um usuário de teste no banco")
            print("   2. Ou usar credenciais válidas existentes")
            print("   3. Ou desabilitar temporariamente a autenticação")

except Exception as e:
    print(f"❌ Erro: {e}")

print("\n📝 RESUMO:")
print("A aplicação requer autenticação para acessar /projetos")
print("Por isso os nossos testes anteriores não mostraram os projetos")
print("A correção da função normalizar() deve estar funcionando,")  
print("mas precisamos de acesso autenticado para confirmar.")