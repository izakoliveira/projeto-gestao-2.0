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

def testar_email_fellipe():
    """Testa especificamente o email do usuário Fellipe"""
    
    # ID do usuário Fellipe
    user_id = "6afb28b7-2c10-4f9b-a0d5-c9ce27600521"
    
    print(f"🔍 Testando email do usuário Fellipe (ID: {user_id})")
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
            
            # Verificar se o email é exatamente igual ao do izak
            email_izak = 'izak.gomes59@gmail.com'
            email_fellipe = usuario['email']
            
            print(f"\n2. Comparando emails...")
            print(f"   Email do izak: '{email_izak}'")
            print(f"   Email do Fellipe: '{email_fellipe}'")
            print(f"   São iguais? {email_fellipe == email_izak}")
            
            # Verificar se há espaços extras ou caracteres especiais
            print(f"\n3. Verificando caracteres...")
            print(f"   Comprimento email izak: {len(email_izak)}")
            print(f"   Comprimento email Fellipe: {len(email_fellipe)}")
            print(f"   Email Fellipe (repr): {repr(email_fellipe)}")
            print(f"   Email izak (repr): {repr(email_izak)}")
            
            # Verificar se há diferenças de case
            print(f"\n4. Verificando case...")
            print(f"   Email Fellipe (lower): '{email_fellipe.lower()}'")
            print(f"   Email izak (lower): '{email_izak.lower()}'")
            print(f"   São iguais (lower)? {email_fellipe.lower() == email_izak.lower()}")
            
            # Verificar se há espaços no início ou fim
            print(f"\n5. Verificando espaços...")
            print(f"   Email Fellipe (strip): '{email_fellipe.strip()}'")
            print(f"   Email izak (strip): '{email_izak.strip()}'")
            print(f"   São iguais (strip)? {email_fellipe.strip() == email_izak.strip()}")
            
            # Conclusão
            print(f"\n6. CONCLUSÃO:")
            if email_fellipe == email_izak:
                print("   ❌ PROBLEMA: Emails são idênticos!")
                print("   💡 SOLUÇÃO: O link Produção aparecerá para o Fellipe")
            else:
                print("   ✅ Emails são diferentes")
                print("   💡 O link Produção NÃO deve aparecer para o Fellipe")
                
        else:
            print("   ❌ Usuário não encontrado!")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_email_fellipe() 