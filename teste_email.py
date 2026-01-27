#!/usr/bin/env python3
"""
Script de teste para verificar o envio de emails
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    from utils.email_notifications import EmailNotifier, notificar_tarefa_concluida_admin

    def testar_email():
        print("🔍 Testando sistema de notificações por email...")

        # Criar notificador
        notifier = EmailNotifier()

        print(f"📧 Email habilitado: {notifier.email_enabled}")
        print(f"🔧 SMTP Server: {notifier.smtp_server}")
        print(f"🔧 SMTP Port: {notifier.smtp_port}")
        print(f"👤 SMTP User: {notifier.smtp_user}")
        print(f"🏷️  From Name: {notifier.from_name}")

        if not notifier.email_enabled:
            print("❌ Email não está habilitado. Verifique as configurações SMTP_USER e SMTP_PASS no .env")
            return False

        # Testar envio de email simples
        print("\n📤 Testando envio de email...")

        # Dados de teste
        admin_email = "izak.gomes59@gmail.com"
        admin_nome = "Izak Oliveira"
        tarefa_info = {
            'nome': 'Tarefa de Teste',
            'id': 999,
            'projeto_nome': 'Projeto de Teste',
            'status': 'concluida',
            'data_conclusao': '2024-01-26'
        }
        usuario_alteracao = "Usuário Teste"
        projeto_url = "http://localhost:5000/projetos/1"

        # Tentar enviar notificação
        sucesso = notificar_tarefa_concluida_admin(
            admin_email=admin_email,
            admin_nome=admin_nome,
            tarefa_info=tarefa_info,
            usuario_alteracao=usuario_alteracao,
            projeto_url=projeto_url
        )

        if sucesso:
            print("✅ Email enviado com sucesso!")
            return True
        else:
            print("❌ Falha ao enviar email")
            return False

    if __name__ == "__main__":
        testar_email()

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se o arquivo email_notifications.py existe e está correto")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()