// ===== SISTEMA DE PREDECESSORAS - ARQUIVO SEPARADO =====
console.log('🚀 ARQUIVO DE PREDECESSORAS CARREGADO!');

// FUNÇÃO DEFINITIVA PARA RESTAURAR PREDECESSORAS
function restaurarPredecessorasDefinitivo() {
    console.log('🎨 RESTAURANDO PREDECESSORAS DEFINITIVAMENTE...');

    try {
        // Encontrar todos os campos de predecessoras
        const campos = document.querySelectorAll('input[name="predecessoras"]');
        console.log('📋 Campos encontrados: ' + campos.length);

        // Para cada campo com valor, executar a função principal
        campos.forEach((campo, index) => {
            if (campo.value && campo.value.trim()) {
                console.log(`🔄 Processando campo ${index + 1}: "${campo.value}"`);

                // Chamar função principal se existir
                if (typeof onPredecessorasEdit === 'function') {
                    onPredecessorasEdit(campo);
                    console.log(`✅ Campo ${index + 1} processado`);
                } else {
                    console.log(`❌ Função onPredecessorasEdit não encontrada`);
                }
            }
        });

        console.log('✅ RESTAURAÇÃO DEFINITIVA CONCLUÍDA!');
    } catch (error) {
        console.log('⚠️ Erro na restauração: ' + error);
    }
}

// EXECUTAR IMEDIATAMENTE
console.log('💥 EXECUTANDO IMEDIATAMENTE...');
setTimeout(restaurarPredecessorasDefinitivo, 100);

// EXECUTAR QUANDO DOM ESTIVER PRONTO
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
        console.log('📱 DOM carregado, executando...');
        setTimeout(restaurarPredecessorasDefinitivo, 100);
    });
} else {
    console.log('📱 DOM já carregado, executando...');
    setTimeout(restaurarPredecessorasDefinitivo, 100);
}

// EXECUTAR QUANDO PÁGINA CARREGAR
window.addEventListener('load', function () {
    console.log('🌐 Página carregada, executando...');
    setTimeout(restaurarPredecessorasDefinitivo, 200);
});

// EXECUTAR MÚLTIPLAS VEZES
setTimeout(restaurarPredecessorasDefinitivo, 1000);
setTimeout(restaurarPredecessorasDefinitivo, 3000);
setTimeout(restaurarPredecessorasDefinitivo, 5000);

// EXPOR FUNÇÃO GLOBALMENTE
window.restaurarPredecessoras = restaurarPredecessorasDefinitivo;
window.restaurarPredecessorasDefinitivo = restaurarPredecessorasDefinitivo;

console.log('💪 Função disponível: restaurarPredecessoras()');
console.log('🚀 ARQUIVO DE PREDECESSORAS ATIVO!');
