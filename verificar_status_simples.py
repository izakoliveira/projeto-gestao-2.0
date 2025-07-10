import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def verificar_status():
    print("=== VERIFICANDO STATUS DAS TAREFAS ===\n")
    
    try:
        # Buscar todas as tarefas
        url = f"{SUPABASE_URL}/rest/v1/tarefas?select=id,nome,status"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code != 200:
            print(f"❌ Erro ao buscar tarefas: {resp.status_code}")
            return
        
        tarefas = resp.json()
        print(f"Total de tarefas encontradas: {len(tarefas)}")
        
        if not tarefas:
            print("❌ Nenhuma tarefa encontrada!")
            return
        
        # Contar status
        status_count = {}
        for tarefa in tarefas:
            status = tarefa.get('status', 'sem_status')
            if status not in status_count:
                status_count[status] = 0
            status_count[status] += 1
        
        print("\n📊 STATUS ATUAIS:")
        print("-" * 40)
        for status, count in sorted(status_count.items()):
            print(f"'{status}': {count} tarefas")
        
        # Verificar se existem tarefas com status corretos
        status_corretos = ['pendente', 'em progresso', 'concluída']
        print("\n🔍 VERIFICANDO STATUS CORRETOS:")
        print("-" * 40)
        for status in status_corretos:
            count = status_count.get(status, 0)
            if count > 0:
                print(f"✅ '{status}': {count} tarefas")
            else:
                print(f"❌ '{status}': 0 tarefas")
        
        # Mostrar algumas tarefas de exemplo
        print("\n🔍 EXEMPLOS DE TAREFAS:")
        print("-" * 40)
        for i, tarefa in enumerate(tarefas[:3]):
            print(f"{i+1}. ID: {tarefa.get('id')}")
            print(f"   Nome: {tarefa.get('nome')}")
            print(f"   Status: '{tarefa.get('status')}'")
            print()
        
        # Perguntar se quer corrigir status
        print("\n💡 SUGESTÃO:")
        print("Se não existem tarefas com os status corretos, você pode:")
        print("1. Criar algumas tarefas de teste com os status corretos")
        print("2. Ou alterar o filtro para usar os status que existem no banco")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_status() 