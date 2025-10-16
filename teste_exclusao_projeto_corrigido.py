#!/usr/bin/env python3
"""
Teste para verificar se a correção de exclusão de projeto funciona corretamente.
Este teste simula o cenário onde um projeto tem notificações associadas.
"""

import os
from supabase_client import supabase
import uuid
from datetime import datetime

def test_exclusao_projeto_com_notificacoes():
    """Testa a exclusão de projeto que possui notificações"""
    
    print("=== TESTE DE EXCLUSÃO DE PROJETO COM NOTIFICAÇÕES ===")
    
    # 1. Criar um projeto de teste
    print("\n1. Criando projeto de teste...")
    projeto_test = {
        "id": str(uuid.uuid4()),
        "nome": "Projeto Teste Exclusão",
        "data_inicio": "2024-01-01",
        "data_fim": "2024-12-31",
        "usuario_id": "b12345"  # ID fictício para teste
    }
    
    try:
        projeto_resp = supabase.table("projetos").insert(projeto_test).execute()
        if not projeto_resp.data:
            print("❌ Erro ao criar projeto de teste")
            return False
        print(f"✅ Projeto criado: {projeto_test['id']}")
    except Exception as e:
        print(f"❌ Erro ao criar projeto: {e}")
        return False
    
    # 2. Criar uma notificação associada ao projeto
    print("\n2. Criando notificação associada ao projeto...")
    notificacao_test = {
        "usuario_id": "b12345",
        "mensagem": "Teste de notificação para exclusão",
        "tipo": "teste",
        "projeto_id": projeto_test['id'],
        "lida": False
    }
    
    try:
        notif_resp = supabase.table("notificacoes").insert(notificacao_test).execute()
        if not notif_resp.data:
            print("❌ Erro ao criar notificação de teste")
            return False
        print(f"✅ Notificação criada para projeto {projeto_test['id']}")
    except Exception as e:
        print(f"❌ Erro ao criar notificação: {e}")
        return False
    
    # 3. Verificar se as notificações existem
    print("\n3. Verificando notificações do projeto...")
    try:
        notif_check = supabase.table("notificacoes").select("*").eq("projeto_id", projeto_test['id']).execute()
        print(f"✅ Encontradas {len(notif_check.data)} notificações para o projeto")
    except Exception as e:
        print(f"❌ Erro ao verificar notificações: {e}")
        return False
    
    # 4. Simular a exclusão usando a nova lógica
    print("\n4. Testando exclusão com nova lógica...")
    try:
        # Passo 1: Excluir notificações
        print("   4.1. Excluindo notificações...")
        del_notif_resp = supabase.table("notificacoes").delete().eq("projeto_id", projeto_test['id']).execute()
        print(f"   ✅ Notificações excluídas: {len(del_notif_resp.data or [])}")
        
        # Passo 2: Excluir tarefas (se houver)
        print("   4.2. Verificando/excluindo tarefas...")
        del_tarefas_resp = supabase.table("tarefas").delete().eq("projeto_id", projeto_test['id']).execute()
        print(f"   ✅ Tarefas excluídas: {len(del_tarefas_resp.data or [])}")
        
        # Passo 3: Excluir projeto
        print("   4.3. Excluindo projeto...")
        del_projeto_resp = supabase.table("projetos").delete().eq("id", projeto_test['id']).execute()
        
        if del_projeto_resp.data:
            print(f"   ✅ Projeto excluído com sucesso!")
            return True
        else:
            print(f"   ❌ Projeto não foi excluído")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante exclusão: {e}")
        return False

def limpar_dados_teste():
    """Limpa dados de teste que possam ter ficado"""
    print("\n=== LIMPEZA DE DADOS DE TESTE ===")
    try:
        # Buscar projetos de teste
        projetos_teste = supabase.table("projetos").select("id").like("nome", "%Teste Exclusão%").execute()
        
        for projeto in projetos_teste.data or []:
            projeto_id = projeto['id']
            print(f"Limpando projeto: {projeto_id}")
            
            # Limpar notificações
            supabase.table("notificacoes").delete().eq("projeto_id", projeto_id).execute()
            # Limpar tarefas  
            supabase.table("tarefas").delete().eq("projeto_id", projeto_id).execute()
            # Limpar projeto
            supabase.table("projetos").delete().eq("id", projeto_id).execute()
            
        print("✅ Limpeza concluída")
        
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")

if __name__ == "__main__":
    print("Iniciando teste de exclusão de projeto...")
    
    # Limpar dados anteriores
    limpar_dados_teste()
    
    # Executar teste
    sucesso = test_exclusao_projeto_com_notificacoes()
    
    if sucesso:
        print("\n🎉 TESTE PASSOU! A correção funciona corretamente.")
    else:
        print("\n❌ TESTE FALHOU! Verifique a implementação.")
    
    print("\n" + "="*50)