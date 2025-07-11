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

def verificar_colecoes():
    print("=== VERIFICANDO COLECÕES DAS TAREFAS ===\n")
    
    try:
        # Buscar todas as tarefas com campo colecao
        url = f"{SUPABASE_URL}/rest/v1/tarefas?select=id,nome,colecao"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code != 200:
            print(f"❌ Erro ao buscar tarefas: {resp.status_code}")
            return
        
        tarefas = resp.json()
        print(f"Total de tarefas encontradas: {len(tarefas)}")
        
        if not tarefas:
            print("❌ Nenhuma tarefa encontrada!")
            return
        
        # Contar coleções
        colecao_count = {}
        tarefas_sem_colecao = 0
        
        for tarefa in tarefas:
            colecao = tarefa.get('colecao')
            if colecao and colecao.strip():
                if colecao not in colecao_count:
                    colecao_count[colecao] = 0
                colecao_count[colecao] += 1
            else:
                tarefas_sem_colecao += 1
        
        print(f"\n📊 DISTRIBUIÇÃO DE COLECÕES:")
        print("-" * 40)
        if colecao_count:
            for colecao, count in sorted(colecao_count.items()):
                print(f"'{colecao}': {count} tarefas")
        else:
            print("❌ Nenhuma coleção encontrada!")
        
        print(f"\n📋 TAREFAS SEM COLECÃO: {tarefas_sem_colecao}")
        
        # Mostrar algumas tarefas de exemplo
        print("\n🔍 EXEMPLOS DE TAREFAS:")
        print("-" * 40)
        for i, tarefa in enumerate(tarefas[:5]):
            print(f"{i+1}. ID: {tarefa.get('id')}")
            print(f"   Nome: {tarefa.get('nome')}")
            print(f"   Coleção: '{tarefa.get('colecao')}'")
            print()
        
        # Verificar se o campo colecao existe na tabela
        print("🔍 VERIFICANDO ESTRUTURA DA TABELA:")
        print("-" * 40)
        
        # Tentar buscar apenas o campo colecao
        url_colecao = f"{SUPABASE_URL}/rest/v1/tarefas?select=colecao&limit=1"
        resp_colecao = requests.get(url_colecao, headers=headers)
        
        if resp_colecao.status_code == 200:
            print("✅ Campo 'colecao' existe na tabela tarefas")
        else:
            print("❌ Campo 'colecao' não existe na tabela tarefas")
            print(f"   Erro: {resp_colecao.status_code}")
        
        # Sugestões
        print("\n💡 SUGESTÕES:")
        if not colecao_count:
            print("1. Adicionar valores de coleção às tarefas existentes")
            print("2. Ou criar algumas tarefas de teste com coleções")
            print("3. Ou remover o filtro de coleção se não for necessário")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_colecoes() 