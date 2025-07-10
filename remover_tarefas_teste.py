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

def remover_tarefas_teste():
    print("=== REMOVENDO TAREFAS DE TESTE ===\n")
    
    try:
        # Buscar tarefas que contêm "Teste" no nome
        url_busca = f"{SUPABASE_URL}/rest/v1/tarefas?select=id,nome,status&nome=ilike.*Teste*"
        resp = requests.get(url_busca, headers=headers)
        
        if resp.status_code != 200:
            print(f"❌ Erro ao buscar tarefas: {resp.status_code}")
            return
        
        tarefas_teste = resp.json()
        print(f"Encontradas {len(tarefas_teste)} tarefas de teste:")
        
        if not tarefas_teste:
            print("✅ Nenhuma tarefa de teste encontrada!")
            return
        
        # Mostrar tarefas que serão removidas
        for i, tarefa in enumerate(tarefas_teste):
            print(f"{i+1}. {tarefa['nome']} (Status: {tarefa['status']})")
        
        # Confirmar remoção
        print(f"\n⚠️  ATENÇÃO: {len(tarefas_teste)} tarefas serão removidas permanentemente!")
        confirmacao = input("\nDigite 'SIM' para confirmar a remoção: ")
        
        if confirmacao.upper() != 'SIM':
            print("❌ Remoção cancelada pelo usuário.")
            return
        
        # Remover as tarefas
        removidas = 0
        for tarefa in tarefas_teste:
            url_delete = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa['id']}"
            resp_delete = requests.delete(url_delete, headers=headers)
            
            if resp_delete.status_code in [200, 204]:
                print(f"✅ Removida: {tarefa['nome']}")
                removidas += 1
            else:
                print(f"❌ Erro ao remover {tarefa['nome']}: {resp_delete.status_code}")
        
        print(f"\n🎉 {removidas} tarefas de teste removidas com sucesso!")
        
        # Verificar status atual
        print("\n📊 STATUS ATUAL:")
        url_status = f"{SUPABASE_URL}/rest/v1/tarefas?select=status"
        resp_status = requests.get(url_status, headers=headers)
        
        if resp_status.status_code == 200:
            tarefas = resp_status.json()
            status_count = {}
            for t in tarefas:
                status = t.get('status', 'sem_status')
                status_count[status] = status_count.get(status, 0) + 1
            
            for status, count in sorted(status_count.items()):
                print(f"'{status}': {count} tarefas")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    remover_tarefas_teste() 