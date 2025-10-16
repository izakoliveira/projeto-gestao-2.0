#!/usr/bin/env python3

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

def normalizar(nome):
    if not nome:
        return ''
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')

print("🔍 TESTE DIRETO NO BANCO")
print("="*30)

for nome, projeto_id in projetos_problema.items():
    print(f"\n📁 {nome}:")
    
    # Busca direta no banco
    tarefas = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute().data
    print(f"  Total no banco: {len(tarefas)}")
    
    # Buscar lançamentos
    lancamentos = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
    print(f"  Lançamentos: {len(lancamentos)}")
    
    for l in lancamentos:
        print(f"    - {l.get('nome')} | Status: {l.get('status')} | Data: {l.get('data_inicio')}")
    
    # Teste de filtros comuns
    print(f"  Testes de filtro:")
    
    # Filtro por status comum
    for status_teste in ['em andamento', 'ativo', 'pendente']:
        filtradas = [
            t for t in tarefas 
            if t.get('status') == status_teste or normalizar(t.get('nome', '')) == 'lancamento'
        ]
        print(f"    Status '{status_teste}' + lançamento: {len(filtradas)} tarefas")
        if len(filtradas) < 15:
            print(f"      ⚠️  Poucas tarefas! Este pode ser o filtro problemático")

print(f"\n💡 HIPÓTESE:")
print(f"A URL /projetos está sendo acessada com parâmetros de filtro que não incluem")
print(f"os status das tarefas desses projetos, deixando apenas o lançamento passar.")
print(f"Mas nossa correção da função normalizar() deveria resolver isso...")