#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste rápido para verificar se a busca de projeto funciona corretamente
"""

import supabase_client

def test_project_search():
    """Testa a busca de projeto"""
    
    SUPABASE_URL = supabase_client.SUPABASE_URL
    headers = supabase_client.headers
    
    # Buscar todos os projetos para ver IDs disponíveis
    import requests
    
    url = f"{SUPABASE_URL}/rest/v1/projetos?select=id,nome,usuario_id"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        projetos = resp.json()
        print(f"📋 Total de projetos encontrados: {len(projetos)}")
        
        for projeto in projetos[:5]:  # Mostrar apenas os primeiros 5
            print(f"  - ID: {projeto['id']}")
            print(f"    Nome: {projeto['nome']}")
            print(f"    Usuário: {projeto['usuario_id']}")
            print()
            
        # Testar busca de um projeto específico que EXISTE
        if projetos:
            projeto_teste = projetos[0]
            print(f"🔍 Testando busca do projeto: {projeto_teste['id']}")
            
            # Simular a busca como na função de exclusão
            url_teste = f"{SUPABASE_URL}/rest/v1/projetos?id=eq.{projeto_teste['id']}&usuario_id=eq.{projeto_teste['usuario_id']}"
            resp_teste = requests.get(url_teste, headers=headers)
            
            print(f"Status: {resp_teste.status_code}")
            print(f"Resposta: {resp_teste.json()}")
            
        # Testar busca de um projeto que NÃO EXISTE
        print(f"\n🔍 Testando busca de projeto inexistente")
        url_inexistente = f"{SUPABASE_URL}/rest/v1/projetos?id=eq.00000000-0000-0000-0000-000000000000&usuario_id=eq.00000000-0000-0000-0000-000000000000"
        resp_inexistente = requests.get(url_inexistente, headers=headers)
        
        print(f"Status: {resp_inexistente.status_code}")
        print(f"Resposta: {resp_inexistente.json()}")
        
    else:
        print(f"❌ Erro ao buscar projetos: {resp.status_code}")

if __name__ == "__main__":
    test_project_search()