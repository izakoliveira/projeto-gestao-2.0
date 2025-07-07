import requests
import json

SUPABASE_URL = "https://zvdpuxggltqejplybzet.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def testar_insercao_tarefa():
    """Testa a inserção de uma tarefa real"""
    print("=== Testando inserção de tarefa ===")
    
    # Primeiro, buscar um projeto existente
    url_projetos = f"{SUPABASE_URL}/rest/v1/projetos?select=id&limit=1"
    resp_projetos = requests.get(url_projetos, headers=headers)
    print(f"Status busca projetos: {resp_projetos.status_code}")
    
    if resp_projetos.status_code == 200 and resp_projetos.json():
        projeto_id = resp_projetos.json()[0]['id']
        print(f"Projeto encontrado: {projeto_id}")
        
        # Buscar um usuário existente
        url_usuarios = f"{SUPABASE_URL}/rest/v1/usuarios?select=id&limit=1"
        resp_usuarios = requests.get(url_usuarios, headers=headers)
        print(f"Status busca usuários: {resp_usuarios.status_code}")
        
        if resp_usuarios.status_code == 200 and resp_usuarios.json():
            usuario_id = resp_usuarios.json()[0]['id']
            print(f"Usuário encontrado: {usuario_id}")
            
            # Tentar inserir uma tarefa
            tarefa = {
                "nome": "Tarefa de Teste",
                "descricao": "Descrição da tarefa de teste",
                "data_inicio": "2024-01-01",
                "data_fim": "2024-01-31",
                "status": "pendente",
                "projeto_id": projeto_id,
                "usuario_id": usuario_id
            }
            
            print(f"Dados da tarefa: {tarefa}")
            
            url_insert = f"{SUPABASE_URL}/rest/v1/tarefas"
            resp_insert = requests.post(url_insert, headers=headers, json=tarefa)
            print(f"Teste de inserção real: {resp_insert.status_code}")
            print(f"Resposta: {resp_insert.text}")
            
            if resp_insert.status_code == 201:
                print("✅ Inserção bem-sucedida!")
                # Deletar a tarefa de teste
                tarefa_id = resp_insert.json()[0]['id']
                url_delete = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
                resp_delete = requests.delete(url_delete, headers=headers)
                print(f"Tarefa de teste removida: {resp_delete.status_code}")
            else:
                print("❌ Falha na inserção")
        else:
            print("❌ Nenhum usuário encontrado")
            print(f"Resposta: {resp_usuarios.text}")
    else:
        print("❌ Nenhum projeto encontrado")
        print(f"Resposta: {resp_projetos.text}")

def verificar_estrutura_tarefas():
    """Verifica a estrutura da tabela tarefas"""
    print("=== Verificando estrutura da tabela tarefas ===")
    
    url = f"{SUPABASE_URL}/rest/v1/tarefas?select=*&limit=1"
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("✅ Tabela tarefas acessível")
        if resp.json():
            print(f"Estrutura: {list(resp.json()[0].keys())}")
        else:
            print("Tabela vazia")
    else:
        print(f"❌ Erro: {resp.text}")

if __name__ == "__main__":
    verificar_estrutura_tarefas()
    testar_insercao_tarefa()

url = "https://zvdpuxggltqejplybzet.supabase.co/rest/v1/tarefas"
headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI",
    "Content-Type": "application/json"
}
data = {
    "nome": "Teste via Python",
    "descricao": "",
    "data_inicio": "2025-06-26",
    "data_fim": "2025-06-26",
    "status": "pendente",
    "projeto_id": "0f101b88-a90c-4020-8cab-81c445310dc9",
    "usuario_id": "6afb28b7-2c10-4f9b-a0d5-c9ce27600521"
}

response = requests.post(url, headers=headers, json=data)
print('Status code:', response.status_code)
print('Resposta:', response.text)