"""
Configuração de testes para o Sistema de Gestão de Projetos 2.0
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Fixture para criar instância da aplicação Flask para testes."""
    # Mock das variáveis de ambiente
    with patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'FLASK_SECRET_KEY': 'test-secret-key',
        'FLASK_ENV': 'testing'
    }):
        # Mock do cliente Supabase
        with patch('supabase_client.supabase') as mock_supabase:
            mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
            
            from app_producao import create_app
            app = create_app()
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            
            yield app

@pytest.fixture
def client(app):
    """Fixture para criar cliente de teste."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture para criar runner de comandos."""
    return app.test_cli_runner()

@pytest.fixture
def mock_supabase():
    """Fixture para mock do Supabase."""
    with patch('supabase_client.supabase') as mock:
        # Configurar comportamento padrão do mock
        mock.table.return_value.select.return_value.execute.return_value.data = []
        mock.table.return_value.insert.return_value.execute.return_value.data = [{'id': 'test-id'}]
        mock.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{'id': 'test-id'}]
        mock.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
        
        yield mock

@pytest.fixture
def sample_user():
    """Fixture com dados de usuário de exemplo."""
    return {
        'id': 'user-123',
        'email': 'teste@exemplo.com',
        'nome': 'Usuário Teste',
        'nivel': 'admin'
    }

@pytest.fixture
def sample_project():
    """Fixture com dados de projeto de exemplo."""
    return {
        'id': 'proj-123',
        'nome': 'Projeto Teste',
        'descricao': 'Descrição do projeto teste',
        'status': 'ativo',
        'usuario_id': 'user-123'
    }

@pytest.fixture
def sample_task():
    """Fixture com dados de tarefa de exemplo."""
    return {
        'id': 'task-123',
        'nome': 'Tarefa Teste',
        'descricao': 'Descrição da tarefa teste',
        'data_inicio': '2025-01-01',
        'data_fim': '2025-01-10',
        'duracao': 7,
        'status': 'pendente',
        'projeto_id': 'proj-123',
        'usuario_id': 'user-123'
    }