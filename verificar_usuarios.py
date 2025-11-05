"""
Script para verificar usuários no banco de dados
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

# Conectar ao Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Buscar todos os usuários
    response = supabase.table("usuarios").select("id, nome, email").order("nome").execute()
    
    if response.data:
        print("\n" + "="*60)
        print("USUÁRIOS NO BANCO DE DADOS")
        print("="*60)
        
        usuarios_simples = []
        usuarios_completos = []
        
        for user in response.data:
            nome = user.get('nome', 'Sem nome')
            email = user.get('email', 'Sem email')
            user_id = user.get('id', 'Sem ID')
            
            if email.endswith('@sistema.local'):
                usuarios_simples.append(user)
                print(f"\n✅ USUÁRIO SIMPLES:")
            else:
                usuarios_completos.append(user)
                print(f"\n📧 USUÁRIO COMPLETO:")
            
            print(f"   Nome: {nome}")
            print(f"   Email: {email}")
            print(f"   ID: {user_id}")
        
        print("\n" + "="*60)
        print(f"TOTAL: {len(response.data)} usuários")
        print(f"  - Usuários Simples: {len(usuarios_simples)}")
        print(f"  - Usuários Completos: {len(usuarios_completos)}")
        print("="*60)
        
        if len(usuarios_simples) == 0:
            print("\n⚠️ NENHUM USUÁRIO SIMPLES ENCONTRADO!")
            print("   Para testar a conversão, você precisa:")
            print("   1. Criar um usuário simples primeiro")
            print("   2. Vá em: /admin/usuarios_simples")
            print("   3. Use o formulário 'Criar Novo Usuário Simples'")
            print("   4. Após criar, o botão 📧 aparecerá na tabela")
    else:
        print("\n❌ Nenhum usuário encontrado no banco de dados")
        
except Exception as e:
    print(f"\n❌ Erro ao buscar usuários: {e}")
