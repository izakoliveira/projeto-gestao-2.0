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

def testar_dashboard_corrigido():
    """Testa o dashboard com as correções aplicadas"""
    
    # ID do usuário Fellipe
    user_id = "6afb28b7-2c10-4f9b-a0d5-c9ce27600521"
    
    print(f"🔍 Testando dashboard CORRIGIDO para usuário Fellipe (ID: {user_id})")
    print("=" * 70)
    
    try:
        # 1. Buscar projetos próprios do usuário
        print("1. Buscando projetos próprios...")
        projetos_resp = supabase.table("projetos").select("id").eq("usuario_id", user_id).execute()
        projetos_proprios = projetos_resp.data if hasattr(projetos_resp, 'data') else []
        projetos_proprios_ids = [p['id'] for p in projetos_proprios]
        
        print(f"   ✅ Projetos próprios: {len(projetos_proprios_ids)}")
        for projeto_id in projetos_proprios_ids:
            print(f"      - {projeto_id}")
        
        # 2. Buscar projetos compartilhados (permissões de visualização)
        print("\n2. Buscando projetos compartilhados...")
        try:
            permissoes_resp = supabase.table("projetos_usuarios_visiveis").select("projeto_id").eq("usuario_id", user_id).execute()
            permissoes = permissoes_resp.data if hasattr(permissoes_resp, 'data') else []
            projetos_compartilhados_ids = [p['projeto_id'] for p in permissoes]
        except Exception as e:
            print(f"   ❌ Erro ao buscar permissões: {str(e)}")
            projetos_compartilhados_ids = []
        
        print(f"   ✅ Projetos compartilhados: {len(projetos_compartilhados_ids)}")
        for projeto_id in projetos_compartilhados_ids:
            print(f"      - {projeto_id}")
        
        # 3. Combinar todos os projetos acessíveis
        print("\n3. Combinando projetos acessíveis...")
        todos_projetos_ids = projetos_proprios_ids + projetos_compartilhados_ids
        projetos_count = len(todos_projetos_ids)
        
        print(f"   ✅ Total de projetos acessíveis: {projetos_count}")
        print(f"      - Próprios: {len(projetos_proprios_ids)}")
        print(f"      - Compartilhados: {len(projetos_compartilhados_ids)}")
        
        # 4. Buscar tarefas do usuário
        print("\n4. Buscando tarefas do usuário...")
        tarefas_usuario_resp = supabase.table("tarefas").select("id, nome, status").eq("usuario_id", user_id).execute()
        tarefas_usuario = tarefas_usuario_resp.data if hasattr(tarefas_usuario_resp, 'data') else []
        
        print(f"   ✅ Tarefas do usuário: {len(tarefas_usuario)}")
        for tarefa in tarefas_usuario:
            print(f"      - {tarefa['nome']} (Status: {tarefa.get('status', 'N/A')})")
        
        # 5. Buscar tarefas dos projetos acessíveis
        print("\n5. Buscando tarefas dos projetos acessíveis...")
        tarefas_projetos = []
        if todos_projetos_ids:
            for projeto_id in todos_projetos_ids:
                tarefas_projeto_resp = supabase.table("tarefas").select("id, nome, status").eq("projeto_id", projeto_id).execute()
                tarefas_projeto = tarefas_projeto_resp.data if hasattr(tarefas_projeto_resp, 'data') else []
                tarefas_projetos.extend(tarefas_projeto)
                print(f"   ✅ Projeto {projeto_id}: {len(tarefas_projeto)} tarefas")
        
        # 6. Combinar e remover duplicatas
        print("\n6. Combinando tarefas...")
        todas_tarefas = tarefas_usuario + tarefas_projetos
        tarefas_unicas = {t['id']: t for t in todas_tarefas}.values()
        tarefas = list(tarefas_unicas)
        tarefas_count = len(tarefas)
        
        print(f"   ✅ Total de tarefas únicas: {tarefas_count}")
        
        # 7. Contar por status
        print("\n7. Contando por status...")
        tarefas_concluidas = len([t for t in tarefas if t.get('status') == 'concluída'])
        tarefas_pendentes = len([t for t in tarefas if t.get('status') == 'pendente'])
        tarefas_em_andamento = len([t for t in tarefas if t.get('status') == 'em progresso'])
        
        print(f"   ✅ Concluídas: {tarefas_concluidas}")
        print(f"   ✅ Pendentes: {tarefas_pendentes}")
        print(f"   ✅ Em progresso: {tarefas_em_andamento}")
        
        # 8. Verificar status únicos
        print("\n8. Status únicos encontrados:")
        status_unicos = set(t.get('status') for t in tarefas if t.get('status'))
        for status in status_unicos:
            count = len([t for t in tarefas if t.get('status') == status])
            print(f"   - '{status}': {count} tarefas")
        
        # 9. Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO DO DASHBOARD CORRIGIDO - USUÁRIO FELLIPE")
        print("=" * 70)
        print(f"Projetos Próprios: {len(projetos_proprios_ids)}")
        print(f"Projetos Compartilhados: {len(projetos_compartilhados_ids)}")
        print(f"Total de Projetos: {projetos_count}")
        print(f"Total de Tarefas: {tarefas_count}")
        print(f"Tarefas Concluídas: {tarefas_concluidas}")
        print(f"Tarefas Pendentes: {tarefas_pendentes}")
        print(f"Tarefas Em Progresso: {tarefas_em_andamento}")
        
        # 10. Verificar se há problemas
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
            print("   ❌ PROBLEMA: Usuário não tem projetos acessíveis!")
        else:
            print("   ✅ Projetos acessíveis encontrados")
            
        if len(projetos_compartilhados_ids) > 0:
            print("   ✅ Projetos compartilhados incluídos no dashboard")
        else:
            print("   ⚠️  AVISO: Nenhum projeto compartilhado encontrado")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_dashboard_corrigido() 