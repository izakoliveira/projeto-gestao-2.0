import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
USERS_TABLE = "usuarios"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

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
