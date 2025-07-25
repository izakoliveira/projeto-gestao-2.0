# Projeto de Gestão de Projetos com Gantt

Sistema web para gestão de projetos com visualização de tarefas em gráfico de Gantt, desenvolvido em Flask e integrado ao Supabase.

## Funcionalidades
- Cadastro e login de usuários
- Criação, edição e exclusão de projetos
- Criação, edição e exclusão de tarefas
- Visualização de tarefas em gráfico de Gantt (Frappe Gantt customizado)
- Agrupamento de tarefas por projeto ou exibição geral
- Tooltip dinâmico e colorização por projeto
- Filtros por status, coleção e datas
- Integração com Supabase para persistência dos dados

## Estrutura de Pastas
```
projeto-gestao/
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
   git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   cd projeto-gestao
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
  git remote set-url origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
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
 