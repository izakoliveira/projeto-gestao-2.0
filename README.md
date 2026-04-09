# Sistema de Gestão de Projetos v2.0

Sistema web moderno para gestão completa de projetos, desenvolvido em Python Flask com interface responsiva.

## 🚀 Funcionalidades Principais

- **Gestão de Projetos**: Criação, edição e acompanhamento de projetos
- **Controle de Tarefas**: Sistema completo de tarefas com predecessoras e dependências
- **Organização por Coleções**: Agrupamento automático de tarefas por coleção baseado no nome do projeto
- **Relatórios**: Geração de relatórios em Excel com dados detalhados
- **Controle de Usuários**: Sistema de permissões e níveis de acesso
- **Interface Moderna**: Design responsivo e intuitivo

## � App Mobile

O sistema inclui um **servidor dedicado para app mobile** completamente independente:

### Servidor Mobile Separado
- **Arquivo**: `app_mobile.py`
- **Porta**: 5001 (diferente do sistema principal)
- **Propósito**: API exclusiva para app React Native
- **Vantagens**: Leve, rápido, sem dependências do sistema web

### Como Usar
1. Execute: `INICIAR_SERVIDOR_MOBILE.bat` (Windows)
2. Ou: `python app_mobile.py`
3. App mobile se conecta automaticamente à porta 5001

### Documentação Detalhada
Veja `SERVIDOR_MOBILE_README.md` para informações completas.

## �🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask
- **Banco de Dados**: Supabase (PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript
- **Relatórios**: ReportLab, Pandas, OpenPyXL
- **Interface**: Tkinter (instalador)
- **Empacotamento**: PyInstaller

## 📦 Instalação

### Instalação Automática (Recomendado)
1. Execute o arquivo `instalador_sistema.py`
2. Siga as instruções do assistente de instalação
3. O sistema será instalado automaticamente

### Instalação Manual
1. Instale Python 3.8 ou superior
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as credenciais do Supabase
4. Execute: `python app_producao.py`

## 🔧 Configuração

1. Configure as credenciais do Supabase em `supabase_client.py`
2. Execute as migrações SQL na pasta raiz se necessário
3. Configure os usuários administradores

## 📊 Relatórios

O sistema gera relatórios completos incluindo:
- Status de projetos
- Progresso de tarefas
- Métricas de desempenho
- Análise de dependências

## 🔒 Segurança

- Controle de acesso baseado em funções (RLS)
- Validação de permissões
- Logs de auditoria

## 📝 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.

## 🆘 Suporte

Para suporte técnico, consulte a documentação em INSTALACAO.md