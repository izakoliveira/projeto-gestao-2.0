#!/usr/bin/env python3
"""
Script de Teste para Notificações de Tarefas Atrasadas
Executa uma verificação manual de tarefas atrasadas
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_overdue_notifications():
    """Testa o sistema de notificações de tarefas atrasadas"""
    try:
        print("🔍 Testando sistema de notificações de tarefas atrasadas...")

        # Importar o gerenciador
        from utils.overdue_notifications import overdue_manager

        print("✅ Gerenciador importado com sucesso")

        # Verificar configuração
        if not overdue_manager.supabase:
            print("❌ Supabase não configurado - verifique variáveis de ambiente")
            return False

        print("✅ Supabase configurado")

        # Executar verificação
        print("🔍 Executando verificação de tarefas atrasadas...")
        overdue_manager.force_check_now()

        print("✅ Verificação concluída")
        return True

    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    print("=== TESTE DE NOTIFICAÇÕES DE TAREFAS ATRASADAS ===")

    success = test_overdue_notifications()

    if success:
        print("\n🎉 Teste concluído com sucesso!")
        print("💡 O sistema de notificações está funcionando.")
        print("💡 As notificações serão enviadas automaticamente a cada 24 horas.")
    else:
        print("\n❌ Teste falhou - verifique a configuração.")

    sys.exit(0 if success else 1)