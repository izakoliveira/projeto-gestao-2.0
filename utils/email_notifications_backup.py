#!/usr/bin/env python3
"""
Sistema de Notificações por Email
Envia emails automáticos para usuários sobre mudanças em tarefas e projetos
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
import logging

# Carregar variáveis de ambiente automaticamente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNotifier:
    """Classe para gerenciar envio de emails de notificação"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.from_name = os.getenv('FROM_NAME', 'Sistema de Gestão de Projetos')
        
        # Verificar se as configurações de email estão disponíveis
        self.email_enabled = bool(self.smtp_user and self.smtp_pass)
        
        if not self.email_enabled:
            logger.warning("Configurações de email não encontradas. Notificações por email desabilitadas.")
    
    def _get_email_template(self, template_name: str, **kwargs) -> str:
        """Retorna o template HTML do email baseado no nome"""
        
        base_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notificação - Sistema de Gestão</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 300; }
        .content { padding: 30px; line-height: 1.6; }
        .task-info { background: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .task-name { font-size: 18px; font-weight: 600; color: #333; margin-bottom: 10px; }
        .task-details { color: #666; font-size: 14px; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; text-transform: uppercase; }
        .status-pendente { background: #fff3cd; color: #856404; }
        .status-em-progresso { background: #d1ecf1; color: #0c5460; }
        .status-concluida { background: #d4edda; color: #155724; }
        .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .btn:hover { background: #0056b3; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }
        .timestamp { color: #999; font-size: 12px; margin-top: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 Notificação do Sistema</h1>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p>Esta é uma notificação automática do Sistema de Gestão de Projetos</p>
            <p>Para desativar notificações por email, entre em contato com o administrador</p>
        </div>
        <div class="timestamp">
            Enviado em {timestamp}
        </div>
    </div>
</body>
</html>"""
        
        templates = {
            'tarefa_designada': """<h2 style="color: #28a745; margin-bottom: 20px;">✅ Nova Tarefa Designada</h2>
<p>Olá <strong>{usuario_nome}</strong>,</p>
<p>Você foi designado para uma nova tarefa no projeto.</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>Data de Início:</strong> {data_inicio}<br>
        <strong>Data de Fim:</strong> {data_fim}<br>
        <strong>Duração:</strong> {duracao}<br>
        <strong>Coleção:</strong> {colecao}
    </div>
</div>

<p>Clique no botão abaixo para acessar a tarefa:</p>
<a href="{projeto_url}" class="btn">Ver Tarefa</a>

<p>Boa sorte com a execução!</p>""",
            
            'tarefa_removida': """<h2 style="color: #dc3545; margin-bottom: 20px;">❌ Tarefa Removida</h2>
<p>Olá <strong>{usuario_nome}</strong>,</p>
<p>Você foi removido da seguinte tarefa:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}
    </div>
</div>

<p>Se você tiver alguma dúvida sobre essa alteração, entre em contato com o administrador do projeto.</p>""",
            
            'status_alterado': """<h2 style="color: #ffc107; margin-bottom: 20px;">🔄 Status da Tarefa Alterado</h2>
<p>Olá <strong>{usuario_nome}</strong>,</p>
<p>O status da sua tarefa foi alterado:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>Novo Status:</strong> 
        <span class="status-badge status-{status_class}">{novo_status}</span><br>
        <strong>Status Anterior:</strong> {status_anterior}
    </div>
</div>

<p>Clique no botão abaixo para acessar a tarefa:</p>
<a href="{projeto_url}" class="btn">Ver Tarefa</a>""",
            
            'tarefa_concluida': """<h2 style="color: #28a745; margin-bottom: 20px;">🎉 Tarefa Concluída!</h2>
<p>Parabéns <strong>{usuario_nome}</strong>!</p>
<p>Sua tarefa foi marcada como concluída:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>Status:</strong> 
        <span class="status-badge status-concluida">Concluída</span>
    </div>
</div>

<p>Excelente trabalho! Continue assim!</p>

<a href="{projeto_url}" class="btn">Ver Projeto</a>""",
            
            'projeto_criado': """<h2 style="color: #17a2b8; margin-bottom: 20px;">🚀 Novo Projeto Criado</h2>
<p>Olá <strong>{usuario_nome}</strong>,</p>
<p>Um novo projeto foi criado e você tem acesso a ele:</p>

<div class="task-info">
    <div class="task-name">{projeto_nome}</div>
    <div class="task-details">
        <strong>Descrição:</strong> {projeto_descricao}<br>
        <strong>Data de Início:</strong> {data_inicio}<br>
        <strong>Data de Fim:</strong> {data_fim}<br>
        <strong>Responsável:</strong> {responsavel}
    </div>
</div>

<p>Clique no botão abaixo para acessar o projeto:</p>
<a href="{projeto_url}" class="btn">Ver Projeto</a>"""
        }
        
        template = templates.get(template_name, '')
        if not template:
            logger.error(f"Template '{template_name}' não encontrado")
            return ""
        
        # Substituir variáveis no template
        content = template.format(**kwargs)
        
        # Formatar timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        return base_template.format(content=content, timestamp=timestamp)
    
    def _get_status_class(self, status: str) -> str:
        """Retorna a classe CSS para o status da tarefa"""
        status_map = {
            'pendente': 'pendente',
            'em progresso': 'em-progresso',
            'concluída': 'concluida'
        }
        return status_map.get(status, 'pendente')
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Envia o email usando SMTP"""
        if not self.email_enabled:
            logger.warning("Email desabilitado - não foi possível enviar para %s", to_email)
            return False
        
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.smtp_user}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adicionar conteúdo HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Conectar ao servidor SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            
            # Enviar email
            text = msg.as_string()
            server.sendmail(self.smtp_user, to_email, text)
            server.quit()
            
            logger.info(f"Email enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {str(e)}")
            return False
    
    def notificar_tarefa_designada(self, usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], projeto_url: str) -> bool:
        """Notifica usuário sobre nova tarefa designada"""
        try:
            html_content = self._get_email_template('tarefa_designada',
                usuario_nome=usuario_nome,
                tarefa_nome=tarefa_info.get('nome', ''),
                projeto_nome=tarefa_info.get('projeto_nome', ''),
                data_inicio=tarefa_info.get('data_inicio', 'Não definida'),
                data_fim=tarefa_info.get('data_fim', 'Não definida'),
                duracao=tarefa_info.get('duracao', 'Não definida'),
                colecao=tarefa_info.get('colecao', 'Não definida'),
                projeto_url=projeto_url
            )
            
            subject = f"🔔 Nova Tarefa Designada: {tarefa_info.get('nome', '')}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação de tarefa designada: {str(e)}")
            return False
    
    def notificar_tarefa_removida(self, usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any]) -> bool:
        """Notifica usuário sobre remoção de tarefa"""
        try:
            html_content = self._get_email_template('tarefa_removida',
                usuario_nome=usuario_nome,
                tarefa_nome=tarefa_info.get('nome', ''),
                projeto_nome=tarefa_info.get('projeto_nome', '')
            )
            
            subject = f"❌ Tarefa Removida: {tarefa_info.get('nome', '')}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação de tarefa removida: {str(e)}")
            return False
    
    def notificar_status_alterado(self, usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], 
                                 novo_status: str, status_anterior: str, projeto_url: str) -> bool:
        """Notifica usuário sobre alteração de status"""
        try:
            html_content = self._get_email_template('status_alterado',
                usuario_nome=usuario_nome,
                tarefa_nome=tarefa_info.get('nome', ''),
                projeto_nome=tarefa_info.get('projeto_nome', ''),
                novo_status=novo_status,
                status_anterior=status_anterior,
                status_class=self._get_status_class(novo_status),
                projeto_url=projeto_url
            )
            
            subject = f"🔄 Status Alterado: {tarefa_info.get('nome', '')} - {novo_status}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação de status alterado: {str(e)}")
            return False
    
    def notificar_tarefa_concluida(self, usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], projeto_url: str) -> bool:
        """Notifica usuário sobre conclusão de tarefa"""
        try:
            html_content = self._get_email_template('tarefa_concluida',
                usuario_nome=usuario_nome,
                tarefa_nome=tarefa_info.get('nome', ''),
                projeto_nome=tarefa_info.get('projeto_nome', ''),
                projeto_url=projeto_url
            )
            
            subject = f"🎉 Tarefa Concluída: {tarefa_info.get('nome', '')}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação de tarefa concluída: {str(e)}")
            return False
    
    def notificar_projeto_criado(self, usuario_email: str, usuario_nome: str, projeto_info: Dict[str, Any], projeto_url: str) -> bool:
        """Notifica usuário sobre novo projeto criado"""
        try:
            html_content = self._get_email_template('projeto_criado',
                usuario_nome=usuario_nome,
                projeto_nome=projeto_info.get('nome', ''),
                projeto_descricao=projeto_info.get('descricao', 'Sem descrição'),
                data_inicio=projeto_info.get('data_inicio', 'Não definida'),
                data_fim=projeto_info.get('data_fim', 'Não definida'),
                responsavel=projeto_info.get('responsavel', 'Não definido'),
                projeto_url=projeto_url
            )
            
            subject = f"🚀 Novo Projeto: {projeto_info.get('nome', '')}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação de projeto criado: {str(e)}")
            return False

