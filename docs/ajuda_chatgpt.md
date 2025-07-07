# Histórico de Ajuda e Dicas — ChatGPT

## Resumo das Soluções e Comandos

- **Problema:** Gantt não aparecia ou tooltip não funcionava
  - Solução: Debug passo a passo, criação de arquivos de teste, ajuste de CSS, ajuste de posicionamento do tooltip, centralização das barras, ajuste dinâmico de altura do container.

- **Tooltip customizado:**
  - Mostra nome, projeto, datas, dias corridos e úteis.
  - Acompanha o mouse em tempo real.
  - Nunca sai da tela, nunca salta para longe do cursor.

- **Comandos Git para conectar ao GitHub:**
  ```sh
  git init
  git add .
  git commit -m "Primeiro commit do projeto de gestão"
  git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
  git branch -M main
  git push -u origin main
  ```

- **Como salvar conversas/documentação:**
  - Crie um arquivo em `docs/ajuda_chatgpt.md` e cole o conteúdo relevante.
  - Faça commit e push normalmente.

- **Dicas de uso:**
  - Para rodar o projeto: `py app.py`
  - Para instalar dependências: `pip install -r requirements.txt`
  - Para acessar o Gantt: `/projetos` no navegador

- **Ajustes de UX:**
  - Tooltip sempre próximo do mouse, nunca fora da tela.
  - Barras do Gantt centralizadas e responsivas.

---

Se precisar de mais comandos, dicas ou quiser evoluir o projeto, basta abrir uma nova conversa! 