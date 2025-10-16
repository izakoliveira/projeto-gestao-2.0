#!/usr/bin/env python3

"""
INVESTIGAÇÃO: Por que as tarefas "Lançamento" dos projetos 2509 e 2606 estão sendo filtradas?
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# IDs dos projetos problemáticos
projetos_problema = {
    '2509 - WORLD SET': '8b4cd282-203c-4c2f-a13e-1e0d6b0745dc',
    '2606 - WORLD JUN': 'c658bec1-0196-4ad0-b1d9-19b418419223'
}

print("🔍 INVESTIGAÇÃO DETALHADA")
print("="*40)
print("Por que as tarefas 'Lançamento' estão sendo filtradas?")
print()

for nome_projeto, projeto_id in projetos_problema.items():
    print(f"📁 {nome_projeto} (ID: {projeto_id})")
    
    # Buscar TODAS as tarefas diretamente no banco
    todas_tarefas = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute().data
    print(f"   Total no banco: {len(todas_tarefas)} tarefas")
    
    # Encontrar especificamente as tarefas "Lançamento"
    lancamentos = [t for t in todas_tarefas if t.get('nome', '').strip().lower() == 'lançamento']
    print(f"   Lançamentos no banco: {len(lancamentos)}")
    
    for lanc in lancamentos:
        print(f"   📋 LANÇAMENTO ENCONTRADO:")
        print(f"      - ID: {lanc.get('id')}")
        print(f"      - Nome: '{lanc.get('nome')}'")
        print(f"      - Status: '{lanc.get('status')}'")
        print(f"      - Data início: {lanc.get('data_inicio')}")
        print(f"      - Projeto ID: {lanc.get('projeto_id')}")
        print(f"      - Coleção: '{lanc.get('colecao')}'")
        print(f"      - Excluída: {lanc.get('excluida', False)}")
        print(f"      - Ativa: {lanc.get('ativa', True)}")
    
    print()
    
    # Verificar se há filtros que podem estar excluindo
    print(f"   🔍 ANÁLISE DE POSSÍVEIS FILTROS:")
    
    if lancamentos:
        lanc = lancamentos[0]  # Pegar o primeiro lançamento para análise
        
        # Verificar campos que podem ser usados para filtrar
        campos_filtro = {
            'excluida': lanc.get('excluida'),
            'ativa': lanc.get('ativa'), 
            'status': lanc.get('status'),
            'colecao': lanc.get('colecao'),
            'projeto_id_match': str(lanc.get('projeto_id')) == str(projeto_id)
        }
        
        for campo, valor in campos_filtro.items():
            if campo == 'excluida' and valor:
                print(f"      ⚠️  PROBLEMA POSSÍVEL: excluida = {valor}")
            elif campo == 'ativa' and not valor:
                print(f"      ⚠️  PROBLEMA POSSÍVEL: ativa = {valor}")
            elif campo == 'projeto_id_match' and not valor:
                print(f"      ⚠️  PROBLEMA POSSÍVEL: projeto_id não confere")
            else:
                print(f"      ✅ {campo}: {valor}")
    
    print()

print("🎯 PRÓXIMOS PASSOS:")
print("Se encontrarmos que excluida=True ou ativa=False, esse é o problema!")
print("Se não, precisamos ver que outro filtro está sendo aplicado na query inicial.")