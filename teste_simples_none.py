#!/usr/bin/env python3
"""
Script simples para testar o problema do None
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalizar(nome):
    if not nome:
        return ''
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')

# Buscar dados
projetos = supabase.table("projetos").select("*").execute().data
projeto_ids = [projeto['id'] for projeto in projetos]
tarefas_filtradas = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute().data

# Associar tarefas
for projeto in projetos:
    pid = projeto.get('id')
    tarefas_associadas = []
    for tarefa in tarefas_filtradas:
        tid = tarefa.get('projeto_id')
        if str(tid).strip() == str(pid).strip():
            tarefas_associadas.append(tarefa)
    projeto['tarefas'] = tarefas_associadas

# Testar apenas os 2 projetos problemáticos
projetos_problema = ['2509 - WORLD SET', '2606 - WORLD JUN']

print("🔍 TESTE DOS PROJETOS PROBLEMÁTICOS:")
for projeto in projetos:
    nome_projeto = projeto.get('nome', 'Sem nome')
    if nome_projeto not in projetos_problema:
        continue
    
    print(f"\n📁 {nome_projeto}:")
    print(f"   Total tarefas: {len(projeto.get('tarefas', []))}")
    
    # Simular o código da aplicação
    data_lanc = None
    for t in projeto.get('tarefas', []):
        nome_tarefa = t.get('nome', '')
        nome_normalizado = normalizar(nome_tarefa)
        if nome_normalizado == 'lancamento':
            data_inicio = t.get('data_inicio')
            data_inicio_tarefa = t.get('data_inicio_tarefa')
            data_lanc = data_inicio or data_inicio_tarefa
            print(f"   ✅ Encontrou lançamento: '{nome_tarefa}'")
            print(f"      data_inicio: {data_inicio}")
            print(f"      data_inicio_tarefa: {data_inicio_tarefa}")
            print(f"      data_final: {data_lanc}")
            break
    
    if data_lanc is None:
        print(f"   ❌ Não encontrou lançamento")
        print(f"   📝 Tarefas disponíveis:")
        for t in projeto.get('tarefas', []):
            nome = t.get('nome', '')
            nome_norm = normalizar(nome)
            print(f"      - '{nome}' | Normalizada: '{nome_norm}'")
    
    print(f"   🎯 Resultado final: {data_lanc}")