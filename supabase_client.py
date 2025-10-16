import os
import requests
from dotenv import load_dotenv
from config.database import SUPABASE_URL as DB_SUPABASE_URL, SUPABASE_KEY as DB_SUPABASE_KEY

# 🔧 TIMESTAMP: 2025-08-20 11:42 - Forçando rebuild no Render
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or DB_SUPABASE_URL
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or DB_SUPABASE_KEY
USERS_TABLE = "usuarios"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Validação básica para evitar URLs inválidas quando variáveis não estão definidas
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Configuração do Supabase ausente. Defina SUPABASE_URL e SUPABASE_KEY no ambiente ou em config.database."
    )

def get_user_by_email(email):
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?email=eq.{email}"
    print("URL usada na busca:", url)
    print("Headers usados:", headers)
    resp = requests.get(url, headers=headers)
    print("Resposta:", resp.status_code, resp.text)
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]
    return None

def get_user_by_id(user_id: str):
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?id=eq.{user_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]
    return None

def create_user(nome, email, senha_hash):
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}"
    data = {
        "nome": nome,
        "email": email,
        "senha_hash": senha_hash
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 201:
        return True
    else:
        print(f"Erro ao criar usuário: {resp.status_code} - {resp.text}")
        return False

def create_simple_user(nome):
    """Cria um usuário simples apenas com nome (para designar tarefas)"""
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}"
    # Usar placeholders para usuários simples (já que os campos são obrigatórios)
    import time
    timestamp = int(time.time())
    email_placeholder = f"usuario_simples_{timestamp}@sistema.local"
    # Hash placeholder que nunca será usado para login (usuário simples não faz login)
    senha_hash_placeholder = "USUARIO_SIMPLES_SEM_LOGIN"
    
    data = {
        "nome": nome,
        "email": email_placeholder,  # Email placeholder para contornar a restrição NOT NULL
        "senha_hash": senha_hash_placeholder  # Hash placeholder para contornar a restrição NOT NULL
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data)
        print(f"Status da resposta: {resp.status_code}")
        print(f"Texto da resposta: '{resp.text}'")
        
        if resp.status_code == 201:
            # Usuário criado com sucesso
            if resp.text and resp.text.strip():
                try:
                    resposta_json = resp.json()
                    if isinstance(resposta_json, list) and len(resposta_json) > 0:
                        return resposta_json[0]
                    elif isinstance(resposta_json, dict):
                        return resposta_json
                except Exception as e:
                    print(f"Erro ao fazer parse do JSON: {e}")
            
            # Se chegou até aqui, o usuário foi criado mas não temos os dados completos
            # Vamos buscar o usuário recém-criado pelo email
            try:
                user_search = get_user_by_email(email_placeholder)
                if user_search:
                    return user_search
            except:
                pass
            
            # Como último recurso, retorna dados básicos
            return {"nome": nome, "email": email_placeholder}
        else:
            print(f"Erro ao criar usuário simples: {resp.status_code} - {resp.text}")
            return None
            
    except Exception as e:
        print(f"Exceção ao criar usuário simples: {e}")
        return None

def get_all_users():
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?select=id,nome,email"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return []

# PROJETOS

def get_all_projects():
    url = f"{SUPABASE_URL}/rest/v1/projetos"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return []

def get_project_by_id(projeto_id):
    url = f"{SUPABASE_URL}/rest/v1/projetos?id=eq.{projeto_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]
    return None

def create_project(data):
    url = f"{SUPABASE_URL}/rest/v1/projetos"
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code in [200, 201]:
        return True
    else:
        print(f"Erro ao criar projeto: {resp.status_code} - {resp.text}")
        return False

def update_project(projeto_id, data):
    url = f"{SUPABASE_URL}/rest/v1/projetos?id=eq.{projeto_id}"
    resp = requests.patch(url, headers=headers, json=data)
    return resp.status_code in [200, 204]

def delete_project(projeto_id):
    url = f"{SUPABASE_URL}/rest/v1/projetos?id=eq.{projeto_id}"
    resp = requests.delete(url, headers=headers)
    return resp.status_code in [200, 204]

# TAREFAS

def get_all_tasks():
    url = f"{SUPABASE_URL}/rest/v1/tarefas"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return []

def get_tasks_by_project(projeto_id):
    url = f"{SUPABASE_URL}/rest/v1/tarefas?projeto_id=eq.{projeto_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return []

def create_task(data):
    url = f"{SUPABASE_URL}/rest/v1/tarefas"
    resp = requests.post(url, headers=headers, json=data)
    return resp.status_code in [200, 201]

def update_task(tarefa_id, data):
    url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
    resp = requests.patch(url, headers=headers, json=data)
    return resp.status_code in [200, 204]

def delete_task(tarefa_id):
    url = f"{SUPABASE_URL}/rest/v1/tarefas?id=eq.{tarefa_id}"
    resp = requests.delete(url, headers=headers)
    return resp.status_code in [200, 204]
