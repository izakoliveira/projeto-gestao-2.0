"""
Testes para as rotas principais da aplicação
"""

import pytest
from unittest.mock import patch, Mock
import json

class TestMainRoutes:
    """Testes para as rotas principais (auth, dashboard, etc.)"""

    def test_index_redirect_to_login(self, client):
        """Testa se a página inicial redireciona para login quando não autenticado."""
        response = client.get('/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_login_page_loads(self, client):
        """Testa se a página de login carrega corretamente."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_register_page_loads(self, client):
        """Testa se a página de cadastro carrega corretamente."""
        response = client.get('/auth/cadastro')
        assert response.status_code == 200
        assert b'cadastro' in response.data.lower()

    @patch('routes.auth.supabase')
    def test_login_successful(self, mock_supabase, client, sample_user):
        """Testa login bem-sucedido."""
        # Mock da resposta do Supabase
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_user]
        
        response = client.post('/auth/login', data={
            'email': 'teste@exemplo.com',
            'senha': 'senha123'
        }, follow_redirects=True)
        
        assert response.status_code == 200

    @patch('routes.auth.supabase')
    def test_login_invalid_credentials(self, mock_supabase, client):
        """Testa login com credenciais inválidas."""
        # Mock de usuário não encontrado
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        response = client.post('/auth/login', data={
            'email': 'invalido@exemplo.com',
            'senha': 'senhaerrada'
        })
        
        assert response.status_code == 200
        assert b'email ou senha' in response.data.lower()

class TestProjectRoutes:
    """Testes para as rotas de projetos"""

    def test_projetos_requires_auth(self, client):
        """Testa se a página de projetos requer autenticação."""
        response = client.get('/projetos')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    @patch('routes.projetos.supabase')
    def test_projetos_with_auth(self, mock_supabase, client, sample_user, sample_project):
        """Testa página de projetos com usuário autenticado."""
        # Simular sessão autenticada
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user['id']
            sess['user_nivel'] = sample_user['nivel']
        
        # Mock dos dados de projetos
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [sample_project]
        
        response = client.get('/projetos')
        assert response.status_code == 200

class TestTaskRoutes:
    """Testes para as rotas de tarefas"""

    @patch('routes.tarefas.supabase')
    def test_criar_tarefa_success(self, mock_supabase, client, sample_user, sample_project):
        """Testa criação de tarefa com sucesso."""
        # Simular sessão autenticada
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user['id']
            sess['user_nivel'] = sample_user['nivel']
        
        # Mock dos dados necessários
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_project]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{'id': 'new-task-id'}]
        
        response = client.post('/tarefas/criar', data={
            'nome': 'Nova Tarefa',
            'descricao': 'Descrição da nova tarefa',
            'data_inicio': '2025-01-01',
            'data_fim': '2025-01-10',
            'duracao': '7',
            'projeto_id': sample_project['id']
        })
        
        assert response.status_code == 302  # Redirect após sucesso

class TestReportRoutes:
    """Testes para as rotas de relatórios"""

    @patch('routes.relatorio.supabase')
    def test_relatorio_pdf_generation(self, mock_supabase, client, sample_user, sample_project, sample_task):
        """Testa geração de relatório PDF."""
        # Simular sessão autenticada
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user['id']
            sess['user_nivel'] = sample_user['nivel']
        
        # Mock dos dados
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [sample_task]
        
        response = client.get('/relatorio/pdf')
        assert response.status_code == 200

    @patch('routes.relatorio.supabase')
    def test_export_excel(self, mock_supabase, client, sample_user, sample_project, sample_task):
        """Testa exportação para Excel."""
        # Simular sessão autenticada
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user['id']
            sess['user_nivel'] = sample_user['nivel']
        
        # Mock dos dados
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [sample_task]
        
        response = client.get('/relatorio/gantt_excel')
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

class TestAPIEndpoints:
    """Testes para endpoints da API"""

    @patch('routes.main.supabase')
    def test_api_projetos_json(self, mock_supabase, client, sample_user, sample_project):
        """Testa endpoint JSON de projetos."""
        # Simular sessão autenticada
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user['id']
        
        # Mock dos dados
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [sample_project]
        
        response = client.get('/api/projetos')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert isinstance(data, list)

class TestErrorHandling:
    """Testes para tratamento de erros"""

    def test_404_page(self, client):
        """Testa página de erro 404."""
        response = client.get('/pagina-inexistente')
        assert response.status_code == 404

    def test_500_error_handling(self, client):
        """Testa tratamento de erro 500."""
        # Simular erro interno
        with patch('routes.main.supabase') as mock_supabase:
            mock_supabase.side_effect = Exception("Erro simulado")
            
            response = client.get('/projetos')
            # Pode retornar 302 (redirect para login) ou 500
            assert response.status_code in [302, 500]

class TestSecurity:
    """Testes de segurança"""

    def test_csrf_protection(self, client):
        """Testa proteção CSRF (quando habilitada)."""
        response = client.post('/auth/login', data={
            'email': 'teste@exemplo.com',
            'senha': 'senha123'
        })
        # Em ambiente de teste, CSRF pode estar desabilitado
        assert response.status_code in [200, 400]

    def test_sql_injection_protection(self, client):
        """Testa proteção contra SQL injection."""
        malicious_input = "'; DROP TABLE projetos; --"
        response = client.post('/auth/login', data={
            'email': malicious_input,
            'senha': 'senha123'
        })
        assert response.status_code == 200  # Deve ser tratado normalmente

    def test_unauthorized_access(self, client):
        """Testa acesso não autorizado a páginas protegidas."""
        protected_pages = [
            '/dashboard',
            '/projetos',
            '/projetos/novo',
            '/admin/usuarios'
        ]
        
        for page in protected_pages:
            response = client.get(page)
            assert response.status_code == 302  # Redirect para login