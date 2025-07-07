# Migração para Frappe Gantt - Visual Similar ao Power BI

## Por que migrar para Frappe Gantt?

O **Frappe Gantt** oferece um visual muito mais moderno e similar ao Power BI, com:
- ✅ Design limpo e profissional
- ✅ Cores suaves e paleta visual agradável
- ✅ Interface intuitiva e responsiva
- ✅ Gratuito e open-source
- ✅ Fácil customização
- ✅ Melhor experiência do usuário

## Comparação Visual

| Aspecto | dhtmlxGantt (atual) | Frappe Gantt (recomendado) |
|---------|---------------------|----------------------------|
| **Visual** | Técnico/robusto | Moderno/elegante |
| **Cores** | Padrão azul | Paleta suave similar ao Power BI |
| **Interface** | Funcional | Intuitiva e responsiva |
| **Customização** | Complexa | Simples e flexível |
| **Performance** | Boa | Excelente |
| **Licença** | Gratuita | Gratuita |

## Passos para Migração

### 1. Atualizar Dependências

Substitua no template `projetos.html`:

```html
<!-- REMOVER -->
<link rel="stylesheet" href="https://cdn.dhtmlx.com/gantt/edge/dhtmlxgantt.css">
<script src="https://cdn.dhtmlx.com/gantt/edge/dhtmlxgantt.js"></script>

<!-- ADICIONAR -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.css">
<script src="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.min.js"></script>
```

### 2. Adaptar Estrutura de Dados

No `app.py`, modificar a função que prepara os dados:

```python
# ANTES (dhtmlxGantt)
def preparar_dados_gantt(tarefas):
    gantt_data = []
    for t in tarefas:
        gantt_data.append({
            'id': t['id'],
            'text': t.get('nome', ''),
            'start_date': t.get('data_inicio_iso', ''),
            'duration': t.get('duration', 1),
            'progress': 0
        })
    return gantt_data

# DEPOIS (Frappe Gantt)
def preparar_dados_gantt(tarefas):
    gantt_data = []
    for t in tarefas:
        # Calcular data de fim
        data_inicio = t.get('data_inicio_iso', '')
        duracao = t.get('duration', 1)
        if data_inicio and duracao:
            data_fim = (datetime.strptime(data_inicio, '%Y-%m-%d') + 
                       timedelta(days=duracao-1)).strftime('%Y-%m-%d')
        else:
            data_fim = data_inicio
            
        gantt_data.append({
            'id': str(t['id']),
            'name': t.get('nome', ''),
            'start': data_inicio,
            'end': data_fim,
            'progress': 0,
            'dependencies': t.get('predecessoras', '').replace(';', ','),
            'custom_class': f"status-{t.get('status', 'pendente').replace(' ', '-')}"
        })
    return gantt_data
```

### 3. Atualizar JavaScript

Substituir o código JavaScript do Gantt:

```javascript
// ANTES (dhtmlxGantt)
gantt.init("gantt_geral");
gantt.parse({
    data: {{ gantt_geral_data | tojson | safe }},
    links: {{ gantt_geral_links | tojson | safe }}
});

// DEPOIS (Frappe Gantt)
const gantt = new Gantt("#gantt_geral", {{ gantt_geral_data | tojson | safe }}, {
    view_mode: 'Month',
    date_format: 'YYYY-MM-DD',
    show_progress: true,
    show_arrows: true,
    show_today: true,
    show_weekends: true,
    language: 'pt',
    on_click: function (task) {
        console.log('Tarefa clicada:', task);
    },
    on_date_change: function (task, start, end) {
        console.log('Data alterada:', task, start, end);
    },
    on_progress_change: function (task, progress) {
        console.log('Progresso alterado:', task, progress);
    }
});
```

### 4. Adicionar CSS Personalizado

```css
/* Estilo similar ao Power BI */
.gantt .bar {
    fill: #667eea;
    stroke: #5a6fd8;
    stroke-width: 1;
    rx: 4;
    ry: 4;
}

.gantt .bar-progress {
    fill: #764ba2;
}

.gantt .grid-header {
    fill: #667eea;
    stroke: #5a6fd8;
}

.gantt .grid-row {
    fill: white;
    stroke: #e9ecef;
}

.gantt .grid-row:nth-child(even) {
    fill: #f8f9fa;
}

/* Cores por status */
.status-pendente { fill: #ffc107; }
.status-em-progresso { fill: #17a2b8; }
.status-concluida { fill: #28a745; }
```

### 5. Implementar Controles de Zoom

```javascript
function changeView(mode) {
    gantt.change_view_mode(mode);
}

function today() {
    gantt.today();
}

function prev() {
    gantt.prev();
}

function next() {
    gantt.next();
}
```

## Vantagens da Migração

### Visual
- **Design moderno** similar ao Power BI
- **Cores suaves** e profissionais
- **Interface limpa** e intuitiva
- **Responsividade** melhorada

### Funcionalidade
- **Performance superior** com grandes datasets
- **Customização mais simples**
- **Melhor suporte** a dependências
- **Tooltips informativos** nativos

### Desenvolvimento
- **Código mais limpo** e organizado
- **Menos configurações** complexas
- **Documentação melhor**
- **Comunidade ativa**

## Exemplo de Implementação Completa

Veja o arquivo `static/frappe_gantt_exemplo.html` para um exemplo completo de implementação com:
- Controles de visualização (Dia/Semana/Mês/Ano)
- Navegação (Anterior/Próximo/Hoje)
- Cores por status
- Legendas informativas
- Design responsivo

## Próximos Passos

1. **Teste o exemplo** em `static/frappe_gantt_exemplo.html`
2. **Adapte os dados** do seu projeto
3. **Implemente gradualmente** em uma página de teste
4. **Migre todas as páginas** que usam Gantt
5. **Remova dependências** do dhtmlxGantt

## Suporte

Se precisar de ajuda na migração:
- Documentação oficial: https://frappe.io/gantt
- Exemplos: https://github.com/frappe/gantt
- Comunidade: GitHub Issues do projeto 