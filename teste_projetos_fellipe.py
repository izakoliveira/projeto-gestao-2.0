#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

from supabase import create_client, Client

# Configuração do Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def testar_projetos_fellipe():
    """Testa todos os projetos e permissões do usuário Fellipe"""
    
    # ID do usuário Fellipe
    user_id = "6afb28b7-2c10-4f9b-a0d5-c9ce27600521"
    
    print(f"🔍 Testando projetos e permissões para usuário Fellipe (ID: {user_id})")
    print("=" * 70)
    
    try:
        # 1. Buscar todos os projetos
        print("1. Buscando TODOS os projetos...")
        todos_projetos_resp = supabase.table("projetos").select("id, nome, usuario_id").execute()
        todos_projetos = todos_projetos_resp.data if hasattr(todos_projetos_resp, 'data') else []
        
        print(f"   ✅ Total de projetos no sistema: {len(todos_projetos)}")
        for projeto in todos_projetos:
            print(f"      - {projeto['nome']} (ID: {projeto['id']}, Usuário: {projeto['usuario_id']})")
        
        # 2. Buscar projetos do usuário Fellipe
        print("\n2. Buscando projetos DO usuário Fellipe...")
        projetos_fellipe_resp = supabase.table("projetos").select("id, nome").eq("usuario_id", user_id).execute()
        projetos_fellipe = projetos_fellipe_resp.data if hasattr(projetos_fellipe_resp, 'data') else []
        
        print(f"   ✅ Projetos DO usuário Fellipe: {len(projetos_fellipe)}")
        for projeto in projetos_fellipe:
            print(f"      - {projeto['nome']} (ID: {projeto['id']})")
        
        # 3. Buscar permissões de visualização
        print("\n3. Buscando permissões de visualização...")
        try:
            permissoes_resp = supabase.table("projetos_usuarios_visiveis").select("*").eq("usuario_id", user_id).execute()
            permissoes = permissoes_resp.data if hasattr(permissoes_resp, 'data') else []
            
            print(f"   ✅ Permissões de visualização: {len(permissoes)}")
            for permissao in permissoes:
                print(f"      - Projeto ID: {permissao['projeto_id']}")
        except Exception as e:
            print(f"   ❌ Erro ao buscar permissões: {str(e)}")
        
        # 4. Buscar tarefas do usuário Fellipe
        print("\n4. Buscando tarefas do usuário Fellipe...")
        tarefas_fellipe_resp = supabase.table("tarefas").select("id, nome, status, projeto_id").eq("usuario_id", user_id).execute()
        tarefas_fellipe = tarefas_fellipe_resp.data if hasattr(tarefas_fellipe_resp, 'data') else []
        
        print(f"   ✅ Tarefas do usuário Fellipe: {len(tarefas_fellipe)}")
        for tarefa in tarefas_fellipe:
            projeto_nome = "N/A"
            if tarefa.get('projeto_id'):
                projeto_info = next((p for p in todos_projetos if p['id'] == tarefa['projeto_id']), None)
                if projeto_info:
                    projeto_nome = projeto_info['nome']
            
            print(f"      - {tarefa['nome']} (Status: {tarefa.get('status', 'N/A')}, Projeto: {projeto_nome})")
        
        # 5. Buscar tarefas de todos os projetos (para ver se há tarefas em projetos que o Fellipe pode ver)
        print("\n5. Buscando tarefas de TODOS os projetos...")
        todas_tarefas_resp = supabase.table("tarefas").select("id, nome, status, projeto_id, usuario_id").execute()
        todas_tarefas = todas_tarefas_resp.data if hasattr(todas_tarefas_resp, 'data') else []
        
        print(f"   ✅ Total de tarefas no sistema: {len(todas_tarefas)}")
        
        # 6. Verificar se há tarefas em projetos que o Fellipe pode acessar
        print("\n6. Verificando tarefas em projetos acessíveis...")
        projetos_acessiveis = [p['id'] for p in projetos_fellipe]
        
        # Adicionar projetos das permissões
        for permissao in permissoes:
            if permissao['projeto_id'] not in projetos_acessiveis:
                projetos_acessiveis.append(permissao['projeto_id'])
        
        tarefas_acessiveis = []
        for tarefa in todas_tarefas:
            if tarefa.get('projeto_id') in projetos_acessiveis:
                tarefas_acessiveis.append(tarefa)
        
        print(f"   ✅ Tarefas em projetos acessíveis: {len(tarefas_acessiveis)}")
        for tarefa in tarefas_acessiveis:
            projeto_info = next((p for p in todos_projetos if p['id'] == tarefa['projeto_id']), None)
            projeto_nome = projeto_info['nome'] if projeto_info else "N/A"
            print(f"      - {tarefa['nome']} (Status: {tarefa.get('status', 'N/A')}, Projeto: {projeto_nome})")
        
        # 7. Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO - USUÁRIO FELLIPE")
        print("=" * 70)
        print(f"Projetos próprios: {len(projetos_fellipe)}")
        print(f"Permissões de visualização: {len(permissoes)}")
        print(f"Projetos acessíveis: {len(projetos_acessiveis)}")
        print(f"Tarefas próprias: {len(tarefas_fellipe)}")
        print(f"Tarefas em projetos acessíveis: {len(tarefas_acessiveis)}")
        
        # 8. Diagnóstico
        print("\n🔍 DIAGNÓSTICO:")
        if len(projetos_fellipe) == 0 and len(permissoes) == 0:
            print("   ❌ PROBLEMA: Usuário não tem projetos próprios nem permissões de visualização!")
            print("   💡 SOLUÇÃO: O dashboard só mostra projetos próprios, não projetos compartilhados")
        elif len(projetos_fellipe) == 0 and len(permissoes) > 0:
            print("   ⚠️  AVISO: Usuário tem permissões mas não projetos próprios")
            print("   💡 SOLUÇÃO: O dashboard precisa ser atualizado para incluir projetos compartilhados")
        else:
            print("   ✅ Usuário tem projetos próprios")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_projetos_fellipe() 