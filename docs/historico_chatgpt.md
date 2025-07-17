# Histórico de Interações com o ChatGPT

## Resumo da Conversa (última atualização)

1. **Notificações por E-mail ao Responsável:**
   - Implementação do envio automático de e-mail ao responsável ao criar ou editar uma tarefa.
   - Personalização do conteúdo do e-mail (nome da tarefa, projeto, datas, status).
   - Orientações sobre configuração do `.env` para SMTP (Gmail, senha de app, etc).
   - Correção de bugs e melhorias no tratamento de erros e feedback ao usuário.
   - Envio de e-mail também ao remover responsável de uma tarefa.

2. **Personalização e Expansão das Notificações:**
   - Modelos de e-mail para designação, remoção e conclusão de tarefa.
   - Ajustes para evitar uso de variáveis não inicializadas e tratamento de possíveis erros de SMTP.

3. **Notificações Internas (Painel/Sininho):**
   - Planejamento e início da implementação de notificações internas (painel/sininho).
   - Definição da estrutura da tabela no Supabase: `id`, `usuario_id`, `mensagem`, `lida`, `tipo`, `data_criacao`.
   - Criação de tarefas para backend Flask (registro e busca), frontend (ícone de sininho, badge, modal/listagem) e integração com eventos do sistema.

4. **Git e Organização:**
   - Commit das alterações no GitHub com mensagem descritiva.
   - Documentação do processo e dificuldades encontradas (ex: comandos no PowerShell).

5. **Próximos Passos:**
   - Criar tabela de notificações no Supabase.
   - Implementar backend Flask para notificações.
   - Adicionar ícone de sininho e painel de notificações na interface.
   - Integrar notificações internas aos eventos do sistema (designação, remoção, conclusão de tarefas).

---

*Este histórico é atualizado periodicamente para registrar as principais decisões, implementações e próximos passos do projeto.* 