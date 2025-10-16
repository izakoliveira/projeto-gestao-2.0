#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import supabase_client
import requests

SUPABASE_URL = supabase_client.SUPABASE_URL
headers = supabase_client.headers

# Verificar tarefas
resp = requests.get(f'{SUPABASE_URL}/rest/v1/tarefas?select=id,nome', headers=headers)
tarefas = resp.json()
print(f'Total de tarefas: {len(tarefas)}')

if tarefas:
    print('Primeiras 5 tarefas:')
    for t in tarefas[:5]:
        print(f'  - {t["nome"]}')
else:
    print('❌ Nenhuma tarefa encontrada!')

# Verificar projetos  
resp_proj = requests.get(f'{SUPABASE_URL}/rest/v1/projetos?select=id,nome', headers=headers)
projetos = resp_proj.json()
print(f'Total de projetos: {len(projetos)}')