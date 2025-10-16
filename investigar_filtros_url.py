#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalizar(nome):
    if not nome:
        return ''
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')

print("🕵️ INVESTIGAÇÃO DETALHADA DOS FILTROS")
print("="*50)

# Buscar projetos e IDs problemáticos
projetos = supabase.table("projetos").select("*").execute().data
projeto_ids = [projeto['id'] for projeto in projetos]

projetos_problema = {}
for projeto in projetos:
    nome = projeto.get('nome', '')
    if nome in ['2509 - WORLD SET', '2606 - WORLD JUN']:
        projetos_problema[nome] = projeto.get('id')

print(f"📋 Total de projetos: {len(projetos)}")
print(f"🎯 Projetos problemáticos: {list(projetos_problema.keys())}")

# CENÁRIO 1: Buscar SEM filtros (como deveria funcionar)
print(f"\n🔍 CENÁRIO 1: Buscar tarefas SEM filtros")
tarefas_sem_filtro = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute().data or []
print(f"Total de tarefas encontradas: {len(tarefas_sem_filtro)}")

for nome, id_proj in projetos_problema.items():
    tarefas_do_projeto = [t for t in tarefas_sem_filtro if t.get('projeto_id') == id_proj]
    lancamentos = [t for t in tarefas_do_projeto if normalizar(t.get('nome', '')) == 'lancamento']
    print(f"  {nome}: {len(tarefas_do_projeto)} tarefas, {len(lancamentos)} lançamentos")

# CENÁRIO 2: Simular filtros que podem estar vindo da URL
print(f"\n🔍 CENÁRIO 2: Simulando possíveis filtros da URL")

# Possíveis filtros que podem estar na URL
filtros_possiveis = [
    {'status': ['em andamento']},
    {'status': ['pendente']},
    {'status': ['ativo']},
    {'status': ['em progresso']},
    {'colecao': ['alguma colecao']},
    {'status': ['pendente'], 'colecao': ['2606 - WORLD JUN']},
]

for filtro in filtros_possiveis:
    print(f"\n  🧪 Testando filtro: {filtro}")
    
    # Simular busca por projeto (como no código original)
    tarefas_filtradas = []
    for projeto_id in projeto_ids:
        tarefas_projeto = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute()
        if hasattr(tarefas_projeto, 'data') and tarefas_projeto.data:
            tarefas_filtradas.extend(tarefas_projeto.data)
    
    print(f"    Total tarefas ANTES dos filtros: {len(tarefas_filtradas)}")
    
    # Aplicar filtro de status
    if 'status' in filtro:
        status_list = filtro['status']
        tarefas_antes = len(tarefas_filtradas)
        tarefas_filtradas = [
            t for t in tarefas_filtradas
            if t.get('status') in status_list or normalizar(t.get('nome', '')) == 'lancamento'
        ]
        print(f"    Após filtro STATUS {status_list}: {tarefas_antes} -> {len(tarefas_filtradas)} tarefas")
    
    # Aplicar filtro de coleção
    if 'colecao' in filtro:
        colecao_list = filtro['colecao']
        tarefas_antes = len(tarefas_filtradas)
        tarefas_filtradas = [t for t in tarefas_filtradas if t.get('colecao') in colecao_list]
        print(f"    Após filtro COLEÇÃO {colecao_list}: {tarefas_antes} -> {len(tarefas_filtradas)} tarefas")
    
    # Verificar projetos problemáticos após filtros
    for nome, id_proj in projetos_problema.items():
        tarefas_do_projeto = [t for t in tarefas_filtradas if t.get('projeto_id') == id_proj]
        lancamentos = [t for t in tarefas_do_projeto if normalizar(t.get('nome', '')) == 'lancamento']
        if len(tarefas_do_projeto) < 15:  # Se perdeu muitas tarefas
            print(f"    ⚠️  {nome}: {len(tarefas_do_projeto)} tarefas ({len(lancamentos)} lançamentos)")
            if len(tarefas_do_projeto) > 0:
                print(f"        Tarefas restantes: {[t.get('nome', '')[:20] + '...' if len(t.get('nome', '')) > 20 else t.get('nome', '') for t in tarefas_do_projeto]}")

print(f"\n💡 CONCLUSÃO:")
print(f"Se algum filtro acima resulta em poucas tarefas para os projetos problemáticos,")
print(f"esse é provavelmente o filtro que está sendo aplicado na URL da aplicação.")