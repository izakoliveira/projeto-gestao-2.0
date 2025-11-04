# Funcionalidade: Datas Conflitantes

## Descrição
Esta funcionalidade identifica e exibe diferentes tipos de conflitos de datas no sistema de gestão de projetos.

## Acesso
- **Rota**: `/relatorio/datas-conflitantes`  
- **Menu**: Relatórios > Datas Conflitantes
- **Permissões**: Usuários logados

## Tipos de Conflitos Detectados

### 1. Projetos Inconsistentes
- **Problema**: Projetos onde a data de término é anterior à data de início
- **Impacto**: Cronograma impossível de executar
- **Ação**: Corrigir as datas do projeto

### 2. Tarefas Fora do Projeto  
- **Problema**: Tarefas com datas que ultrapassam o período definido para o projeto
- **Impacto**: Desalinhamento entre projeto e tarefas
- **Ação**: Ajustar datas das tarefas ou do projeto

### 3. Tarefas Sobrepostas
- **Problema**: Múltiplas tarefas do mesmo projeto executando simultaneamente
- **Impacto**: Possível conflito de recursos
- **Ação**: Revisar sequenciamento das tarefas

### 4. Datas Inválidas
- **Problema**: Tarefas onde a data de término é anterior à data de início
- **Impacto**: Cronograma impossível de executar
- **Ação**: Corrigir as datas da tarefa

### 5. Problemas com Predecessoras
- **Problema**: Tarefas com predecessoras inexistentes ou com ordem inválida
- **Impacto**: Dependências quebradas no cronograma
- **Ação**: Corrigir as referências de predecessoras

## Interface

### Resumo Visual
- 6 cards coloridos mostrando o total de cada tipo de conflito
- Card adicional com total geral de conflitos
- Cores diferentes para cada categoria de problema
- Layout responsivo para diferentes tamanhos de tela

### Filtros
- Checkboxes para mostrar/ocultar tipos específicos de conflitos
- Botão "Todos/Nenhum" para alternar todos os filtros rapidamente
- Aplicação em tempo real

### Tabelas Detalhadas
- Informações completas sobre cada conflito encontrado
- Links diretos para edição dos itens problemáticos
- Ordenação e formatação clara

## Funcionalidades Técnicas

### Backend (`routes/relatorio.py`)
- **Rota**: `@relatorio_bp.route('/datas-conflitantes')`
- **Função principal**: `detectar_conflitos_datas(projetos, tarefas)`
- **Função auxiliar**: `verificar_sobreposicao_tarefas(tarefa1, tarefa2)`

### Frontend (`templates/datas_conflitantes.html`)
- Interface responsiva com Bootstrap
- Filtros dinâmicos com JavaScript
- Animações e estados visuais
- Links de ação para resolução

## Integração com o Sistema

### Menu de Navegação
- Adicionado dropdown "Relatórios" na navbar
- Links para "Exportação" e "Datas Conflitantes"

### Autorização  
- Utiliza decorator `@login_required`
- Acessível para todos os usuários logados

## Benefícios

1. **Prevenção de Problemas**: Identifica conflitos antes que afetem o projeto
2. **Qualidade de Dados**: Melhora a consistência das informações
3. **Gestão Proativa**: Permite correções preventivas
4. **Visibilidade**: Interface clara para identificação rápida
5. **Ação Direta**: Links para correção imediata dos problemas

## Melhorias Futuras

- Notificações automáticas quando conflitos são detectados
- Exportação dos conflitos para Excel/PDF
- Sugestões automáticas de correção
- Filtros por projeto específico
- Histórico de conflitos resolvidos
- Alertas em tempo real durante criação/edição
- Detecção de ciclos em predecessoras
- Análise de caminho crítico com conflitos
- Alertas por email para gestores
- Correção automática de conflitos simples

## Casos de Uso

1. **Auditoria de Qualidade**: Verificação periódica da consistência dos dados
2. **Preparação de Projetos**: Validação antes do início da execução  
3. **Resolução de Problemas**: Identificação rápida de inconsistências reportadas
4. **Manutenção Preventiva**: Limpeza regular da base de dados

## Teste

Para testar a funcionalidade:

1. Execute: `python teste_datas_conflitantes.py`
2. Acesse: `http://localhost:5000/relatorio/datas-conflitantes`
3. Verifique se todos os tipos de conflitos são detectados corretamente
4. Teste os filtros e links de ação

---

**Data de implementação**: 29/10/2025  
**Versão**: 1.0  
**Desenvolvedor**: Sistema de Gestão de Projetos