#!/usr/bin/env python3
"""
Script para testar envio direto de email para administradores
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.email_notifications import EmailNotifier
from supabase import create_client, Client
from config.database import SUPABASE_URL, SUPABASE_KEY

def testar_envio_email_admin():
    """Testa envio de email para administradores"""
    try:
        # Inicializar notificador
        email_notifier = EmailNotifier()

        # Conectar ao Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Buscar administradores
        admins_response = supabase.table('usuarios_admin').select('usuario_id, usuarios!usuarios_admin_usuario_id_fkey(email, nome)').execute()

        if not admins_response.data:
            print("❌ Nenhum administrador encontrado!")
            return False

        print(f"📧 Encontrados {len(admins_response.data)} administradores:")

        # Enviar email de teste para cada admin
        for admin_item in admins_response.data:
            admin_email = admin_item['usuarios']['email']
            admin_nome = admin_item['usuarios']['nome']

            print(f"📤 Enviando email de teste para: {admin_email} ({admin_nome})")

            # Criar conteúdo de teste
            html_content = f"""
            <h2 style="color: #28a745;">🧪 Teste de Notificação - Sistema de Gestão</h2>
            <p>Olá <strong>{admin_nome}</strong>,</p>
            <p>Este é um email de teste para verificar se o sistema de notificações está funcionando corretamente.</p>
            <p>Se você recebeu este email, significa que:</p>
            <ul>
                <li>✅ A configuração SMTP está correta</li>
                <li>✅ Os dados dos administradores estão acessíveis</li>
                <li>✅ O sistema de envio de emails está operacional</li>
            </ul>
            <p><strong>Data/Hora do teste:</strong> {email_notifier._formatar_data_brasileira(None)}</p>
            <p>Atenciosamente,<br>Sistema de Gestão de Projetos</p>
            """

            # Enviar email
            success = email_notifier._send_email(
                to_email=admin_email,
                subject="🧪 Teste de Notificação - Sistema de Gestão",
                html_content=html_content
            )

            if success:
                print(f"✅ Email enviado com sucesso para {admin_email}")
            else:
                print(f"❌ Falha ao enviar email para {admin_email}")

        return True

    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste de envio de email para administradores...")
    success = testar_envio_email_admin()
    if success:
        print("\n🎉 Teste concluído!")
        print("💡 Verifique as caixas de entrada dos administradores para confirmar o recebimento.")
    else:
        print("\n❌ Teste falhou!")