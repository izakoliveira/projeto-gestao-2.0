"""
Script para migrar restrições do restricoes.json para o banco de dados Supabase
Execute este script uma vez após aplicar o SQL de migração
"""
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def migrar_restricoes():
    print("Iniciando migração de restrições...")
    
    # Carregar dados do arquivo JSON
    try:
        with open('restricoes.json', 'r') as f:
            restricoes_json = json.load(f)
    except Exception as e:
        print(f"Erro ao ler restricoes.json: {e}")
        return False
    
    print(f"Encontradas restrições para {len(restricoes_json)} usuários no JSON")
    
    # Campos de restrição
    campos_restricao = [
        'restr_criar_projeto', 'restr_editar_projeto', 'restr_excluir_projeto',
        'restr_criar_tarefa', 'restr_editar_tarefa', 'restr_excluir_tarefa',
        'restr_editar_responsavel', 'restr_editar_duracao', 'restr_editar_datas',
        'restr_editar_predecessoras', 'restr_editar_nome_tarefa'
    ]
    
    sucesso = 0
    erros = 0
    
    # Migrar cada usuário
    for user_id, dados in restricoes_json.items():
        try:
            # Preparar dados de atualização
            dados_update = {}
            for campo in campos_restricao:
                if campo in dados:
                    dados_update[campo] = bool(dados[campo])
            
            if dados_update:
                # Atualizar no banco
                url = f"{SUPABASE_URL}/rest/v1/usuarios?id=eq.{user_id}"
                response = requests.patch(url, json=dados_update, headers=headers)
                
                if response.status_code in [200, 204]:
                    nome = dados.get('nome', 'Desconhecido')
                    print(f"✓ Migrado: {nome} ({user_id})")
                    sucesso += 1
                else:
                    print(f"✗ Erro ao migrar {user_id}: {response.status_code} - {response.text}")
                    erros += 1
        except Exception as e:
            print(f"✗ Erro ao migrar {user_id}: {e}")
            erros += 1
    
    print(f"\n=== Resultado da Migração ===")
    print(f"Sucesso: {sucesso}")
    print(f"Erros: {erros}")
    print(f"Total: {len(restricoes_json)}")
    
    return erros == 0

if __name__ == "__main__":
    sucesso = migrar_restricoes()
    if sucesso:
        print("\n✅ Migração concluída com sucesso!")
        print("Agora as restrições estão no banco de dados e serão sincronizadas entre todas as instalações.")
    else:
        print("\n⚠️ Migração concluída com erros. Verifique os logs acima.")
