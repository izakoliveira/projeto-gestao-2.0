import requests
from supabase_client import SUPABASE_URL, SUPABASE_KEY

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Listar admins
print("=== ADMINISTRADORES ATUAIS ===")
data = {'operation': 'list'}
url = f"{SUPABASE_URL}/rest/v1/rpc/manage_admin"
resp = requests.post(url, json=data, headers=headers)

if resp.status_code == 200:
    admins = resp.json()
    if admins:
        for admin in admins:
            print(f"• {admin.get('email')} - Nível: {admin.get('nivel_acesso')} - Ativo: {admin.get('ativo')}")
    else:
        print("Nenhum administrador encontrado.")
else:
    print(f"Erro ao listar admins: {resp.status_code} - {resp.text}")