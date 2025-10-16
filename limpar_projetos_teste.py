#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para limpar projetos de teste
"""

import supabase_client
import requests

def clean_test_projects():
    """Remove todos os projetos de teste"""
    
    SUPABASE_URL = supabase_client.SUPABASE_URL
    headers = supabase_client.headers
    
    print("🔍 Buscando projetos de teste...")
    
    # Buscar projetos que contêm "Teste" no nome
    url = f"{SUPABASE_URL}/rest/v1/projetos?nome=like.*Teste*"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ Erro ao buscar projetos: {resp.status_code}")
        return
    
    projetos = resp.json()
    print(f"📋 Projetos de teste encontrados: {len(projetos)}")
    
    if not projetos:
        print("✅ Nenhum projeto de teste encontrado!")
        return
    
    for projeto in projetos:
        print(f"\n🗑️ Removendo projeto:")
        print(f"  - ID: {projeto['id']}")
        print(f"  - Nome: {projeto['nome']}")
        print(f"  - Usuário: {projeto['usuario_id']}")
        
        try:
            # 1. Excluir notificações relacionadas
            url_notif = f"{SUPABASE_URL}/rest/v1/notificacoes?projeto_id=eq.{projeto['id']}"
            resp_notif = requests.delete(url_notif, headers=headers)
            print(f"    ✅ Notificações: {resp_notif.status_code}")
            
            # 2. Excluir tarefas do projeto
            url_tarefas = f"{SUPABASE_URL}/rest/v1/tarefas?projeto_id=eq.{projeto['id']}"
            resp_tarefas = requests.delete(url_tarefas, headers=headers)
            print(f"    ✅ Tarefas: {resp_tarefas.status_code}")
            
            # 3. Excluir projeto
            url_projeto = f"{SUPABASE_URL}/rest/v1/projetos?id=eq.{projeto['id']}"
            resp_projeto = requests.delete(url_projeto, headers=headers)
            print(f"    ✅ Projeto: {resp_projeto.status_code}")
            
            if resp_projeto.status_code in [200, 204]:
                print(f"    🎉 Projeto '{projeto['nome']}' removido com sucesso!")
            else:
                print(f"    ❌ Erro ao remover projeto: {resp_projeto.text}")
                
        except Exception as e:
            print(f"    💥 Erro: {e}")

def main():
    print("🧹 Limpando projetos de teste...")
    print("=" * 50)
    
    try:
        clean_test_projects()
        print("\n✅ Limpeza concluída!")
        
    except Exception as e:
        print(f"\n💥 Erro durante a limpeza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()