import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis do .env
load_dotenv()

# Conecta ao Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise Exception("SUPABASE_URL ou SUPABASE_KEY não definidas no arquivo .env")

supabase: Client = create_client(url, key)

def verificar_status_tarefas():
    print("=== VERIFICANDO STATUS DAS TAREFAS ===\n")
    
    try:
        # Buscar todas as tarefas
        response = supabase.table("tarefas").select("id, nome, status, projeto_id").execute()
        tarefas = response.data
        
        print(f"Total de tarefas encontradas: {len(tarefas)}")
        
        if not tarefas:
            print("❌ Nenhuma tarefa encontrada no banco de dados!")
            return
        
        # Contar status
        status_count = {}
        for tarefa in tarefas:
            status = tarefa.get('status', 'sem_status')
            if status not in status_count:
                status_count[status] = 0
            status_count[status] += 1
        
        print("\n📊 DISTRIBUIÇÃO DE STATUS:")
        print("-" * 40)
        for status, count in sorted(status_count.items()):
            print(f"'{status}': {count} tarefas")
        
        print("\n🔍 EXEMPLOS DE TAREFAS:")
        print("-" * 40)
        for i, tarefa in enumerate(tarefas[:5]):  # Mostrar apenas as primeiras 5
            print(f"{i+1}. ID: {tarefa.get('id')}")
            print(f"   Nome: {tarefa.get('nome')}")
            print(f"   Status: '{tarefa.get('status')}'")
            print(f"   Projeto ID: {tarefa.get('projeto_id')}")
            print()
        
        # Verificar se existem tarefas com status específicos
        status_procurados = ['pendente', 'em progresso', 'concluída', 'em-progresso', 'concluida']
        print("🔎 VERIFICANDO STATUS ESPECÍFICOS:")
        print("-" * 40)
        for status_procurado in status_procurados:
            count = status_count.get(status_procurado, 0)
            if count > 0:
                print(f"✅ '{status_procurado}': {count} tarefas")
            else:
                print(f"❌ '{status_procurado}': 0 tarefas")
        
    except Exception as e:
        print(f"❌ Erro ao buscar tarefas: {e}")

if __name__ == "__main__":
    verificar_status_tarefas() 