# Instância global do notificador
email_notifier = EmailNotifier()

# Funções de conveniência para uso em outros módulos
def notificar_tarefa_designada(usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], projeto_url: str) -> bool:
    """Notifica usuário sobre nova tarefa designada"""
    return email_notifier.notificar_tarefa_designada(usuario_email, usuario_nome, tarefa_info, projeto_url)

def notificar_tarefa_removida(usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any]) -> bool:
    """Notifica usuário sobre remoção de tarefa"""
    return email_notifier.notificar_tarefa_removida(usuario_email, usuario_nome, tarefa_info)

def notificar_status_alterado(usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], 
                             novo_status: str, status_anterior: str, projeto_url: str) -> bool:
    """Notifica usuário sobre alteração de status"""
    return email_notifier.notificar_status_alterado(usuario_email, usuario_nome, tarefa_info, 
                                                   novo_status, status_anterior, projeto_url)

def notificar_tarefa_concluida(usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], projeto_url: str) -> bool:
    """Notifica usuário sobre conclusão de tarefa"""
    return email_notifier.notificar_tarefa_concluida(usuario_email, usuario_nome, tarefa_info, projeto_url)

def notificar_projeto_criado(usuario_email: str, usuario_nome: str, projeto_info: Dict[str, Any], projeto_url: str) -> bool:
    """Notifica usuário sobre novo projeto criado"""
    return email_notifier.notificar_projeto_criado(usuario_email, usuario_nome, projeto_info, projeto_url)
