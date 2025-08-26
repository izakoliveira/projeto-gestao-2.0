/**
 * Sistema de Drag & Drop para Tarefas
 * Sistema de Gestão de Projetos v2.0.0
 */

class SortableTarefas {
    constructor() {
        this.instance = null;
        this.tbody = null;
        this.isInitialized = false;
        this.init();
    }

    init() {
        // Aguardar o DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Aguardar um pouco para garantir que tudo carregou
        setTimeout(() => {
            this.findElements();
            this.loadSortable();
        }, 500);
    }

    findElements() {
        this.tbody = document.querySelector('#tabela-tarefas-inline tbody');
        if (!this.tbody) {
            console.log('❌ Tbody não encontrado para Sortable');
            return false;
        }
        console.log('✅ Tbody encontrado para Sortable');
        return true;
    }

    loadSortable() {
        if (typeof Sortable !== 'undefined') {
            this.initializeSortable();
        } else {
            this.loadSortableFromCDN();
        }
    }

    loadSortableFromCDN() {
        console.log('📥 Carregando SortableJS da CDN...');
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js';
        script.async = true;
        script.onload = () => {
            console.log('✅ SortableJS carregado com sucesso');
            this.initializeSortable();
        };
        script.onerror = () => {
            console.log('❌ Falha ao carregar SortableJS da CDN principal');
            this.loadSortableFallback();
        };
        document.head.appendChild(script);
    }

    loadSortableFallback() {
        console.log('🔄 Tentando fallback do SortableJS...');
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/sortablejs@1.15.0/Sortable.min.js';
        script.async = true;
        script.onload = () => {
            console.log('✅ SortableJS carregado via fallback');
            this.initializeSortable();
        };
        script.onerror = () => {
            console.log('❌ Falha ao carregar SortableJS de todas as fontes');
        };
        document.head.appendChild(script);
    }

    initializeSortable() {
        if (!this.tbody || this.isInitialized) return;

        try {
            // Destruir instância anterior se existir
            if (this.instance) {
                this.instance.destroy();
            }

            // Verificar se há linhas para arrastar
            const linhas = this.tbody.querySelectorAll('tr:not(#linha-nova-tarefa)');
            if (linhas.length === 0) {
                console.log('⚠️ Nenhuma linha encontrada para arrastar');
                return;
            }

            console.log('🔧 Inicializando SortableJS...');

            const options = {
                handle: '.drag-handle',
                animation: 150,
                forceFallback: false,
                fallbackOnBody: true,
                fallbackTolerance: 3,
                draggable: 'tr:not(#linha-nova-tarefa)',
                filter: '#linha-nova-tarefa, input, select, textarea, button, a, .btn, .form-control, .form-select, .numero-tarefa',
                preventOnFilter: false,
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                dragClass: 'sortable-drag',
                onStart: (evt) => {
                    console.log('🚀 Drag iniciado');
                    evt.item.classList.add('dragging');
                },
                onEnd: (evt) => {
                    console.log('🏁 Drag finalizado');
                    evt.item.classList.remove('dragging');
                    this.handleReorder();
                },
                onMove: (evt) => {
                    // Permitir mover apenas se não for linha de nova tarefa
                    if (evt.related.id === 'linha-nova-tarefa') {
                        return false;
                    }
                    return true;
                },
                // Configurações para não interferir com inputs
                delay: 150,
                delayOnTouchOnly: true,
                touchStartThreshold: 3
            };

            this.instance = new Sortable(this.tbody, options);
            this.isInitialized = true;
            console.log('✅ SortableJS inicializado com sucesso');

            // Adicionar estilos visuais
            this.addVisualFeedback();

            // Garantir que campos sejam editáveis
            this.ensureEditableFields();

        } catch (error) {
            console.error('❌ Erro ao inicializar SortableJS:', error);
        }
    }

    addVisualFeedback() {
        // Adicionar estilos CSS para feedback visual
        const style = document.createElement('style');
        style.textContent = `
            .sortable-ghost {
                opacity: 0.5;
                background: #f8f9fa !important;
            }
            .sortable-chosen {
                background: #e3f2fd !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .sortable-drag {
                background: #fff !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: rotate(5deg);
            }
            .dragging {
                cursor: grabbing !important;
            }
            .drag-handle {
                cursor: grab;
                color: #6c757d;
                transition: color 0.2s;
            }
            .drag-handle:hover {
                color: #007bff;
                cursor: grab;
            }
            .drag-handle:active {
                cursor: grabbing;
            }
            
            /* Garantir que campos editáveis funcionem */
            .form-control, .form-select {
                pointer-events: auto !important;
                cursor: text !important;
            }
            
            .form-control:focus, .form-select:focus {
                border-color: #007bff !important;
                box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25) !important;
            }
            
            /* Botões sempre clicáveis */
            .btn, button {
                pointer-events: auto !important;
                cursor: pointer !important;
            }
        `;
        document.head.appendChild(style);
    }

