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

def limpar_colecoes():
    print("=== LIMPANDO DADOS DAS COLECÕES ===\n")
    
    try:
        # Buscar todas as tarefas com coleção
        url = f"{SUPABASE_URL}/rest/v1/tarefas?select=id,nome,colecao&colecao=not.is.null"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code != 200:
            print(f"❌ Erro ao buscar tarefas: {resp.status_code}")
            return
        
        tarefas = resp.json()
        print(f"Tarefas com coleção encontradas: {len(tarefas)}")
        
        if not tarefas:
            print("❌ Nenhuma tarefa com coleção encontrada!")
            return
        
        # Mostrar coleções antes da limpeza
        print("\n📊 COLECÕES ANTES DA LIMPEZA:")
        print("-" * 40)
        colecoes_antes = set()
        for tarefa in tarefas:
            colecao = tarefa.get('colecao', '')
            if colecao:
                colecoes_antes.add(repr(colecao))  # repr() mostra caracteres especiais
        
        for colecao in sorted(colecoes_antes):
            print(f"'{colecao}'")
        
        # Função para limpar coleção
        def limpar_colecao(colecao):
            if not colecao:
                return colecao
            # Remover quebras de linha, espaços extras e caracteres especiais
            limpa = colecao.replace('\n', '').replace('\r', '').strip()
            return limpa
        
        # Atualizar coleções
        atualizadas = 0
        for tarefa in tarefas:
            colecao_original = tarefa.get('colecao', '')
            colecao_limpa = limpar_colecao(colecao_original)
            
            if colecao_original != colecao_limpa:
                # Atualizar no banco
                url_update = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa['id']}"
                dados_update = {"colecao": colecao_limpa}
                
                resp_update = requests.patch(url_update, headers=headers, json=dados_update)
                
                if resp_update.status_code in [200, 204]:
                    print(f"✅ Atualizada: '{colecao_original}' → '{colecao_limpa}'")
                    atualizadas += 1
                else:
                    print(f"❌ Erro ao atualizar {tarefa['nome']}: {resp_update.status_code}")
        
        print(f"\n🎉 {atualizadas} coleções atualizadas!")
        
        # Verificar resultado
        print("\n📊 COLECÕES APÓS A LIMPEZA:")
        print("-" * 40)
        resp_final = requests.get(url, headers=headers)
        if resp_final.status_code == 200:
            tarefas_final = resp_final.json()
            colecoes_depois = set()
            for tarefa in tarefas_final:
                colecao = tarefa.get('colecao', '')
                if colecao:
                    colecoes_depois.add(colecao)
            
            for colecao in sorted(colecoes_depois):
                print(f"'{colecao}'")
        
        print("\n💡 Agora o filtro de coleção deve funcionar corretamente!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    limpar_colecoes() 