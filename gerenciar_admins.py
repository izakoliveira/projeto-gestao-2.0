"""
Script para adicionar/gerenciar usuários admin via Python
Execute: python gerenciar_admins.py
"""

import requests
from supabase_client import SUPABASE_URL, SUPABASE_KEY

# Headers para requests
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def listar_usuarios():
    """Lista todos os usuários disponíveis"""
    print("\n=== USUÁRIOS DISPONÍVEIS ===")
    url = f"{SUPABASE_URL}/rest/v1/usuarios?select=id,email,nome&order=email"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        usuarios = resp.json()
        for i, user in enumerate(usuarios, 1):
            print(f"{i}. {user.get('email')} - {user.get('nome')} (ID: {user.get('id')})")
        return usuarios
    else:
        print(f"❌ Erro ao listar usuários: {resp.status_code} - {resp.text}")
        return []


def listar_admins():
    """Lista todos os administradores"""
    print("\n=== ADMINISTRADORES ATUAIS ===")
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
        return admins
    else:
        print(f"❌ Erro ao listar admins: {resp.status_code} - {resp.text}")
        return []


def adicionar_admin(usuario_id, nivel='admin', criado_por='d0d784bd-f2bb-44b2-8096-5c10ec4d57be'):
    """
    Adiciona um novo administrador
    
    Args:
        usuario_id: UUID do usuário
        nivel: 'admin', 'super_admin' ou 'master_admin'
        criado_por: UUID de quem está criando (padrão: você)
    """
    try:
        data = {
            'operation': 'add',
            'user_id': usuario_id,
            'admin_level': nivel
        }
        
        url = f"{SUPABASE_URL}/rest/v1/rpc/manage_admin"
        resp = requests.post(url, json=data, headers=headers)
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('success'):
                print(f"\n✅ Usuário adicionado como {nivel} com sucesso!")
                return True
            else:
                print(f"\n❌ Erro: {result.get('message')}")
                return False
        else:
            print(f"\n❌ Erro ao adicionar usuário: {resp.status_code} - {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def remover_admin(usuario_id):
    """Desativa um administrador (não deleta, apenas marca como inativo)"""
    try:
        data = {
            'operation': 'remove',
            'user_id': usuario_id
        }
        
        url = f"{SUPABASE_URL}/rest/v1/rpc/manage_admin"
        resp = requests.post(url, json=data, headers=headers)
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('success'):
                print("\n✅ Administrador desativado com sucesso!")
                return True
            else:
                print(f"\n❌ Erro: {result.get('message')}")
                return False
        else:
            print(f"❌ Erro ao remover: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao remover: {e}")
        return False


def menu():
    """Menu interativo"""
    while True:
        print("\n" + "="*50)
        print("GERENCIAMENTO DE ADMINISTRADORES")
        print("="*50)
        print("1. Listar todos os usuários")
        print("2. Listar administradores atuais")
        print("3. Adicionar novo administrador")
        print("4. Desativar administrador")
        print("5. Sair")
        print("="*50)
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == '1':
            listar_usuarios()
            
        elif escolha == '2':
            listar_admins()
            
        elif escolha == '3':
            listar_usuarios()
            usuario_id = input("\nCole o UUID do usuário: ").strip()
            print("\nNíveis disponíveis:")
            print("1. admin (padrão)")
            print("2. super_admin")
            print("3. master_admin")
            nivel = input("Escolha o nível (1-3): ").strip()
            
            niveis = {'1': 'admin', '2': 'super_admin', '3': 'master_admin'}
            nivel_acesso = niveis.get(nivel, 'admin')
            
            adicionar_admin(usuario_id, nivel_acesso)
            
        elif escolha == '4':
            listar_admins()
            usuario_id = input("\nCole o UUID do admin para desativar: ").strip()
            confirma = input("Tem certeza? (s/n): ").strip().lower()
            if confirma == 's':
                remover_admin(usuario_id)
                
        elif escolha == '5':
            print("\nSaindo...")
            break
        else:
            print("\n❌ Opção inválida!")


if __name__ == "__main__":
    print("\n🔐 Sistema de Gerenciamento de Administradores")
    menu()
