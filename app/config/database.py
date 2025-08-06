"""
Configuração do banco de dados Supabase
=======================================
"""

import os
from supabase import create_client, Client

# Variável global para o cliente Supabase
supabase: Client = None

def init_supabase():
    """Inicializa a conexão com o Supabase"""
    global supabase
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise Exception("SUPABASE_URL ou SUPABASE_KEY não definidas no arquivo .env")
    
    supabase = create_client(url, key)
    
    # Testando a conexão com o Supabase
    try:
        supabase_client = supabase.auth
        print("Conectado com sucesso ao Supabase!")
    except Exception as e:
        print(f"Erro ao conectar com o Supabase: {e}")
        raise

def get_supabase():
    """Retorna o cliente Supabase"""
    if supabase is None:
        raise Exception("Supabase não foi inicializado. Chame init_supabase() primeiro.")
    return supabase 