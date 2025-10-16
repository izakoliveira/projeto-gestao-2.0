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

def testar_dashboard_fellipe():
    """Testa especificamente o dashboard do usuário Fellipe"""
    
    # ID do usuário Fellipe
    user_id = "6afb28b7-2c10-4f9b-a0d5-c9ce27600521"
    
    print(f"🔍 Testando dashboard para usuário Fellipe (ID: {user_id})")
    print("=" * 60)
    
    try:
        # 1. Buscar projetos do usuário
        print("1. Buscando projetos do usuário...")
        projetos_resp = supabase.table("projetos").select("id, nome").eq("usuario_id", user_id).execute()
        projetos = projetos_resp.data if hasattr(projetos_resp, 'data') else []
        projetos_count = len(projetos)
        projetos_ids = [p['id'] for p in projetos]
        
        print(f"   ✅ Projetos encontrados: {projetos_count}")
        for projeto in projetos:
            print(f"      - {projeto['nome']} (ID: {projeto['id']})")
        
        # 2. Buscar tarefas do usuário
        print("\n2. Buscando tarefas do usuário...")
        tarefas_usuario_resp = supabase.table("tarefas").select("id, nome, status").eq("usuario_id", user_id).execute()
        tarefas_usuario = tarefas_usuario_resp.data if hasattr(tarefas_usuario_resp, 'data') else []
        
        print(f"   ✅ Tarefas do usuário: {len(tarefas_usuario)}")
        for tarefa in tarefas_usuario:
            print(f"      - {tarefa['nome']} (Status: {tarefa.get('status', 'N/A')})")
        
        # 3. Buscar tarefas dos projetos do usuário
        print("\n3. Buscando tarefas dos projetos...")
        tarefas_projetos = []
        if projetos_ids:
            for projeto_id in projetos_ids:
                tarefas_projeto_resp = supabase.table("tarefas").select("id, nome, status").eq("projeto_id", projeto_id).execute()
                tarefas_projeto = tarefas_projeto_resp.data if hasattr(tarefas_projeto_resp, 'data') else []
                tarefas_projetos.extend(tarefas_projeto)
                print(f"   ✅ Projeto {projeto_id}: {len(tarefas_projeto)} tarefas")
        
        # 4. Combinar e remover duplicatas
        print("\n4. Combinando tarefas...")
        todas_tarefas = tarefas_usuario + tarefas_projetos
        tarefas_unicas = {t['id']: t for t in todas_tarefas}.values()
        tarefas = list(tarefas_unicas)
        tarefas_count = len(tarefas)
        
        print(f"   ✅ Total de tarefas únicas: {tarefas_count}")
        
        # 5. Contar por status
        print("\n5. Contando por status...")
        tarefas_concluidas = len([t for t in tarefas if t.get('status') == 'concluída'])
        tarefas_pendentes = len([t for t in tarefas if t.get('status') == 'pendente'])
        tarefas_em_andamento = len([t for t in tarefas if t.get('status') == 'em progresso'])
        
        print(f"   ✅ Concluídas: {tarefas_concluidas}")
        print(f"   ✅ Pendentes: {tarefas_pendentes}")
        print(f"   ✅ Em progresso: {tarefas_em_andamento}")
        
        # 6. Verificar status únicos
        print("\n6. Status únicos encontrados:")
        status_unicos = set(t.get('status') for t in tarefas if t.get('status'))
        for status in status_unicos:
            count = len([t for t in tarefas if t.get('status') == status])
            print(f"   - '{status}': {count} tarefas")
        
        # 7. Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DO DASHBOARD - USUÁRIO FELLIPE")
        print("=" * 60)
        print(f"Projetos: {projetos_count}")
        print(f"Total de Tarefas: {tarefas_count}")
        print(f"Tarefas Concluídas: {tarefas_concluidas}")
        print(f"Tarefas Pendentes: {tarefas_pendentes}")
        print(f"Tarefas Em Progresso: {tarefas_em_andamento}")
        
        # 8. Verificar se há problemas
        print("\n🔍 DIAGNÓSTICO:")
        if tarefas_count == 0:
            print("   ❌ PROBLEMA: Nenhuma tarefa encontrada!")
        else:
            print("   ✅ Tarefas encontradas")
            
        if tarefas_em_andamento == 0 and any(t.get('status') == 'em progresso' for t in tarefas):
            print("   ❌ PROBLEMA: Tarefas 'em progresso' existem mas não estão sendo contadas!")
        elif tarefas_em_andamento > 0:
            print("   ✅ Tarefas 'em progresso' sendo contadas corretamente")
            
        if projetos_count == 0:
            print("   ⚠️  AVISO: Usuário não tem projetos próprios")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_dashboard_fellipe() 