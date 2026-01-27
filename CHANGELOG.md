# Sistema de Gestão de Projetos - Changelog

## v2.0 - Melhorias e Correções

### ✅ Funcionalidades Implementadas

#### Atualização Automática de Coleção (19/01/2026)
- **Funcionalidade**: Quando o nome de um projeto é alterado na tela de detalhes do projeto, a coleção de todas as tarefas do projeto é automaticamente atualizada para o novo nome do projeto.
- **Motivo**: Permite que o usuário altere a coleção de algumas tarefas específicas sem afetar todas as tarefas do projeto.
- **Implementação**: Modificada a função `editar_projeto()` em `routes/main.py` para detectar mudanças no nome e atualizar a coleção das tarefas via query SQL.
- **Benefício**: Melhor organização e flexibilidade no gerenciamento de coleções de tarefas.

#### Exibição de Feriados da API na Tela de Feriados (19/01/2026)
- **Funcionalidade**: A tela de Feriados agora exibe tanto os feriados manuais quanto todos os feriados nacionais da API BrasilAPI.
- **Implementação**: 
  - Criada nova função `obter_feriados_ano_completos()` em `utils/dias_uteis.py` para buscar feriados completos da API
  - Modificada a rota `producao_feriados()` para passar feriados manuais e da API para o template
  - Atualizado template `feriados.html` com duas colunas: "Feriados Manuais" e "Feriados Nacionais [ano]"
  - Implementadas rotas AJAX para CRUD de feriados manuais
- **Benefício**: Visualização completa de todos os feriados, facilitando o planejamento e gestão de datas especiais.

### 🔧 Correções Técnicas

#### Remoção de Funcionalidade "Feriados Manuais (Admin)"
- Removida a interface de feriados manuais da tela admin/Restrições
- Eliminadas todas as funções JavaScript relacionadas
- Limpeza completa do código não utilizado

### 📚 Melhorias na Documentação
- Atualizado README.md com informações sobre organização por coleções
- Adicionada seção sobre agrupamento automático de tarefas por coleção

---

*Para mais detalhes sobre instalação e uso, consulte o arquivo README.md*</content>
<parameter name="filePath">c:\Users\izak.oliveira\Desktop\projeto-gestao-2.0-main\CHANGELOG.md