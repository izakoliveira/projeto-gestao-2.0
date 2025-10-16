#!/usr/bin/env python3
"""
Script de teste para o sistema de notificações por email
Execute este script para verificar se as configurações de email estão funcionando
"""

import os
from dotenv import load_dotenv
from utils.email_notifications import (
    email_notifier, 
    notificar_tarefa_designada,
    notificar_tarefa_removida,
    notificar_status_alterado,
    notificar_tarefa_concluida
)

def testar_configuracao_email():
    """Testa a configuração básica do sistema de email"""
    print("🔧 Testando configuração do sistema de email...")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER', 'Não definido')}")
    print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'Não definido')}")
    print(f"SMTP_USER: {os.getenv('SMTP_USER', 'Não definido')}")
    print(f"SMTP_PASS: {'***' if os.getenv('SMTP_PASS') else 'Não definido'}")
    print(f"FROM_NAME: {os.getenv('FROM_NAME', 'Não definido')}")
    print()
    
    # Verificar status do notificador
    print(f"Email habilitado: {email_notifier.email_enabled}")
    if email_notifier.email_enabled:
        print("✅ Configuração de email válida!")
    else:
        print("❌ Configuração de email inválida ou incompleta")
        print("   Verifique as variáveis de ambiente no arquivo .env")
        return False
    
    print()
    return True

def testar_envio_emails():
    """Testa o envio de diferentes tipos de email"""
    if not email_notifier.email_enabled:
        print("❌ Sistema de email desabilitado. Configure as variáveis primeiro.")
        return
    
    print("📧 Testando envio de emails...")
    print("=" * 50)
    
    # Dados de teste
    tarefa_info = {
        'nome': 'Tarefa de Teste do Sistema',
        'projeto_nome': 'Projeto de Demonstração',
        'data_inicio': '01/01/2025',
        'data_fim': '31/01/2025',
        'duracao': '30 dias',
        'colecao': 'Testes e Validações'
    }
    
    projeto_url = "http://localhost:5000/projetos/123"
    
    # Teste 1: Tarefa designada
    print("1️⃣ Testando notificação de tarefa designada...")
    try:
        sucesso = notificar_tarefa_designada(
            'teste@exemplo.com',  # Substitua por um email válido para teste
            'Usuário de Teste',
            tarefa_info,
            projeto_url
        )
        if sucesso:
            print("   ✅ Email de tarefa designada enviado com sucesso!")
        else:
            print("   ❌ Falha ao enviar email de tarefa designada")
    except Exception as e:
        print(f"   ❌ Erro ao enviar email de tarefa designada: {e}")
    
    print()
    
    # Teste 2: Tarefa removida
    print("2️⃣ Testando notificação de tarefa removida...")
    try:
        sucesso = notificar_tarefa_removida(
            'teste@exemplo.com',  # Substitua por um email válido para teste
            'Usuário de Teste',
            tarefa_info
        )
        if sucesso:
            print("   ✅ Email de tarefa removida enviado com sucesso!")
        else:
            print("   ❌ Falha ao enviar email de tarefa removida")
    except Exception as e:
        print(f"   ❌ Erro ao enviar email de tarefa removida: {e}")
    
    print()
    
    # Teste 3: Status alterado
    print("3️⃣ Testando notificação de status alterado...")
    try:
        sucesso = notificar_status_alterado(
            'teste@exemplo.com',  # Substitua por um email válido para teste
            'Usuário de Teste',
            tarefa_info,
            'em progresso',
            'pendente',
            projeto_url
        )
        if sucesso:
            print("   ✅ Email de status alterado enviado com sucesso!")
        else:
            print("   ❌ Falha ao enviar email de status alterado")
    except Exception as e:
        print(f"   ❌ Erro ao enviar email de status alterado: {e}")
    
    print()
    
    # Teste 4: Tarefa concluída
    print("4️⃣ Testando notificação de tarefa concluída...")
    try:
        sucesso = notificar_tarefa_concluida(
            'teste@exemplo.com',  # Substitua por um email válido para teste
            'Usuário de Teste',
            tarefa_info,
            projeto_url
        )
        if sucesso:
            print("   ✅ Email de tarefa concluída enviado com sucesso!")
        else:
            print("   ❌ Falha ao enviar email de tarefa concluída")
    except Exception as e:
        print(f"   ❌ Erro ao enviar email de tarefa concluída: {e}")

def testar_conexao_smtp():
    """Testa a conexão com o servidor SMTP"""
    if not email_notifier.email_enabled:
        print("❌ Sistema de email desabilitado.")
        return
    
    print("🔌 Testando conexão SMTP...")
    print("=" * 50)
    
    try:
        import smtplib
        
        # Tentar conectar ao servidor SMTP
        print(f"Conectando a {email_notifier.smtp_server}:{email_notifier.smtp_port}...")
        
        server = smtplib.SMTP(email_notifier.smtp_server, email_notifier.smtp_port)
        server.starttls()
        
        print("✅ Conexão SMTP estabelecida com sucesso!")
        print("🔐 Tentando autenticação...")
        
        server.login(email_notifier.smtp_user, email_notifier.smtp_pass)
        print("✅ Autenticação SMTP bem-sucedida!")
        
        server.quit()
        print("✅ Conexão SMTP fechada com sucesso!")
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Falha na autenticação SMTP")
        print("   Verifique usuário e senha")
    except smtplib.SMTPConnectError:
        print("❌ Falha na conexão com servidor SMTP")
        print("   Verifique servidor e porta")
    except Exception as e:
        print(f"❌ Erro na conexão SMTP: {e}")

def main():
    """Função principal do teste"""
    print("🚀 TESTE DO SISTEMA DE NOTIFICAÇÕES POR EMAIL")
    print("=" * 60)
    print()
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Testar configuração
    if not testar_configuracao_email():
        print("\n❌ Configuração inválida. Corrija as variáveis de ambiente primeiro.")
        return
    
    print()
    
    # Testar conexão SMTP
    testar_conexao_smtp()
    
    print()
    
    # Perguntar se quer testar envio de emails
    resposta = input("📧 Deseja testar o envio de emails? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        print()
        testar_envio_emails()
    
    print()
    print("🏁 Teste concluído!")
    print("\n💡 Dicas:")
    print("   - Configure um email válido no código para testar o envio")
    print("   - Verifique os logs para mais detalhes")
    print("   - Consulte docs/CONFIGURACAO_EMAIL.md para configuração")

if __name__ == "__main__":
    main()
