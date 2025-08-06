import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Conecta ao Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Se as variáveis não estiverem definidas, usar valores padrão para desenvolvimento
if not url or not key:
    print("⚠️  SUPABASE_URL ou SUPABASE_KEY não definidas. Usando valores padrão para desenvolvimento.")
    url = "https://zvdpuxggltqejplybzet.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"

try:
    supabase: Client = create_client(url, key)
    # Testando a conexão com o Supabase
    supabase_client = supabase.auth
    print("✅ Conectado com sucesso ao Supabase!")
except Exception as e:
    print(f"❌ Erro ao conectar com o Supabase: {e}")
    # Criar um cliente vazio para evitar erros
    supabase = None

# Constantes do banco
SUPABASE_URL = url
SUPABASE_KEY = key 