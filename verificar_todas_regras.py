#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
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

def carregar_restricoes():
    """Carrega as restrições do arquivo JSON"""
    try:
        with open('restricoes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar restrições: {e}")
        return {}

def verificar_todas_regras():
    """Verifica todas as regras para todos os usuários"""
    
    print("🔍 VERIFICAÇÃO COMPLETA DE TODAS AS REGRAS")
    print("=" * 60)
    
    # 1. Carregar restrições
    print("\n1. 📋 CARREGANDO RESTRIÇÕES...")
    restricoes = carregar_restricoes()
    print(f"   ✅ Restrições carregadas: {len(restricoes)} usuários")
    
    # 2. Buscar todos os usuários
    print("\n2. 👥 BUSCANDO TODOS OS USUÁRIOS...")
    try:
        usuarios_resp = supabase.table("usuarios").select("id, nome, email").execute()
        usuarios = usuarios_resp.data if hasattr(usuarios_resp, 'data') else []
        print(f"   ✅ {len(usuarios)} usuários encontrados")
    except Exception as e:
        print(f"   ❌ Erro ao buscar usuários: {e}")
        return
    
    # 3. Verificar cada usuário
    print("\n3. 🔍 VERIFICANDO CADA USUÁRIO...")
    print("-" * 60)
    
    problemas_encontrados = []
    
    for usuario in usuarios:
        user_id = str(usuario['id'])
        nome = usuario['nome']
        email = usuario['email']
        
        print(f"\n👤 USUÁRIO: {nome} ({email})")
        print(f"   ID: {user_id}")
        
        # Verificar se tem restrições definidas
        if user_id in restricoes:
            restricoes_usuario = restricoes[user_id]
            print(f"   ✅ Restrições encontradas")
            
            # Verificar cada restrição
            restricoes_ativas = []
            for restricao, valor in restricoes_usuario.items():
                if restricao.startswith('restr_') and valor:
                    restricoes_ativas.append(restricao.replace('restr_', ''))
            
            if restricoes_ativas:
                print(f"   ⚠️  Restrições ativas: {', '.join(restricoes_ativas)}")
            else:
                print(f"   ✅ Sem restrições ativas")
                
        else:
            print(f"   ❌ PROBLEMA: Usuário não tem restrições definidas!")
            problemas_encontrados.append(f"Usuário {nome} ({email}) não tem restrições definidas")
        
        # Verificar regras específicas
        print(f"   🔍 Verificando regras específicas...")
        
        # Regra 1: Link Produção (apenas para izak)
        if email == 'izak.gomes59@gmail.com':
            print(f"   ✅ Link Produção: DEVE aparecer (usuário izak)")
        else:
            print(f"   ✅ Link Produção: NÃO deve aparecer (não é izak)")
        
        # Regra 2: Link Administração (apenas para izak)
        if email == 'izak.gomes59@gmail.com':
            print(f"   ✅ Link Administração: DEVE aparecer (usuário izak)")
        else:
            print(f"   ✅ Link Administração: NÃO deve aparecer (não é izak)")
        
        # Regra 3: Link Pastas (apenas para izak)
        if email == 'izak.gomes59@gmail.com':
            print(f"   ✅ Link Pastas: DEVE aparecer (usuário izak)")
        else:
            print(f"   ✅ Link Pastas: NÃO deve aparecer (não é izak)")
    
    # 4. Verificar usuários órfãos (restrições sem usuário)
    print("\n4. 🔍 VERIFICANDO USUÁRIOS ÓRFÃOS...")
    usuarios_ids = [str(u['id']) for u in usuarios]
    restricoes_ids = list(restricoes.keys())
    
    usuarios_orfos = [rid for rid in restricoes_ids if rid not in usuarios_ids]
    if usuarios_orfos:
        print(f"   ⚠️  {len(usuarios_orfos)} usuários órfãos encontrados:")
        for rid in usuarios_orfos:
            print(f"      - ID: {rid}")
            if rid in restricoes:
                nome = restricoes[rid].get('nome', 'N/A')
                email = restricoes[rid].get('email', 'N/A')
                print(f"        Nome: {nome}, Email: {email}")
    else:
        print(f"   ✅ Nenhum usuário órfão encontrado")
    
    # 5. Verificar usuários sem restrições
    print("\n5. 🔍 VERIFICANDO USUÁRIOS SEM RESTRIÇÕES...")
    usuarios_sem_restricoes = [u for u in usuarios if str(u['id']) not in restricoes]
    if usuarios_sem_restricoes:
        print(f"   ⚠️  {len(usuarios_sem_restricoes)} usuários sem restrições:")
        for u in usuarios_sem_restricoes:
            print(f"      - {u['nome']} ({u['email']}) - ID: {u['id']}")
    else:
        print(f"   ✅ Todos os usuários têm restrições definidas")
    
    # 6. Resumo final
    print("\n6. 📊 RESUMO FINAL")
    print("-" * 60)
    print(f"   Total de usuários: {len(usuarios)}")
    print(f"   Usuários com restrições: {len(restricoes)}")
    print(f"   Usuários sem restrições: {len(usuarios_sem_restricoes)}")
    print(f"   Usuários órfãos: {len(usuarios_orfos)}")
    print(f"   Problemas encontrados: {len(problemas_encontrados)}")
    
    if problemas_encontrados:
        print(f"\n❌ PROBLEMAS ENCONTRADOS:")
        for problema in problemas_encontrados:
            print(f"   - {problema}")
    else:
        print(f"\n✅ TODAS AS REGRAS ESTÃO APLICADAS CORRETAMENTE!")
    
    # 7. Verificar regras específicas do sistema
    print("\n7. 🔧 VERIFICANDO REGRAS DO SISTEMA...")
    
    # Verificar se o izak tem todas as permissões
    izak_restricoes = None
    for user_id, restricoes_user in restricoes.items():
        if restricoes_user.get('email') == 'izak.gomes59@gmail.com':
            izak_restricoes = restricoes_user
            break
    
    if izak_restricoes:
        print(f"   ✅ Usuário izak encontrado nas restrições")
        restricoes_izak = [k for k, v in izak_restricoes.items() if k.startswith('restr_') and v]
        if restricoes_izak:
            print(f"   ⚠️  AVISO: Usuário izak tem restrições ativas: {restricoes_izak}")
        else:
            print(f"   ✅ Usuário izak sem restrições (correto)")
    else:
        print(f"   ❌ PROBLEMA: Usuário izak não encontrado nas restrições!")
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    verificar_todas_regras() 