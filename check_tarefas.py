import sys
sys.path.append('.')
from config.database import supabase
tarefas = supabase.table('tarefas').select('nome, status, data_fim, projeto_id').limit(20).execute()
for t in tarefas.data:
    print(f'Tarefa: {t.get("nome", "")} | Status: {t.get("status", "")} | Data fim: {t.get("data_fim", "")} | Projeto: {t.get("projeto_id", "")}')