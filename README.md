# Sistema de Gestão de Projetos 2.0 🚀

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-orange.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-red.svg)](https://github.com/izakoliveira/sistema-gestao-projetos-2.0/releases)

Sistema web completo para gestão de projetos com visualização interativa em gráfico de Gantt, relatórios Excel/PDF e sistema de notificações por email.

## ✨ Funcionalidades Principais

### 👥 **Gestão de Usuários**
- Sistema completo de autenticação e cadastro
- Controle de acesso por níveis de usuário
- Perfis personalizáveis com notificações

### 📊 **Gestão de Projetos**
- Criação, edição e exclusão de projetos
- Organização em pastas e categorias
- Duplicação de projetos com templates
- Controle de status e progresso

### ✅ **Gestão de Tarefas**
- Criação e edição avançada de tarefas
- Sistema de dependências entre tarefas
- Controle de datas, durações e responsáveis
- Diferentes tipos de coleções e status

### 📈 **Visualização Gantt**
- Gráfico de Gantt interativo e responsivo
- Colorização automática por projeto
- Tooltip dinâmico com informações detalhadas
- Visualização desktop e mobile otimizada

### 📋 **Relatórios e Exportação**
- Exportação completa para Excel (múltiplas abas)
- Geração de relatórios em PDF
- Coluna de responsáveis nas planilhas
- Números centralizados em relatórios

### 🔔 **Sistema de Notificações**
- Notificações por email automáticas
- Alertas de prazos e atualizações
- Templates personalizáveis de email

### 🎯 **Filtros e Buscas**
- Filtros avançados por status, coleção e datas
- Sistema de busca inteligente
- Agrupamento flexível de dados

## Estrutura de Pastas
```
projeto-gestao-2.0/
├── app.py                  # Backend Flask principal
├── supabase_client.py      # Funções utilitárias para Supabase
├── detectar_ciclos.py      # Script para detectar ciclos em tarefas
├── requirements.txt        # Dependências do projeto
├── restricoes.json         # Restrições de funcionalidades
├── static/                 # Arquivos estáticos (CSS, JS, HTML de teste)
├── templates/              # Templates HTML (Jinja2)
├── docs/                   # Documentação adicional
├── .env                    # Variáveis de ambiente (não versionado)
└── README.md               # Este arquivo
```

## Como rodar o projeto

1. **Clone o repositório:**
   ```sh
   git clone https://github.com/SEU_USUARIO/projeto-gestao-2.0.git
   cd projeto-gestao-2.0
   ```
2. **Crie e ative o ambiente virtual:**
   ```sh
   python -m venv env
   ./env/Scripts/activate  # Windows
   source env/bin/activate  # Linux/Mac
   ```
3. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure as variáveis de ambiente:**
   - Copie `env_example.txt` para `.env` e preencha com suas chaves do Supabase e Flask.
5. **Rode o projeto:**
   ```sh
   python app.py
   ```
   Acesse [http://localhost:5000](http://localhost:5000)

## Expor o projeto na internet (Cloudflare Tunnel)

Para tornar seu projeto acessível de qualquer lugar através da internet:

### Configuração Inicial (uma vez só)
```bash
# Opção 1: Script Python interativo
python cloudflared_setup.py

# Opção 2: Script batch (Windows)
setup_cloudflared.bat
```

### Uso Diário
```bash
# 1. Inicie sua aplicação Flask
python app.py

# 2. Em outro terminal, inicie o túnel
python cloudflared_setup.py start projeto-gestao

# Ou use o script batch
start_cloudflared.bat
```

**📖 Guia completo:** Veja `docs/cloudflared_guide.md` para instruções detalhadas.

## Personalização do Gráfico de Gantt
- O template principal do Gantt está em `templates/projetos_gantt_basico.html`.
- Para customizar cores, estilos ou tooltips, edite esse arquivo e o CSS em `static/style.css`.
- Para testar agrupamentos, use o endpoint `/gantt-teste` ou edite `teste_agrupamento_gantt.html`.

## Comandos Git úteis
- Adicionar mudanças:
  ```sh
  git add .
  ```
- Commitar:
  ```sh
  git commit -m "Descreva sua alteração aqui"
  ```
- Enviar para o GitHub:
  ```sh
  git push origin main
  ```
- Trocar o remoto:
  ```sh
  git remote set-url origin https://github.com/SEU_USUARIO/projeto-gestao-2.0.git
  ```
- Ver endereço remoto:
  ```sh
  git remote -v
  ```

## Créditos e Contato
- Desenvolvido por [Seu Nome] (<seu@email.com>)
- Integração com [Supabase](https://supabase.com/) e [Frappe Gantt](https://frappe.io/gantt)

---
Se tiver dúvidas, consulte este README ou abra uma issue no repositório!
 