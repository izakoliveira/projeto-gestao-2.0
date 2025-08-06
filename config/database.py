import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Conecta ao Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise Exception("SUPABASE_URL ou SUPABASE_KEY não definidas no arquivo .env")

supabase: Client = create_client(url, key)

# Testando a conexão com o Supabase
try:
    supabase_client = supabase.auth
    print("Conectado com sucesso ao Supabase!")
except Exception as e:
    print(f"Erro ao conectar com o Supabase: {e}")

# Constantes do banco
SUPABASE_URL = url
SUPABASE_KEY = key 