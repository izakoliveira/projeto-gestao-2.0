#!/usr/bin/env python3

"""
TESTE ESPECÍFICO: Comparar query exata usada na aplicação vs query direta
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# IDs dos projetos
projeto_2509 = '8b4cd282-203c-4c2f-a13e-1e0d6b0745dc'
projeto_2606 = 'c658bec1-0196-4ad0-b1d9-19b418419223'
projeto_ids = [projeto_2509, projeto_2606]

print("🧪 TESTE DE QUERY EXATA")
print("="*30)

# Testar a query exata usada na aplicação
print("1️⃣ Query exata da aplicação (sem filtros):")
try:
    # Esta é a query EXATA usada na aplicação quando não há filtros
    resultado_app = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute()
    tarefas_app = resultado_app.data or []
    print(f"   Total de tarefas retornadas: {len(tarefas_app)}")
    
    # Contar por projeto
    count_2509 = len([t for t in tarefas_app if t.get('projeto_id') == projeto_2509])
    count_2606 = len([t for t in tarefas_app if t.get('projeto_id') == projeto_2606])
    
    print(f"   Projeto 2509: {count_2509} tarefas")
    print(f"   Projeto 2606: {count_2606} tarefas")
    
    # Buscar lançamentos
    lancamentos_2509 = [t for t in tarefas_app if t.get('projeto_id') == projeto_2509 and t.get('nome', '').strip().lower() == 'lançamento']
    lancamentos_2606 = [t for t in tarefas_app if t.get('projeto_id') == projeto_2606 and t.get('nome', '').strip().lower() == 'lançamento']
    
    print(f"   Lançamentos 2509: {len(lancamentos_2509)}")
    print(f"   Lançamentos 2606: {len(lancamentos_2606)}")
    
except Exception as e:
    print(f"   Erro: {e}")

print()
print("2️⃣ Query individual por projeto:")
for projeto_id in projeto_ids:
    try:
        resultado_individual = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute()
        tarefas_individual = resultado_individual.data or []
        nome_projeto = "2509" if projeto_id == projeto_2509 else "2606"
        
        print(f"   Projeto {nome_projeto}: {len(tarefas_individual)} tarefas")
        
        # Buscar lançamento
        lancamento = [t for t in tarefas_individual if t.get('nome', '').strip().lower() == 'lançamento']
        print(f"   Lançamentos {nome_projeto}: {len(lancamento)}")
        
        if lancamento:
            l = lancamento[0]
            print(f"      - Nome: '{l.get('nome')}'")
            print(f"      - Status: {l.get('status')}")
            print(f"      - Ativa: {l.get('ativa')}")
            print(f"      - Excluída: {l.get('excluida')}")
            
    except Exception as e:
        print(f"   Erro projeto {nome_projeto}: {e}")

print()
print("3️⃣ Verificação de filtros RLS/políticas:")
print("   Se as queries individuais retornam 19 tarefas com lançamento,")
print("   mas a query .in_() retorna menos, pode ser:")
print("   - Problema de RLS (Row Level Security) no Supabase") 
print("   - Limite de resultados na query .in_()")
print("   - Algum filtro sendo aplicado automaticamente")