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

def restaurar_teste_tecnico():
    print("=== RESTAURANDO TAREFAS 'TESTE TÉCNICO' ===\n")
    
    try:
        # Buscar um projeto existente para associar as tarefas
        url_projetos = f"{SUPABASE_URL}/rest/v1/projetos?select=id,nome&limit=1"
        resp_projetos = requests.get(url_projetos, headers=headers)
        
        if resp_projetos.status_code != 200 or not resp_projetos.json():
            print("❌ Nenhum projeto encontrado!")
            return
        
        projeto = resp_projetos.json()[0]
        projeto_id = projeto['id']
        print(f"📋 Usando projeto: {projeto['nome']} (ID: {projeto_id})")
        
        # Buscar a maior ordem atual para continuar a numeração
        url_ordem = f"{SUPABASE_URL}/rest/v1/tarefas?projeto_id=eq.{projeto_id}&select=ordem&order=ordem.desc&limit=1"
        resp_ordem = requests.get(url_ordem, headers=headers)
        maior_ordem = 0
        if resp_ordem.status_code == 200 and resp_ordem.json():
            maior_ordem = resp_ordem.json()[0].get('ordem') or 0
        
        # Tarefas "Teste técnico" para restaurar
        tarefas_teste_tecnico = [
            {
                "nome": "Teste técnico",
                "descricao": "Teste técnico do projeto",
                "data_inicio": "2025-01-10",
                "data_fim": "2025-01-20"
            },
            {
                "nome": "Teste técnico",
                "descricao": "Teste técnico do projeto",
                "data_inicio": "2025-01-15",
                "data_fim": "2025-01-25"
            },
            {
                "nome": "Teste técnico",
                "descricao": "Teste técnico do projeto",
                "data_inicio": "2025-01-20",
                "data_fim": "2025-01-30"
            },
            {
                "nome": "Teste técnico",
                "descricao": "Teste técnico do projeto",
                "data_inicio": "2025-02-01",
                "data_fim": "2025-02-10"
            },
            {
                "nome": "Teste técnico",
                "descricao": "Teste técnico do projeto",
                "data_inicio": "2025-02-05",
                "data_fim": "2025-02-15"
            }
        ]
        
        # Criar as tarefas
        url_tarefas = f"{SUPABASE_URL}/rest/v1/tarefas"
        criadas = 0
        
        for i, tarefa in enumerate(tarefas_teste_tecnico):
            dados = {
                "id": str(uuid.uuid4()),
                "nome": tarefa["nome"],
                "descricao": tarefa["descricao"],
                "status": "pendente",
                "data_inicio": tarefa["data_inicio"],
                "data_fim": tarefa["data_fim"],
                "projeto_id": projeto_id,
                "ordem": maior_ordem + i + 1
            }
            
            resp = requests.post(url_tarefas, headers=headers, json=dados)
            
            if resp.status_code in [200, 201]:
                print(f"✅ Restaurada: {tarefa['nome']} (Ordem: {dados['ordem']})")
                criadas += 1
            else:
                print(f"❌ Erro ao restaurar {tarefa['nome']}: {resp.status_code}")
        
        print(f"\n🎉 {criadas} tarefas 'Teste técnico' restauradas com sucesso!")
        print("\n💡 Agora você tem suas tarefas originais de volta!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    restaurar_teste_tecnico() 