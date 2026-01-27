
# Conferência de tarefas "Lançamento" usando variáveis do .env
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalizar_nome(nome):
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')


def listar_lancamentos():
    tarefas = supabase.table('tarefas').select('*').execute().data
    projetos = supabase.table('projetos').select('id, nome').execute().data
    projetos_ids = set(p['id'] for p in projetos)
    lancamentos = [t for t in tarefas if normalizar_nome(t.get('nome', '')) == 'lancamento']

    print(f"Total de tarefas encontradas: {len(tarefas)}")
    print(f"Total de tarefas 'Lançamento': {len(lancamentos)}")
    print(f"Total de projetos: {len(projetos)}\n")

    # Relatório: tarefas 'Lançamento' por projeto
    print("--- Tarefas 'Lançamento' por projeto ---")
    projetos_lanc = {}
    for t in lancamentos:
        pid = t.get('projeto_id', '')
        projetos_lanc.setdefault(pid, []).append(t)
    for pid, tarefas in projetos_lanc.items():
        nome_proj = next((p['nome'] for p in projetos if p['id'] == pid), '(Projeto não encontrado)')
        print(f"Projeto: {pid} | Nome: {nome_proj} | Qtde tarefas 'Lançamento': {len(tarefas)}")
        for t in tarefas:
            print(f"   - Tarefa ID: {t.get('id', '')} | Nome: {t.get('nome', '')}")

    # Projetos com mais de uma tarefa 'Lançamento'
    print("\n--- Projetos com MAIS de uma tarefa 'Lançamento' ---")
    for pid, tarefas in projetos_lanc.items():
        if len(tarefas) > 1:
            nome_proj = next((p['nome'] for p in projetos if p['id'] == pid), '(Projeto não encontrado)')
            print(f"Projeto: {pid} | Nome: {nome_proj} | Qtde: {len(tarefas)}")

    # Tarefas 'Lançamento' associadas a projetos inexistentes
    print("\n--- Tarefas 'Lançamento' associadas a projetos inexistentes ---")
    for pid, tarefas in projetos_lanc.items():
        if pid not in projetos_ids:
            for t in tarefas:
                print(f"Tarefa ID: {t.get('id', '')} | Projeto: {pid} | Nome: {t.get('nome', '')}")

if __name__ == "__main__":
    listar_lancamentos()
