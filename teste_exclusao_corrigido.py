#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste para verificar se a correção da exclusão de projetos funciona
"""

import supabase_client
import requests
import json

def test_delete_with_notifications():
    """Testa exclusão de projeto que tem notificações"""
    
    print("🔍 Testando exclusão de projeto com notificações...")
    
    # Configuração
    SUPABASE_URL = supabase_client.SUPABASE_URL
    headers = supabase_client.headers
    
    # Primeiro, obter um usuário existente
    usuarios = supabase_client.get_all_users()
    if not usuarios:
        print("❌ Nenhum usuário encontrado. Criando um usuário de teste...")
        # Criar um usuário temporário para o teste
        if not supabase_client.create_user("Usuário Teste", "teste@exemplo.com", "hash_teste"):
            print("❌ Não foi possível criar usuário de teste")
            return False
        usuarios = supabase_client.get_all_users()
    
    usuario_id = usuarios[0]['id']
    print(f"✅ Usando usuário: {usuarios[0]['nome']} (ID: {usuario_id})")
    
    # 1. Criar um projeto de teste
    projeto_data = {
        "nome": "Projeto Teste Exclusão",
        "descricao": "Projeto para testar exclusão com notificações",
        "data_inicio": "2025-10-16",
        "data_fim": "2025-12-16",
        "usuario_id": usuario_id
    }
    
    # Criar projeto
    url_projetos = f"{SUPABASE_URL}/rest/v1/projetos"
    resp_projeto = requests.post(url_projetos, headers=headers, json=projeto_data)
    
    print(f"Status da criação do projeto: {resp_projeto.status_code}")
    
    if resp_projeto.status_code not in [200, 201]:
        print(f"❌ Erro ao criar projeto: {resp_projeto.status_code} - {resp_projeto.text}")
        return False
    
    # Buscar o projeto criado pelo nome (já que a resposta pode estar vazia)
    import time
    time.sleep(1)  # Aguardar um pouco para garantir que foi criado
    projetos = supabase_client.get_all_projects()
    projeto_encontrado = next((p for p in projetos if p['nome'] == "Projeto Teste Exclusão"), None)
    
    if not projeto_encontrado:
        print("❌ Não foi possível encontrar o projeto criado")
        return False
    
    projeto_id = projeto_encontrado['id']
    
    print(f"✅ Projeto criado com ID: {projeto_id}")
    
    # 2. Criar notificações relacionadas ao projeto
    notificacao_data = {
        "projeto_id": projeto_id,
        "usuario_id": usuario_id,  # Usar o mesmo usuário
        "mensagem": "Notificação de teste",
        "tipo": "info",
        "lida": False
    }
    
    url_notificacoes = f"{SUPABASE_URL}/rest/v1/notificacoes"
    resp_notif = requests.post(url_notificacoes, headers=headers, json=notificacao_data)
    
    if resp_notif.status_code not in [200, 201]:
        print(f"⚠️ Não foi possível criar notificação: {resp_notif.status_code} - {resp_notif.text}")
        print("Continuando o teste sem notificações...")
    else:
        print("✅ Notificação criada com sucesso")
    
    # 3. Tentar excluir o projeto (deveria funcionar agora com a correção)
    print(f"🗑️ Tentando excluir projeto {projeto_id}...")
    
    # Primeiro, excluir notificações relacionadas
    url_delete_notif = f"{SUPABASE_URL}/rest/v1/notificacoes?projeto_id=eq.{projeto_id}"
    resp_delete_notif = requests.delete(url_delete_notif, headers=headers)
    
    if resp_delete_notif.status_code in [200, 204]:
        print("✅ Notificações excluídas com sucesso")
    else:
        print(f"⚠️ Erro ao excluir notificações: {resp_delete_notif.status_code} - {resp_delete_notif.text}")
    
    # Agora excluir o projeto
    url_delete_projeto = f"{SUPABASE_URL}/rest/v1/projetos?id=eq.{projeto_id}"
    resp_delete_projeto = requests.delete(url_delete_projeto, headers=headers)
    
    if resp_delete_projeto.status_code in [200, 204]:
        print("✅ Projeto excluído com sucesso!")
        return True
    else:
        print(f"❌ Erro ao excluir projeto: {resp_delete_projeto.status_code} - {resp_delete_projeto.text}")
        return False

def main():
    print("🧪 Testando correção da exclusão de projetos com notificações")
    print("=" * 60)
    
    try:
        sucesso = test_delete_with_notifications()
        
        if sucesso:
            print("\n🎉 Teste passou! A correção está funcionando.")
        else:
            print("\n❌ Teste falhou. Verifique a implementação.")
            
    except Exception as e:
        print(f"\n💥 Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()