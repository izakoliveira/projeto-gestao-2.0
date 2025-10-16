import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"URL: {SUPABASE_URL}")
print(f"KEY: {SUPABASE_KEY[:10]}...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Conectado ao Supabase com sucesso!")
    
    # Verificar estrutura da tabela projetos
    result = supabase.table("projetos").select("*").limit(1).execute()
    if result.data:
        projeto = result.data[0]
        print("\nColunas disponiveis na tabela 'projetos':")
        for coluna in projeto.keys():
            print(f"  - {coluna}")
    else:
        print("Nenhum projeto encontrado")
        
    # Verificar estrutura da tabela tarefas
    result_tarefas = supabase.table("tarefas").select("*").limit(1).execute()
    if result_tarefas.data:
        tarefa = result_tarefas.data[0]
        print("\nColunas disponiveis na tabela 'tarefas':")
        for coluna in tarefa.keys():
            print(f"  - {coluna}")
    else:
        print("Nenhuma tarefa encontrada")
        
except Exception as e:
    print(f"Erro: {e}")