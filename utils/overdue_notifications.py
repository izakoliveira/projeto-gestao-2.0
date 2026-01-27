#!/usr/bin/env python3
"""
Sistema de Notificações de Tarefas Atrasadas
Verifica periodicamente tarefas atrasadas e envia notificações por email
para administradores e responsáveis pelas tarefas
"""

import os
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

# Importar funções do cliente Supabase para cache
try:
    from supabase_client import (
        get_notification_cache,
        add_to_notification_cache,
        remove_from_notification_cache,
        cleanup_old_notification_cache,
        is_task_notified
    )
except ImportError:
    logger.error("Erro ao importar funções do cache do Supabase")
    get_notification_cache = None

# Importar função de validação de tarefas atrasadas (mesma lógica da tela detalhes_projeto)
try:
    from .validators import verificar_tarefa_atrasada
except ImportError:
    logger.error("Erro ao importar função verificar_tarefa_atrasada")
    verificar_tarefa_atrasada = None

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OverdueNotificationManager:
    """Gerenciador de notificações de tarefas atrasadas"""

    def __init__(self):
        # Configurações do Supabase
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            logger.error("Configurações do Supabase não encontradas")
            self.supabase = None
        else:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Conectado ao Supabase para notificações atrasadas")

        # Configurações de agendamento
        self.check_interval_hours = int(os.getenv('OVERDUE_CHECK_INTERVAL_HOURS', '24'))  # Verificar a cada 24 horas por padrão
        self.notification_enabled = bool(os.getenv('OVERDUE_NOTIFICATIONS_ENABLED', 'true').lower() == 'true')

        # Controle de execução
        self.running = False
        self.thread = None

        # Cache para evitar notificações duplicadas (carregado do banco)
        self.last_notification_cache = self._load_notification_cache()

        logger.info(f"Cache de notificações carregado: {len(self.last_notification_cache)} entradas")

    def _load_notification_cache(self) -> Dict[str, datetime]:
        """Carrega o cache de notificações do banco de dados"""
        try:
            if get_notification_cache is None:
                logger.error("Funções do cache do Supabase não disponíveis")
                return {}

            cache_data = get_notification_cache()

            # Converter strings de data para objetos datetime
            cache = {}
            for task_id, timestamp_str in cache_data.items():
                try:
                    # Supabase retorna timestamp como string ISO
                    cache[task_id] = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Timestamp inválido para tarefa {task_id}: {timestamp_str} - {e}")
                    continue

            # Limpar entradas antigas (mais de 30 dias) - será feito no banco também
            cutoff_date = datetime.now() - timedelta(days=30)
            cache = {k: v for k, v in cache.items() if v > cutoff_date}

            logger.info(f"Cache carregado com {len(cache)} entradas válidas")
            return cache
        except Exception as e:
            logger.error(f"Erro ao carregar cache de notificações: {str(e)}")
            return {}

    def _save_notification_cache(self):
        """Salva o cache de notificações no banco (não necessário - operações são síncronas)"""
        # Com banco de dados, as operações são síncronas, então não precisamos salvar explicitamente
        logger.debug(f"Cache em memória: {len(self.last_notification_cache)} entradas")

    def _cleanup_old_cache_entries(self):
        """Remove entradas antigas do cache no banco de dados (mais de 7 dias)"""
        try:
            if cleanup_old_notification_cache is not None:
                success = cleanup_old_notification_cache(days=7)
                if success:
                    logger.info("Cache antigo limpo no banco de dados")
                    # Recarregar cache após limpeza
                    self.last_notification_cache = self._load_notification_cache()
                else:
                    logger.warning("Falha ao limpar cache antigo no banco")
        except Exception as e:
            logger.error(f"Erro ao limpar cache antigo: {str(e)}")

    def start_background_monitoring(self):
        """Inicia o monitoramento em background"""
        if not self.notification_enabled:
            logger.info("Notificações de tarefas atrasadas desabilitadas")
            return

        if not self.supabase:
            logger.error("Não é possível iniciar monitoramento - Supabase não configurado")
            return

        if self.running:
            logger.warning("Monitoramento já está em execução")
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.thread.start()
        logger.info(f"Monitoramento de tarefas atrasadas iniciado (intervalo: {self.check_interval_hours} horas)")

    def stop_background_monitoring(self):
        """Para o monitoramento em background"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Monitoramento de tarefas atrasadas parado")

    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                self.check_and_notify_overdue_tasks()
            except Exception as e:
                logger.error(f"Erro no monitoramento de tarefas atrasadas: {str(e)}")

            # Aguardar até a próxima verificação
            time.sleep(self.check_interval_hours * 3600)  # Converter horas para segundos

    def check_and_notify_overdue_tasks(self):
        """Verifica tarefas atrasadas e envia notificações"""
        try:
            # Limpeza automática do cache antigo no início de cada verificação
            self._cleanup_old_cache_entries()

            logger.info("Verificando tarefas atrasadas...")

            # Buscar tarefas atrasadas
            overdue_tasks = self._get_overdue_tasks()

            if not overdue_tasks:
                logger.info("Nenhuma tarefa atrasada encontrada")
                return

            logger.info(f"Encontradas {len(overdue_tasks)} tarefas atrasadas")

            # Para cada tarefa atrasada, enviar notificações
            for task in overdue_tasks:
                try:
                    self._notify_task_overdue(task)
                except Exception as e:
                    logger.error(f"Erro ao notificar tarefa atrasada {task.get('id')}: {str(e)}")

        except Exception as e:
            logger.error(f"Erro ao verificar tarefas atrasadas: {str(e)}")

    def _get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Busca tarefas atrasadas no banco de dados usando a mesma lógica da tela detalhes_projeto"""
        try:
            logger.info("Buscando tarefas atrasadas usando lógica da tela detalhes_projeto...")

            # Buscar TODAS as tarefas (não apenas as não concluídas)
            # A validação será feita pela função verificar_tarefa_atrasada
            tarefas_response = self.supabase.table('tarefas').select(
                'id, nome, data_inicio, data_fim, status, projeto_id, usuario_id'
            ).execute()

            logger.info(f"Query retornou {len(tarefas_response.data)} tarefas para análise")

            tasks = []
            for tarefa in tarefas_response.data:
                # Usar a MESMA lógica da tela detalhes_projeto
                if verificar_tarefa_atrasada is None:
                    logger.error("Função verificar_tarefa_atrasada não disponível")
                    continue

                # Verificar se a tarefa está atrasada usando a mesma lógica da tela
                if not verificar_tarefa_atrasada(tarefa):
                    continue

                logger.info(f"✅ Tarefa identificada como atrasada: {tarefa['id']} - {tarefa['nome']} (status: {tarefa['status']})")

                # Buscar informações do projeto
                projeto_response = self.supabase.table('projetos').select('nome').eq('id', tarefa['projeto_id']).execute()
                projeto_nome = projeto_response.data[0]['nome'] if projeto_response.data else 'Projeto não encontrado'

                # Buscar informações do usuário
                usuario_response = self.supabase.table('usuarios').select('email, nome').eq('id', tarefa['usuario_id']).execute()
                usuario_info = usuario_response.data[0] if usuario_response.data else {'email': 'email@nao.encontrado', 'nome': 'Usuário não encontrado'}

                # Calcular dias de atraso baseado na data_fim (se existir)
                dias_atraso = 0
                if tarefa.get('data_fim'):
                    try:
                        data_fim = datetime.fromisoformat(tarefa['data_fim'].split('T')[0]).date()
                        today = datetime.now().date()
                        if data_fim < today:
                            dias_atraso = (today - data_fim).days
                    except Exception as e:
                        logger.warning(f"Erro ao calcular dias de atraso para tarefa {tarefa['id']}: {str(e)}")

                task_info = {
                    'id': tarefa['id'],
                    'nome': tarefa['nome'],
                    'data_inicio': tarefa.get('data_inicio'),
                    'data_fim': tarefa.get('data_fim'),
                    'status': tarefa['status'],
                    'dias_atraso': dias_atraso,
                    'projeto_id': tarefa['projeto_id'],
                    'projeto_nome': projeto_nome,
                    'usuario_id': tarefa['usuario_id'],
                    'usuario_email': usuario_info['email'],
                    'usuario_nome': usuario_info['nome']
                }
                tasks.append(task_info)

            logger.info(f"Total de tarefas identificadas como atrasadas: {len(tasks)}")
            return tasks

        except Exception as e:
            logger.error(f"Erro ao buscar tarefas atrasadas: {str(e)}")
            return []

    def _notify_task_overdue(self, task: Dict[str, Any]):
        """Envia notificações para uma tarefa atrasada"""
        task_id = task['id']
        usuario_email = task['usuario_email']
        usuario_nome = task['usuario_nome']
        dias_atraso = task['dias_atraso']

        # Verificar se já notificamos recentemente (evitar spam)
        if is_task_notified is not None and is_task_notified(task_id):
            logger.debug(f"Tarefa {task_id} já foi notificada hoje (cache do banco)")
            return

        # VERIFICAÇÃO FINAL: Confirmar se a tarefa ainda está atrasada usando a mesma lógica da tela
        try:
            logger.info(f"Verificação final da tarefa {task_id} ({task['nome']}) usando lógica da tela detalhes_projeto")

            # Buscar dados atuais da tarefa
            current_task = self.supabase.table('tarefas').select('id, nome, data_inicio, data_fim, status').eq('id', task_id).execute()

            if not current_task.data:
                logger.info(f"Tarefa {task_id} não encontrada - pode ter sido excluída")
                return

            current_task_data = current_task.data[0]
            logger.info(f"Status atual da tarefa {task_id}: status='{current_task_data['status']}', data_inicio='{current_task_data.get('data_inicio')}', data_fim='{current_task_data.get('data_fim')}'")

            # Usar a MESMA função da tela detalhes_projeto para verificar se está atrasada
            if verificar_tarefa_atrasada is None:
                logger.error("Função verificar_tarefa_atrasada não disponível para verificação final")
                return

            if not verificar_tarefa_atrasada(current_task_data):
                logger.info(f"🚫 BLOQUEADO: Tarefa {task_id} ({task['nome']}) NÃO ESTÁ ATRASADA pela lógica da tela detalhes_projeto")
                return

            # Recalcular dias de atraso baseado na lógica da função
            dias_atraso = 0
            tipo_atraso = 'conclusao'  # padrão: atraso na conclusão
            
            # Determinar o tipo de atraso baseado na lógica da função verificar_tarefa_atrasada
            status = current_task_data.get('status', '').lower()
            data_inicio = current_task_data.get('data_inicio')
            data_fim = current_task_data.get('data_fim')
            today = datetime.now().date()
            
            # Lógica 1: Tarefa pendente com data de início passada
            if status == 'pendente' and data_inicio:
                try:
                    data_inicio_obj = datetime.fromisoformat(data_inicio.split('T')[0]).date()
                    if data_inicio_obj < today:
                        tipo_atraso = 'inicio'
                        dias_atraso = (today - data_inicio_obj).days
                except Exception:
                    pass
            
            # Lógica 2: Tarefa não concluída com data de fim passada (se não foi determinado como atraso de início)
            if tipo_atraso == 'conclusao' and data_fim and status not in ['concluída', 'concluida']:
                try:
                    data_fim_obj = datetime.fromisoformat(data_fim.split('T')[0]).date()
                    if data_fim_obj < today:
                        dias_atraso = (today - data_fim_obj).days
                except Exception as e:
                    logger.warning(f"Erro ao recalcular dias de atraso para tarefa {task_id}: {str(e)}")

            task['dias_atraso'] = dias_atraso
            task['tipo_atraso'] = tipo_atraso
            logger.info(f"✅ APROVADO: Tarefa {task_id} ({task['nome']}) está atrasada pela lógica da tela detalhes_projeto - Tipo: {tipo_atraso}, Dias: {dias_atraso}")

        except Exception as e:
            logger.error(f"Erro na verificação final da tarefa {task_id}: {str(e)}")
            logger.warning(f"🚫 BLOQUEADO por erro: Não enviando notificação para tarefa {task_id}")
            return

        # Notificar responsável pela tarefa
        try:
            from .email_notifications import notificar_tarefa_atrasada
        except ImportError:
            logger.error("Não foi possível importar função de notificação por email")
            return

        # URL do projeto (assumindo que está rodando localmente)
        projeto_url = f"http://localhost:5000/projeto/{task['projeto_id']}"

        success = notificar_tarefa_atrasada(
            usuario_email=usuario_email,
            usuario_nome=usuario_nome,
            tarefa_info=task,
            projeto_url=projeto_url,
            dias_atraso=dias_atraso,
            tipo_atraso=tipo_atraso
        )

        if success:
            logger.info(f"Notificação enviada para responsável: {usuario_email}")
        else:
            logger.error(f"Falha ao enviar notificação para responsável: {usuario_email}")

        # Também notificar administradores
        self._notify_admins_about_overdue_task(task, projeto_url)

        # Registrar no cache do banco de dados
        if add_to_notification_cache is not None:
            success = add_to_notification_cache(task_id)
            if success:
                logger.debug(f"Tarefa {task_id} registrada no cache do banco")
                # Atualizar cache em memória
                self.last_notification_cache[task_id] = datetime.now()
            else:
                logger.warning(f"Falha ao registrar tarefa {task_id} no cache do banco")
        else:
            # Fallback para cache em memória se banco não estiver disponível
            self.last_notification_cache[task_id] = datetime.now()

        # Limpeza periódica de entradas antigas no banco (a cada 50 notificações)
        if len(self.last_notification_cache) % 50 == 0:
            self._cleanup_old_cache_entries()

    def _notify_admins_about_overdue_task(self, task: Dict[str, Any], projeto_url: str):
        """Notifica administradores sobre tarefa atrasada"""
        try:
            # Buscar administradores
            admins_response = self.supabase.table('usuarios_admin').select('usuario_id, usuarios!usuarios_admin_usuario_id_fkey(email, nome)').execute()

            for admin_item in admins_response.data:
                admin_email = admin_item['usuarios']['email']
                admin_nome = admin_item['usuarios']['nome']

                # Usar a mesma função de notificação, mas com mensagem para admin
                try:
                    from .email_notifications import notificar_tarefa_atrasada
                except ImportError:
                    continue

                # Modificar tarefa_info para incluir contexto de admin
                admin_task_info = task.copy()
                admin_task_info['nome'] = f"[ADMIN] {task['nome']}"

                success = notificar_tarefa_atrasada(
                    usuario_email=admin_email,
                    usuario_nome=admin_nome,
                    tarefa_info=admin_task_info,
                    projeto_url=projeto_url,
                    dias_atraso=task['dias_atraso']
                )

                if success:
                    logger.info(f"Notificação enviada para admin: {admin_email}")
                else:
                    logger.error(f"Falha ao enviar notificação para admin: {admin_email}")

        except Exception as e:
            logger.error(f"Erro ao notificar administradores sobre tarefa atrasada: {str(e)}")

    def force_check_now(self):
        """Força uma verificação imediata (para testes/debugging)"""
        if not self.running:
            logger.warning("Monitoramento não está em execução - executando verificação única")
            self.check_and_notify_overdue_tasks()
        else:
            logger.info("Executando verificação forçada...")
            self.check_and_notify_overdue_tasks()


# Instância global do gerenciador
overdue_manager = OverdueNotificationManager()


def start_overdue_monitoring():
    """Inicia o monitoramento de tarefas atrasadas"""
    overdue_manager.start_background_monitoring()


def stop_overdue_monitoring():
    """Para o monitoramento de tarefas atrasadas"""
    overdue_manager.stop_background_monitoring()


def check_overdue_tasks_now():
    """Verifica tarefas atrasadas imediatamente"""
    overdue_manager.force_check_now()