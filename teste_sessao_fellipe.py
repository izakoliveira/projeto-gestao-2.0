#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

from supabase import create_client, Client

# Configuração do Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def testar_sessao_fellipe():
    """Testa a sessão do usuário Fellipe"""
    
    # ID do usuário Fellipe
    user_id = "6afb28b7-2c10-4f9b-a0d5-c9ce27600521"
    
    print(f"🔍 Testando sessão para usuário Fellipe (ID: {user_id})")
    print("=" * 50)
    
    try:
        # Buscar informações do usuário Fellipe
        print("1. Buscando informações do usuário Fellipe...")
        usuario_resp = supabase.table("usuarios").select("id, nome, email").eq("id", user_id).execute()
        usuario = usuario_resp.data[0] if usuario_resp.data else None
        
        if usuario:
            print(f"   ✅ Nome: {usuario['nome']}")
            print(f"   ✅ Email: {usuario['email']}")
            print(f"   ✅ ID: {usuario['id']}")
            
            # Verificar se o email é o do izak
            if usuario['email'] == 'izak.gomes59@gmail.com':
                print("   ❌ PROBLEMA: Usuário Fellipe está com email do izak!")
                print("   💡 SOLUÇÃO: O link Produção aparecerá porque o email é igual")
            else:
                print("   ✅ Email correto - não é o do izak")
                
            # Verificar se há outros usuários com o mesmo email
            print("\n2. Verificando se há outros usuários com o mesmo email...")
            email_duplicado_resp = supabase.table("usuarios").select("id, nome, email").eq("email", usuario['email']).execute()
            usuarios_mesmo_email = email_duplicado_resp.data if hasattr(email_duplicado_resp, 'data') else []
            
            if len(usuarios_mesmo_email) > 1:
                print(f"   ⚠️  AVISO: {len(usuarios_mesmo_email)} usuários com o mesmo email!")
                for u in usuarios_mesmo_email:
                    print(f"      - {u['nome']} (ID: {u['id']}) - {u['email']}")
            else:
                print("   ✅ Apenas um usuário com este email")
                
        else:
            print("   ❌ Usuário não encontrado!")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_sessao_fellipe() 