import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ID do projeto 2602 - WORLD FEV
projeto_id = '27194dde-57c2-46fd-9af6-01aa715b4b44'

# Buscar todas as tarefas "Lançamento" desse projeto
response = supabase.table('tarefas').select('*').eq('projeto_id', projeto_id).eq('nome', 'Lançamento').execute()

tarefas = response.data or []
print(f"Tarefas 'Lançamento' do projeto {projeto_id}:")
for t in tarefas:
    print(f"ID: {t.get('id')} | Nome: {t.get('nome')} | projeto_id: {t.get('projeto_id')} | data_inicio: {t.get('data_inicio')} | status: {t.get('status')}")

if not tarefas:
    print("Nenhuma tarefa 'Lançamento' encontrada para este projeto.")