    ensureEditableFields() {
        // Garantir que todos os campos editáveis funcionem
        const editableFields = this.tbody.querySelectorAll('input, select, textarea, button, .btn');

        editableFields.forEach(field => {
            // Remover qualquer evento que possa interferir
            field.style.pointerEvents = 'auto';
            field.style.cursor = field.tagName === 'INPUT' || field.tagName === 'TEXTAREA' ? 'text' : 'pointer';

            // Garantir que cliques nos campos não iniciem drag
            field.addEventListener('mousedown', (e) => {
                e.stopPropagation();
            }, { passive: true });

            field.addEventListener('click', (e) => {
                e.stopPropagation();
            }, { passive: true });

            // Para campos de input, garantir foco
            if (field.tagName === 'INPUT' || field.tagName === 'TEXTAREA') {
                field.addEventListener('focus', (e) => {
                    e.target.style.borderColor = '#007bff';
                    e.target.style.boxShadow = '0 0 0 0.2rem rgba(0,123,255,.25)';
                });

                field.addEventListener('blur', (e) => {
                    e.target.style.borderColor = '';
                    e.target.style.boxShadow = '';
                });
            }
        });

        // Preservar sistema de cálculo original da aplicação
        this.preserveOriginalCalculation();

        console.log('✅ Campos editáveis configurados:', editableFields.length);
    }

    preserveOriginalCalculation() {
        // Garantir que as funções originais de cálculo funcionem
        const dataInicioFields = this.tbody.querySelectorAll('input[name="data_inicio"]');
        const dataFimFields = this.tbody.querySelectorAll('input[name="data_fim"]');
        const duracaoFields = this.tbody.querySelectorAll('input[name="duracao"]');

        // Restaurar eventos originais se existirem

        // Configurar eventos para data início
        dataInicioFields.forEach(field => {
            // Garantir que o evento original funcione
            if (typeof window.onInicioOuFimEdit === 'function') {
                field.addEventListener('input', () => {
                    window.onInicioOuFimEdit(field);
                });
            }
        });

        // Configurar eventos para data fim
        dataFimFields.forEach(field => {
            // Garantir que o evento original funcione
            if (typeof window.onInicioOuFimEdit === 'function') {
                field.addEventListener('input', () => {
                    window.onInicioOuFimEdit(field);
                });
            }
        });

        // Configurar eventos para duração
        duracaoFields.forEach(field => {
            // Garantir que o evento original funcione
            if (typeof window.onDuracaoOuFimEdit === 'function') {
                field.addEventListener('input', () => {
                    window.onDuracaoOuFimEdit(field);
                });
                field.addEventListener('blur', () => {
                    window.onDuracaoOuFimEdit(field, true);
                });
            }
        });

        console.log('✅ Sistema de cálculo original preservado para', dataInicioFields.length, 'linhas');
    }

    handleReorder() {
        if (!this.tbody) return;

        try {
            // Atualizar números das tarefas
            const linhas = Array.from(this.tbody.querySelectorAll('tr:not(#linha-nova-tarefa)'));
            linhas.forEach((tr, idx) => {
                const tdNumero = tr.querySelector('.numero-tarefa');
                if (tdNumero) {
                    tdNumero.textContent = idx + 1;
                }
            });

            // Coletar IDs das tarefas na nova ordem
            const ids = linhas.map(tr => {
                const input = tr.querySelector('input[name="nome"]');
                return input ? input.dataset.id : null;
            }).filter(Boolean);

            console.log('🔄 Nova ordem das tarefas:', ids);

            if (ids.length > 0) {
                // Enviar para o backend
                this.updateOrderOnServer(ids);
            }

        } catch (error) {
            console.error('❌ Erro ao processar reordenação:', error);
        }
    }

    updateOrderOnServer(ids) {
        fetch('/tarefas/atualizar_ordem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ ids })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('✅ Ordem das tarefas atualizada no servidor');
                    this.showSuccessMessage('Ordem das tarefas atualizada com sucesso!');
                } else {
                    console.error('❌ Erro ao atualizar ordem:', data.error);
                    this.showErrorMessage('Erro ao atualizar ordem das tarefas');
                }
            })
            .catch(error => {
                console.error('❌ Erro na requisição:', error);
                this.showErrorMessage('Erro de conexão ao atualizar ordem');
            });
    }

    showSuccessMessage(message) {
        // Mostrar mensagem de sucesso
        if (window.mostrarNotificacaoToast) {
            window.mostrarNotificacaoToast(message, 'success', 3000);
        } else {
            alert(message);
        }
    }

    showErrorMessage(message) {
        // Mostrar mensagem de erro
        if (window.mostrarNotificacaoToast) {
            window.mostrarNotificacaoToast(message, 'error', 5000);
        } else {
            alert(message);
        }
    }

    destroy() {
        if (this.instance) {
            this.instance.destroy();
            this.instance = null;
        }
        this.isInitialized = false;
    }

    refresh() {
        this.destroy();
        setTimeout(() => {
            this.setup();
        }, 100);
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    // Aguardar um pouco para garantir que tudo carregou
    setTimeout(() => {
        window.sortableTarefas = new SortableTarefas();
    }, 1000);
});

// Função global para recarregar o Sortable
window.refreshSortableTarefas = () => {
    if (window.sortableTarefas) {
        window.sortableTarefas.refresh();
    }
};

// Função global para verificar status
window.checkSortableStatus = () => {
    if (window.sortableTarefas) {
        console.log('Status do Sortable:', {
            initialized: window.sortableTarefas.isInitialized,
            instance: !!window.sortableTarefas.instance,
            tbody: !!window.sortableTarefas.tbody
        });
    } else {
        console.log('SortableTarefas não foi inicializado');
    }
};
