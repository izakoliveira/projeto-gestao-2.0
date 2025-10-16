#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import supabase_client
import requests

SUPABASE_URL = supabase_client.SUPABASE_URL
headers = supabase_client.headers

# Verificar se o projeto específico existe
projeto_id = "2ead78b0-b1c0-4d1b-9dc2-1d822a2c501f"
resp = requests.get(f'{SUPABASE_URL}/rest/v1/projetos?id=eq.{projeto_id}', headers=headers)

print(f'Status: {resp.status_code}')
print(f'Projeto encontrado: {len(resp.json()) > 0}')

if resp.json():
    projeto = resp.json()[0]
    print(f'Nome: {projeto["nome"]}')
    print(f'Descrição: {projeto.get("descricao", "N/A")}')
    print(f'Data início: {projeto.get("data_inicio", "N/A")}')
    print(f'Data fim: {projeto.get("data_fim", "N/A")}')
    print(f'Usuário: {projeto.get("usuario_id", "N/A")}')
else:
    print("❌ Projeto NÃO encontrado no banco de dados")