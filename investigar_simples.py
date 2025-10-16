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

# Buscar projetos problemáticos
projetos = supabase.table("projetos").select("*").execute().data
projetos_problema = {}
for projeto in projetos:
    nome = projeto.get('nome', '')
    if nome in ['2509 - WORLD SET', '2606 - WORLD JUN']:
        projetos_problema[nome] = projeto.get('id')

print("🎯 Projetos problemáticos:")
for nome, id_proj in projetos_problema.items():
    print(f"  {nome}: {id_proj}")

# Buscar TODAS as tarefas desses projetos
print(f"\n📋 Verificando tarefas dos projetos problemáticos:")

for nome, id_proj in projetos_problema.items():
    print(f"\n📁 {nome} (ID: {id_proj}):")
    
    # Buscar diretamente do banco
    tarefas = supabase.table("tarefas").select("*").eq("projeto_id", id_proj).execute().data
    print(f"  Total de tarefas no banco: {len(tarefas)}")
    
    # Buscar tarefas de lançamento
    lancamentos = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
    print(f"  Tarefas de lançamento: {len(lancamentos)}")
    
    for l in lancamentos:
        print(f"    - '{l.get('nome', '')}'")
        print(f"      Status: '{l.get('status', '')}'")
        print(f"      Coleção: '{l.get('colecao', '')}'")
        print(f"      Data: {l.get('data_inicio') or l.get('data_inicio_tarefa')}")
    
    # Verificar status de todas as tarefas
    status_counts = {}
    for t in tarefas:
        status = t.get('status', '') or 'sem status'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"  Status das tarefas:")
    for status, count in status_counts.items():
        print(f"    {status}: {count} tarefas")
    
    # Verificar coleções
    colecao_counts = {}
    for t in tarefas:
        colecao = t.get('colecao', '') or 'sem coleção'
        colecao_counts[colecao] = colecao_counts.get(colecao, 0) + 1
    
    print(f"  Coleções das tarefas:")
    for colecao, count in colecao_counts.items():
        print(f"    {colecao}: {count} tarefas")