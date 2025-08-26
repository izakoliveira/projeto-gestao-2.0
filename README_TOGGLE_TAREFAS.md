# Funcionalidade de Expandir/Colapsar Lista de Tarefas

## Descrição

Esta funcionalidade permite aos usuários expandir ou colapsar a lista de tarefas na tela de detalhes do projeto, melhorando a experiência do usuário ao visualizar projetos com muitas tarefas.

## Funcionalidades Implementadas

### 1. Botão de Toggle
- **Localização**: Posicionado ao lado do título "Tarefas do Projeto"
- **Estilo**: Botão outline com ícone e texto descritivo
- **Comportamento**: Alterna entre os estados "Expandir" e "Colapsar"

### 2. Estados da Lista
- **Estado Colapsado (Padrão)**:
  - Altura máxima: 350px
  - Scroll vertical ativado
  - Botão mostra "Expandir" com ícone de expansão
  
- **Estado Expandido**:
  - Altura máxima: removida (sem limite)
  - Scroll vertical desativado
  - Botão mostra "Colapsar" com ícone de compressão

### 3. Feedback Visual
- **Ícone**: Muda entre `fa-expand-alt` e `fa-compress-alt`
- **Texto**: Alterna entre "Expandir" e "Colapsar"
- **Cor do Botão**: Muda de outline para preenchido quando expandido

## Arquivos Modificados

### 1. `templates/detalhes_projeto.html`
- Adicionado botão de toggle no cabeçalho das tarefas
- Implementada função JavaScript `toggleTarefas()`
- Botão posicionado entre o título e os botões de ação

### 2. `templates/detalhes_projeto_mobile.html`
- Adicionado botão de toggle adaptado para mobile
- Implementada função JavaScript `toggleTarefasMobile()`
- Layout responsivo mantido

## Implementação Técnica

### Função JavaScript Principal
```javascript
function toggleTarefas() {
    const tabelaWrap = document.querySelector('.tabela-tarefas-wrap');
    const btnToggle = document.getElementById('btn-toggle-tarefas');
    const iconToggle = document.getElementById('icon-toggle-tarefas');
    const textToggle = document.getElementById('text-toggle-tarefas');
    
    if (tabelaWrap.style.maxHeight === '350px' || !tabelaWrap.style.maxHeight) {
        // Expandir
        tabelaWrap.style.maxHeight = 'none';
        tabelaWrap.style.overflowY = 'visible';
        iconToggle.className = 'fas fa-compress-alt';
        textToggle.textContent = 'Colapsar';
        btnToggle.classList.remove('btn-outline-secondary');
        btnToggle.classList.add('btn-secondary');
    } else {
        // Colapsar
        tabelaWrap.style.maxHeight = '350px';
        tabelaWrap.style.overflowY = 'auto';
        iconToggle.className = 'fas fa-expand-alt';
        textToggle.textContent = 'Expandir';
        btnToggle.classList.remove('btn-secondary');
        btnToggle.classList.add('btn-outline-secondary');
    }
}
```

### Estrutura HTML
```html
<button type="button" class="btn btn-outline-secondary btn-sm" id="btn-toggle-tarefas" 
        onclick="toggleTarefas()" title="Expandir/Colapsar lista de tarefas">
    <i class="fas fa-expand-alt" id="icon-toggle-tarefas"></i>
    <span id="text-toggle-tarefas">Expandir</span>
</button>
```

## Arquivos de Teste

### 1. `teste_toggle_tarefas.html`
- Demonstração da funcionalidade para desktop
- Inclui tabela de exemplo com 8 tarefas
- Funcionalidade completa implementada

### 2. `teste_toggle_tarefas_mobile.html`
- Demonstração da funcionalidade para mobile
- Layout responsivo com cards mobile
- Funcionalidade adaptada para telas pequenas

## Como Usar

1. **Acesse a tela de detalhes do projeto**
2. **Localize o botão "Expandir"** ao lado do título "Tarefas do Projeto"
3. **Clique no botão** para expandir a lista de tarefas
4. **Clique novamente** para colapsar e voltar ao tamanho original

## Benefícios

- **Melhor Usabilidade**: Usuários podem ver todas as tarefas sem scroll
- **Flexibilidade**: Alternância rápida entre visualizações
- **Responsividade**: Funciona tanto em desktop quanto em mobile
- **Feedback Visual**: Estados claros e intuitivos
- **Performance**: Não afeta a funcionalidade existente

## Compatibilidade

- ✅ **Desktop**: Funciona em todas as resoluções
- ✅ **Mobile**: Adaptado para telas pequenas
- ✅ **Navegadores**: Compatível com navegadores modernos
- ✅ **Bootstrap**: Integrado com o framework existente
- ✅ **Font Awesome**: Utiliza ícones da biblioteca existente

## Personalização

A funcionalidade pode ser facilmente personalizada:

- **Altura padrão**: Alterar o valor `350px` na função JavaScript
- **Estilos**: Modificar classes CSS do botão
- **Ícones**: Trocar ícones Font Awesome
- **Posicionamento**: Ajustar layout do cabeçalho

## Manutenção

- **Função isolada**: Fácil de manter e debugar
- **IDs únicos**: Evita conflitos com outras funcionalidades
- **Código limpo**: Estrutura clara e bem documentada
- **Reutilizável**: Pode ser adaptada para outras listas do sistema
