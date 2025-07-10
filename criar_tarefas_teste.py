import os
import requests
import uuid
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

def criar_tarefas_teste():
    print("=== CRIANDO TAREFAS DE TESTE ===\n")
    
    try:
        # Primeiro, buscar um projeto existente
        url_projetos = f"{SUPABASE_URL}/rest/v1/projetos?select=id,nome&limit=1"
        resp_projetos = requests.get(url_projetos, headers=headers)
        
        if resp_projetos.status_code != 200 or not resp_projetos.json():
            print("❌ Nenhum projeto encontrado. Crie um projeto primeiro!")
            return
        
        projeto = resp_projetos.json()[0]
        projeto_id = projeto['id']
        print(f"📋 Usando projeto: {projeto['nome']} (ID: {projeto_id})")
        
        # Tarefas de teste
        tarefas_teste = [
            {
                "nome": "Tarefa em Progresso - Teste",
                "status": "em progresso",
                "data_inicio": "2025-01-15",
                "data_fim": "2025-01-30"
            },
            {
                "nome": "Tarefa Concluída - Teste",
                "status": "concluída", 
                "data_inicio": "2025-01-01",
                "data_fim": "2025-01-14"
            },
            {
                "nome": "Outra Tarefa em Progresso",
                "status": "em progresso",
                "data_inicio": "2025-02-01",
                "data_fim": "2025-02-15"
            }
        ]
        
        # Criar as tarefas
        url_tarefas = f"{SUPABASE_URL}/rest/v1/tarefas"
        criadas = 0
        
        for tarefa in tarefas_teste:
            dados = {
                "id": str(uuid.uuid4()),
                "nome": tarefa["nome"],
                "status": tarefa["status"],
                "data_inicio": tarefa["data_inicio"],
                "data_fim": tarefa["data_fim"],
                "projeto_id": projeto_id,
                "descricao": f"Tarefa de teste para status '{tarefa['status']}'",
                "ordem": 999  # Para ficar no final
            }
            
            resp = requests.post(url_tarefas, headers=headers, json=dados)
            
            if resp.status_code in [200, 201]:
                print(f"✅ Criada: {tarefa['nome']} (Status: {tarefa['status']})")
                criadas += 1
            else:
                print(f"❌ Erro ao criar {tarefa['nome']}: {resp.status_code}")
        
        print(f"\n🎉 {criadas} tarefas de teste criadas com sucesso!")
        print("\n💡 Agora você pode testar o filtro de status:")
        print("   - 'em progresso' deve mostrar 2 tarefas")
        print("   - 'concluída' deve mostrar 1 tarefa")
        print("   - 'pendente' deve mostrar todas as tarefas originais")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    criar_tarefas_teste() 