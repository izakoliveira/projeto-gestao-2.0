#!/usr/bin/env python3
"""
Sistema de Notificações por Email - Versão Simplificada
Envia emails automáticos para usuários sobre mudanças em tarefas e projetos
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logger.info("Arquivo .env carregado com sucesso")
except ImportError:
    logger.warning("python-dotenv não instalado, usando variáveis de ambiente do sistema")
except Exception as e:
    logger.error(f"Erro ao carregar .env: {e}")

class EmailNotifier:
    """Classe para gerenciar envio de emails de notificação"""
    
    def __init__(self):
        # Garantir que o .env seja carregado novamente no contexto atual
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)  # override=True para garantir que as variáveis sejam recarregadas
            logger.info("Arquivo .env carregado com sucesso no EmailNotifier")
        except ImportError:
            logger.warning("python-dotenv não instalado")
        
        # DEBUG: Verificar todas as variáveis de ambiente relacionadas a email
        logger.info("=== DEBUG: Verificando variáveis de ambiente ===")
        all_env_vars = {k: v for k, v in os.environ.items() if 'smtp' in k.lower() or 'email' in k.lower() or 'from' in k.lower()}
        logger.info(f"Variáveis encontradas: {all_env_vars}")
        
        # Configurações padrão para desenvolvimento/produção
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.from_name = os.getenv('FROM_NAME', 'Sistema de Gestão')
        
        logger.info(f"DEBUG: smtp_server='{self.smtp_server}'")
        logger.info(f"DEBUG: smtp_port='{self.smtp_port}'")
        logger.info(f"DEBUG: smtp_user='{self.smtp_user}'")
        logger.info(f"DEBUG: smtp_pass='{'***' if self.smtp_pass else 'None'}'")
        logger.info(f"DEBUG: from_name='{self.from_name}'")
        
        # Verificar se as configurações essenciais estão disponíveis
        self.email_enabled = bool(self.smtp_user and self.smtp_pass and self.smtp_user.strip() and self.smtp_pass.strip())
        
        logger.info(f"DEBUG: email_enabled={self.email_enabled}")
        
        if not self.email_enabled:
            logger.warning("Configurações de email incompletas. Notificações por email desabilitadas.")
            logger.info(f"SMTP_SERVER: {self.smtp_server}")
            logger.info(f"SMTP_PORT: {self.smtp_port}")
            logger.info(f"SMTP_USER: {'***@***' if self.smtp_user else 'NÃO configurado'}")
            logger.info(f"SMTP_PASS: {'Configurado' if self.smtp_pass else 'NÃO configurado'}")
            logger.info(f"FROM_NAME: {self.from_name}")
        else:
            logger.info("Sistema de email configurado e habilitado!")
            logger.info(f"Servidor: {self.smtp_server}:{self.smtp_port}")
            logger.info(f"Usuário: {self.smtp_user}")
            logger.info(f"De: {self.from_name}")
            logger.info(f"De: {self.from_name}")
    
    def _formatar_data_brasileira(self, data_str: str) -> str:
        """Formata uma data no formato brasileiro DD/MM/AAAA"""
        if not data_str or data_str == 'Não definida' or data_str == 'Nao definida':
            return data_str
        
        try:
            # Tentar diferentes formatos de entrada
            formatos_possiveis = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y']
            
            data_obj = None
            for formato in formatos_possiveis:
                try:
                    if 'T' in data_str:
                        data_str = data_str.split('T')[0]  # Remover parte do tempo se existir
                    data_obj = datetime.strptime(data_str, formato)
                    break
                except ValueError:
                    continue
            
            if data_obj:
                return data_obj.strftime('%d/%m/%Y')
            else:
                return data_str
                
        except Exception as e:
            logger.warning(f"Erro ao formatar data '{data_str}': {e}")
            return data_str
    
    def _get_email_template(self, template_name: str, **kwargs) -> str:
        """Retorna o template HTML do email baseado no nome"""
        
        # Template base simples
        base_template = """<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Notificacao - Sistema de Gestao</title>
    <style>
        body {{font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;}}
        .container {{ max-width: 600px; margin: 10px auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 18px 24px 12px 24px; text-align: left; }}
        .header h1 {{ margin: 0; font-size: 22px; font-weight: 400; text-align: left; }}
        .content {{ padding: 18px 24px 18px 24px; line-height: 1.6; text-align: left; }}
        .task-info {{ background: #f8f9fa; border-left: 4px solid #007bff; padding: 16px; margin: 18px 0; border-radius: 5px; }}
        .task-name {{ font-size: 17px; font-weight: 600; color: #333; margin-bottom: 8px; }}
        .task-details {{ color: #666; font-size: 14px; }}
        .status-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; text-transform: uppercase; }}
        .status-pendente {{ background: #fff3cd; color: #856404; }}
        .status-em-progresso {{ background: #d1ecf1; color: #0c5460; }}
        .status-concluida {{ background: #d4edda; color: #155724; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 16px 0; }}
        .btn:hover {{ background: #0056b3; }}
        .footer {{ background: #f8f9fa; padding: 16px; text-align: center; color: #666; font-size: 12px; }}
        .timestamp {{ color: #999; font-size: 12px; margin-top: 16px; text-align: center; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <div class=\"header\">
            <h1>🔔 Notificacao do Sistema</h1>
        </div>
        <div class=\"content\">
            {content}
        </div>
        <div class=\"footer\">
            <p>Esta e uma notificacao automatica do Sistema de Gestao de Projetos</p>
            <p>Para desativar notificacoes por email, entre em contato com o administrador</p>
        </div>
        <div class=\"timestamp\">
            Enviado em {timestamp}
        </div>
    </div>
</body>
</html>"""
        
        # Templates simples
        templates = {
            'tarefa_designada': """<h2 style="color: #28a745; margin-bottom: 20px;">✅ Nova Tarefa Designada</h2>
<p>Ola <strong>{usuario_nome}</strong>,</p>
<p>Voce foi designado para uma nova tarefa no projeto.</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>Data de Inicio:</strong> {data_inicio}<br>
        <strong>Data de Fim:</strong> {data_fim}<br>
        <strong>Duracao:</strong> {duracao}<br>
        <strong>Colecao:</strong> {colecao}
    </div>
</div>

<p>Clique no botao abaixo para acessar a tarefa:</p>
<a href="{projeto_url}" class="btn">Ver Tarefa</a>

<p>Boa sorte com a execucao!</p>""",
            
            'tarefa_removida': """<h2 style="color: #dc3545; margin-bottom: 20px;">❌ Tarefa Removida</h2>
<p>Ola <strong>{usuario_nome}</strong>,</p>
<p>Voce foi removido da seguinte tarefa:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}
    </div>
</div>

<p>Se voce tiver alguma duvida sobre essa alteracao, entre em contato com o administrador do projeto.</p>""",
            
            'status_alterado': """<h2 style="color: #ffc107; margin-bottom: 20px;">🔄 Status da Tarefa Alterado</h2>
<p>Ola <strong>{usuario_nome}</strong>,</p>
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

<p>Clique no botao abaixo para acessar a tarefa:</p>
<a href="{projeto_url}" class="btn">Ver Tarefa</a>""",
            
            'tarefa_concluida': """<h2 style="color: #28a745; margin-bottom: 20px;">🎉 Tarefa Concluida!</h2>
<p>Parabens <strong>{usuario_nome}</strong>!</p>
<p>Sua tarefa foi marcada como concluida:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>Status:</strong> 
        <span class="status-badge status-concluida">Concluida</span>
    </div>
</div>

<p>Excelente trabalho! Continue assim!</p>

<a href="{projeto_url}" class="btn">Ver Projeto</a>""",
            
            'tarefa_concluida_admin': """<h2 style="color: #28a745; margin-bottom: 20px;">🎉 Tarefa Concluida (Notificação Admin)</h2>
<p>Ola <strong>{admin_nome}</strong>,</p>
<p>Uma tarefa foi marcada como concluida no sistema:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>Concluida por:</strong> {usuario_alteracao}<br>
        <strong>Status:</strong> 
        <span class="status-badge status-concluida">Concluida</span>
    </div>
</div>

<p>Como administrador, voce foi notificado sobre esta conclusao.</p>

<a href="{projeto_url}" class="btn">Ver Projeto</a>""",
            
            'tarefa_progresso_admin': """<h2 style="color: #17a2b8; margin-bottom: 20px;">🚀 Tarefa em Progresso (Notificação Admin)</h2>
<p>Ola <strong>{admin_nome}</strong>,</p>
<p>Uma tarefa foi iniciada no sistema:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>Iniciada por:</strong> {usuario_alteracao}<br>
        <strong>Status:</strong> 
        <span class="status-badge status-em-progresso">Em Progresso</span>
    </div>
</div>

<p>Como administrador, voce foi notificado sobre o inicio desta tarefa.</p>

<a href="{projeto_url}" class="btn">Ver Projeto</a>""",
            
            'projeto_criado': """<h2 style="color: #17a2b8; margin-bottom: 20px;">🚀 Novo Projeto Criado</h2>
<p>Ola <strong>{usuario_nome}</strong>,</p>
<p>Um novo projeto foi criado e voce tem acesso a ele:</p>

<div class="task-info">
    <div class="task-name">{projeto_nome}</div>
    <div class="task-details">
        <strong>Descricao:</strong> {projeto_descricao}<br>
        <strong>Data de Inicio:</strong> {data_inicio}<br>
        <strong>Data de Fim:</strong> {data_fim}<br>
        <strong>Responsavel:</strong> {responsavel}
    </div>
</div>

<p>Clique no botao abaixo para acessar o projeto:</p>
<a href="{projeto_url}" class="btn">Ver Projeto</a>""",
            
            'tarefas_pendentes_liberacao': """<h2 style="color: #28a745; margin-bottom: 20px;">🎯 Acesso Liberado - Tarefas Pendentes</h2>
<p>Ola <strong>{usuario_nome}</strong>,</p>
<p>O acesso ao projeto <strong>"{projeto_nome}"</strong> foi liberado para voce! Você foi designado para as seguintes tarefas:</p>

{tarefas_lista}

<p>Clique no botao abaixo para acessar o projeto e visualizar todas as suas tarefas:</p>
<a href="{projeto_url}" class="btn">Ver Projeto</a>

<p>Boa sorte com a execucao das tarefas!</p>""",
            
            'tarefa_atrasada': """<h2 style="color: #dc3545; margin-bottom: 20px;">⚠️ Tarefa Atrasada</h2>
<p>Ola <strong>{usuario_nome}</strong>,</p>
<p>A seguinte tarefa esta atrasada e precisa de atencao imediata:</p>

<div class="task-info">
    <div class="task-name">{tarefa_nome}</div>
    <div class="task-details">
        <strong>Projeto:</strong> {projeto_nome}<br>
        <strong>{data_label}:</strong> {data_referencia}<br>
        <strong>Status:</strong> 
        <span class="status-badge status-{status_class}">{status}</span><br>
        <strong>Dias de Atraso:</strong> {dias_atraso}
    </div>
</div>

<p>{mensagem_atraso} Por favor, atualize o status ou entre em contato com o administrador do projeto para discutir prazos.</p>

<p>Clique no botao abaixo para acessar a tarefa:</p>
<a href="{projeto_url}" class="btn">Ver Tarefa</a>

<p>Atencao: Tarefas atrasadas podem impactar o cronograma do projeto.</p>"""
        }
        
        template = templates.get(template_name, '')
        if not template:
            logger.error(f"Template '{template_name}' nao encontrado")
            return ""
        
        # Substituir variáveis no template
        content = template.format(**kwargs)
        
        # Formatar timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y as %H:%M")
        
        return base_template.format(content=content, timestamp=timestamp)
    
    def _get_status_class(self, status: str) -> str:
        """Retorna a classe CSS para o status da tarefa"""
        status_map = {
            'pendente': 'pendente',
            'em progresso': 'em-progresso',
            'concluida': 'concluida'
        }
        return status_map.get(status, 'pendente')
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Envia o email usando SMTP"""
        if not self.email_enabled:
            logger.warning("Email desabilitado - nao foi possivel enviar para %s", to_email)
            return False

        try:
            # Criar mensagem
            from email.header import Header
            from email.utils import formataddr, make_msgid, formatdate
            import time

            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((str(Header(self.from_name, 'utf-8')), self.smtp_user))
            msg['To'] = to_email
            msg['Subject'] = subject

            # Adicionar headers importantes para melhor entregabilidade
            msg['Message-ID'] = make_msgid(domain=self.smtp_server.split('.')[-2] + '.' + self.smtp_server.split('.')[-1])
            msg['Date'] = formatdate(time.time(), localtime=True)
            msg['X-Mailer'] = 'Sistema de Gestão de Projetos v2.0'
            msg['X-Priority'] = '3'  # Normal priority
            msg['Return-Path'] = self.smtp_user

            # Adicionar conteúdo HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Conectar ao servidor SMTP
            if self.smtp_port == 465:
                # Porta 465 usa SSL direto
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                server.login(self.smtp_user, self.smtp_pass)
            else:
                # Outras portas (587, 25) usam STARTTLS
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
                data_inicio=self._formatar_data_brasileira(tarefa_info.get('data_inicio', 'Nao definida')),
                data_fim=self._formatar_data_brasileira(tarefa_info.get('data_fim', 'Nao definida')),
                duracao=tarefa_info.get('duracao', 'Nao definida'),
                colecao=tarefa_info.get('colecao', 'Nao definida'),
                projeto_url=projeto_url
            )
            
            subject = f"🔔 Nova Tarefa Designada: {tarefa_info.get('nome', '')}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificacao de tarefa designada: {str(e)}")
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
            logger.error(f"Erro ao criar notificacao de tarefa removida: {str(e)}")
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
            logger.error(f"Erro ao criar notificacao de status alterado: {str(e)}")
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
            
            subject = f"🎉 Tarefa Concluida: {tarefa_info.get('nome', '')}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificacao de tarefa concluida: {str(e)}")
            return False
    
    def notificar_tarefa_concluida_admin(self, admin_email: str, admin_nome: str, tarefa_info: Dict[str, Any], usuario_alteracao: str, projeto_url: str) -> bool:
        """Notifica administrador sobre conclusão de tarefa"""
        try:
            html_content = self._get_email_template('tarefa_concluida_admin',
                admin_nome=admin_nome,
                tarefa_nome=tarefa_info.get('nome', ''),
                projeto_nome=tarefa_info.get('projeto_nome', ''),
                usuario_alteracao=usuario_alteracao,
                projeto_url=projeto_url
            )
            
            subject = f"🎉 Tarefa Concluida (Admin): {tarefa_info.get('nome', '')}"
            return self._send_email(admin_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificacao de tarefa concluida para admin: {str(e)}")
            return False
    
    def notificar_tarefa_progresso_admin(self, admin_email: str, admin_nome: str, tarefa_info: Dict[str, Any], usuario_alteracao: str, projeto_url: str) -> bool:
        """Notifica administrador sobre tarefa iniciada (em progresso)"""
        try:
            html_content = self._get_email_template('tarefa_progresso_admin',
                admin_nome=admin_nome,
                tarefa_nome=tarefa_info.get('nome', ''),
                projeto_nome=tarefa_info.get('projeto_nome', ''),
                usuario_alteracao=usuario_alteracao,
                projeto_url=projeto_url
            )
            
            subject = f"🚀 Tarefa em Progresso (Admin): {tarefa_info.get('nome', '')}"
            return self._send_email(admin_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificacao de tarefa em progresso para admin: {str(e)}")
            return False
    
    def notificar_projeto_criado(self, usuario_email: str, usuario_nome: str, projeto_info: Dict[str, Any], projeto_url: str) -> bool:
        """Notifica usuário sobre novo projeto criado"""
        try:
            html_content = self._get_email_template('projeto_criado',
                usuario_nome=usuario_nome,
                projeto_nome=projeto_info.get('nome', ''),
                projeto_descricao=projeto_info.get('descricao', 'Sem descricao'),
                data_inicio=self._formatar_data_brasileira(projeto_info.get('data_inicio', 'Nao definida')),
                data_fim=self._formatar_data_brasileira(projeto_info.get('data_fim', 'Nao definida')),
                responsavel=projeto_info.get('responsavel', 'Nao definido'),
                projeto_url=projeto_url
            )
            
            subject = f"🚀 Novo Projeto: {projeto_info.get('nome', '')}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificacao de projeto criado: {str(e)}")
            return False
    
    def notificar_tarefas_pendentes_liberacao(self, usuario_email: str, usuario_nome: str, projeto_nome: str, tarefas: List[Dict[str, Any]], projeto_url: str) -> bool:
        """Notifica usuário sobre múltiplas tarefas pendentes quando o acesso ao projeto é liberado"""
        try:
            # Criar lista HTML das tarefas
            tarefas_html = ""
            for i, tarefa in enumerate(tarefas, 1):
                status_class = self._get_status_class(tarefa.get('status', 'pendente'))
                tarefas_html += f"""
<div class="task-info">
    <div class="task-name">{i}. {tarefa.get('nome', '')}</div>
    <div class="task-details">
        <strong>Status:</strong> <span class="status-badge status-{status_class}">{tarefa.get('status', 'Pendente')}</span><br>
        <strong>Data de Inicio:</strong> {self._formatar_data_brasileira(tarefa.get('data_inicio', 'Nao definida'))}<br>
        <strong>Data de Fim:</strong> {self._formatar_data_brasileira(tarefa.get('data_fim', 'Nao definida'))}<br>
        <strong>Duracao:</strong> {tarefa.get('duracao', 'Nao definida')}<br>
        <strong>Colecao:</strong> {tarefa.get('colecao', 'Nao definida')}
    </div>
</div>"""
            
            html_content = self._get_email_template('tarefas_pendentes_liberacao',
                usuario_nome=usuario_nome,
                projeto_nome=projeto_nome,
                tarefas_lista=tarefas_html,
                projeto_url=projeto_url
            )
            
            subject = f"🎯 Acesso Liberado - {len(tarefas)} tarefa(s) pendente(s) em {projeto_nome}"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificacao de tarefas pendentes liberacao: {str(e)}")
            return False
    
    def notificar_tarefa_atrasada(self, usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], projeto_url: str, dias_atraso: int, tipo_atraso: str = 'conclusao') -> bool:
        """Notifica usuário sobre tarefa atrasada"""
        try:
            # Determinar qual data mostrar baseado no tipo de atraso
            if tipo_atraso == 'inicio':
                data_referencia = tarefa_info.get('data_inicio', 'Nao definida')
                data_label = 'Data de Inicio'
                mensagem_atraso = 'Esta tarefa deveria ter sido iniciada até a data de início.'
            else:
                data_referencia = tarefa_info.get('data_fim', 'Nao definida')
                data_label = 'Data de Fim'
                mensagem_atraso = 'Esta tarefa deveria ter sido concluída até a data limite.'
            
            html_content = self._get_email_template('tarefa_atrasada',
                usuario_nome=usuario_nome,
                tarefa_nome=tarefa_info.get('nome', ''),
                projeto_nome=tarefa_info.get('projeto_nome', ''),
                data_referencia=self._formatar_data_brasileira(data_referencia),
                data_label=data_label,
                status=tarefa_info.get('status', 'pendente'),
                status_class=self._get_status_class(tarefa_info.get('status', 'pendente')),
                dias_atraso=dias_atraso,
                mensagem_atraso=mensagem_atraso,
                projeto_url=projeto_url
            )
            
            subject = f"⚠️ Tarefa Atrasada: {tarefa_info.get('nome', '')} - {dias_atraso} dia(s) de atraso"
            return self._send_email(usuario_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Erro ao criar notificacao de tarefa atrasada: {str(e)}")
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

def notificar_tarefa_concluida_admin(admin_email: str, admin_nome: str, tarefa_info: Dict[str, Any], usuario_alteracao: str, projeto_url: str) -> bool:
    """Notifica administrador sobre conclusão de tarefa"""
    return email_notifier.notificar_tarefa_concluida_admin(admin_email, admin_nome, tarefa_info, usuario_alteracao, projeto_url)

def notificar_tarefa_progresso_admin(admin_email: str, admin_nome: str, tarefa_info: Dict[str, Any], usuario_alteracao: str, projeto_url: str) -> bool:
    """Notifica administrador sobre tarefa iniciada (em progresso)"""
    return email_notifier.notificar_tarefa_progresso_admin(admin_email, admin_nome, tarefa_info, usuario_alteracao, projeto_url)

def notificar_projeto_criado(usuario_email: str, usuario_nome: str, projeto_info: Dict[str, Any], projeto_url: str) -> bool:
    """Notifica usuário sobre novo projeto criado"""
    return email_notifier.notificar_projeto_criado(usuario_email, usuario_nome, projeto_info, projeto_url)

def notificar_tarefas_pendentes_liberacao(usuario_email: str, usuario_nome: str, projeto_nome: str, tarefas: List[Dict[str, Any]], projeto_url: str) -> bool:
    """Notifica usuário sobre múltiplas tarefas pendentes quando o acesso ao projeto é liberado"""
    return email_notifier.notificar_tarefas_pendentes_liberacao(usuario_email, usuario_nome, projeto_nome, tarefas, projeto_url)

def notificar_tarefa_atrasada(usuario_email: str, usuario_nome: str, tarefa_info: Dict[str, Any], projeto_url: str, dias_atraso: int, tipo_atraso: str = 'conclusao') -> bool:
    """Notifica usuário sobre tarefa atrasada"""
    return email_notifier.notificar_tarefa_atrasada(usuario_email, usuario_nome, tarefa_info, projeto_url, dias_atraso, tipo_atraso)
