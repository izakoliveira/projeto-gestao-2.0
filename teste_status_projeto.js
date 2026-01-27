// Teste específico para limpeza do filtro de status do projeto
console.log('🧪 TESTANDO LIMPEZA DO STATUS DO PROJETO');

// Verificar se o wrapper existe
const wrapper = document.querySelector('.custom-select-wrapper[data-select-id="status-projeto"]');
console.log('Wrapper encontrado:', wrapper);

if (wrapper) {
    const instance = wrapper._customSelectInstance;
    console.log('Instância encontrada:', instance);

    if (instance) {
        console.log('🔄 Limpando status-projeto...');

        // Método 1: Reset do select nativo
        instance.nativeSelect.selectedIndex = -1;
        Array.from(instance.nativeSelect.options).forEach(opt => {
            opt.selected = false;
            console.log('Opção desmarcada:', opt.value);
        });

        // Método 2: Desmarcar checkboxes
        const checkboxes = wrapper.querySelectorAll('input[type="checkbox"]');
        console.log('Checkboxes encontrados:', checkboxes.length);
        checkboxes.forEach((checkbox, index) => {
            checkbox.checked = false;
            console.log(`Checkbox ${index} desmarcado`);
        });

        // Método 3: Limpar display
        const valueContainer = wrapper.querySelector('.custom-select-value');
        if (valueContainer) {
            valueContainer.querySelectorAll('.text').forEach(span => span.remove());
            const placeholder = valueContainer.querySelector('.placeholder');
            if (placeholder) {
                placeholder.style.display = 'inline';
                placeholder.textContent = 'Selecione o Status';
                console.log('Placeholder restaurado');
            }
        }

        // Método 4: Atualizar interface
        try {
            instance.updateDisplay();
            instance.syncCheckboxes();
            console.log('✅ updateDisplay e syncCheckboxes executados');
        } catch (e) {
            console.error('❌ Erro ao atualizar:', e);
        }

        console.log('✅ Limpeza concluída');
    } else {
        console.log('❌ Instância não encontrada');
    }
} else {
    console.log('❌ Wrapper não encontrado');
}