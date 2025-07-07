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
