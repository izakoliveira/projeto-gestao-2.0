# Projeto de Gestão com Gantt

Este é um sistema de gestão de projetos e tarefas com visualização em Gantt, desenvolvido em Flask e integrado ao Supabase.

## Funcionalidades
- Cadastro e login de usuários
- Cadastro de projetos e tarefas
- Visualização de tarefas em gráfico de Gantt customizado
- Tooltip detalhado ao passar o mouse sobre as tarefas
- Integração com Supabase para persistência dos dados

## Como rodar localmente

1. **Clone o repositório:**
   ```sh
   git clone <URL_DO_SEU_REPOSITORIO>
   cd projeto-gestao
   ```
2. **Crie e configure o arquivo `.env`** com as variáveis do Supabase e Flask.
3. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Rode o servidor Flask:**
   ```sh
   py app.py
   ```
5. **Acesse em:**
   - [http://localhost:5000](http://localhost:5000)

## Estrutura de Pastas
- `app.py` — Backend Flask
- `templates/` — Templates HTML (inclui o Gantt)
- `static/` — Arquivos estáticos (CSS, JS, testes)
- `docs/` — Documentação e histórico de ajuda

## Créditos
- Desenvolvido com auxílio do ChatGPT para automação, debug e UX. 