// 🔧 CORREÇÃO PARA EXCLUSÃO DE TAREFAS
// Este arquivo corrige problemas na funcionalidade de exclusão

console.log('🔧 Carregando correção para exclusão de tarefas...');

// Função principal de correção
function corrigirExclusaoTarefas() {
    console.log('🔧 Aplicando correção para exclusão de tarefas...');

    // 1. Verificar se já existe configuração
    if (window.exclusaoTarefasConfigurada) {
        console.log('⚠️ Exclusão de tarefas já configurada, reconfigurando...');
    }

    // 2. Limpar event listeners existentes
    try {
        // Remover com mesmas opções usadas na adição (capture=true)
        document.removeEventListener('click', window.handleExclusaoClickGlobal, true);
        console.log('✅ Event listeners anteriores removidos');
    } catch (error) {
        console.log('⚠️ Erro ao remover event listeners:', error);
    }

    // 3. Definir handler global
    window.handleExclusaoClickGlobal = function (e) {
        // Verificar se clicou no botão de exclusão
        if (e.target.closest('.btn-excluir-tarefa')) {
            e.preventDefault();
            e.stopPropagation();

            console.log('🗑️ Botão de exclusão clicado!');

            const btn = e.target.closest('.btn-excluir-tarefa');
            const tarefaId = btn.getAttribute('data-tarefa-id');

            if (!tarefaId) {
                console.error('❌ ID da tarefa não encontrado');
                alert('Erro: ID da tarefa não encontrado');
                return;
            }

            console.log(`🗑️ Excluindo tarefa: ${tarefaId}`);

            // Confirmar exclusão
            if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
                // Executar exclusão
                executarExclusaoCorrigida(tarefaId, btn);
            }
        }
    };

    // 4. Adicionar event listener (fase de captura para resistir a stopPropagation em bubbling)
    document.addEventListener('click', window.handleExclusaoClickGlobal, true);
    console.log('✅ Event listener de exclusão configurado (capture=true)');

    // 5. Marcar como configurado
    window.exclusaoTarefasConfigurada = true;

    console.log('✅ Correção aplicada com sucesso!');

    // 6. Watchdog/heartbeat: reanexar periodicamente para evitar sobrescritas
    try {
        if (window._exclusaoHeartbeat) {
            clearInterval(window._exclusaoHeartbeat);
        }
        window._exclusaoHeartbeat = setInterval(() => {
            try {
                document.removeEventListener('click', window.handleExclusaoClickGlobal, true);
                document.addEventListener('click', window.handleExclusaoClickGlobal, true);
                // console.debug('🔁 Heartbeat: listener de exclusão reanexado');
            } catch (hbErr) {
                console.warn('⚠️ Heartbeat erro:', hbErr);
            }
        }, 3000);
        console.log('🫀 Heartbeat de reconfiguração ativado');
    } catch (errHb) {
        console.warn('⚠️ Não foi possível ativar heartbeat:', errHb);
    }

    // 7. Reconfigurar em eventos de visibilidade/foco
    try {
        const rebind = () => {
            try {
                document.removeEventListener('click', window.handleExclusaoClickGlobal, true);
                document.addEventListener('click', window.handleExclusaoClickGlobal, true);
                // console.debug('🔄 Rebind em visibilidade/foco');
            } catch (_) { }
        };
        window.addEventListener('visibilitychange', rebind);
        window.addEventListener('focus', rebind);
    } catch (errVis) {
        console.warn('⚠️ Erro ao registrar rebind de visibilidade/foco:', errVis);
    }
}

// Função para executar exclusão
function executarExclusaoCorrigida(tarefaId, btnExcluir) {
    console.log(`🗑️ Executando exclusão da tarefa: ${tarefaId}`);

    // Desabilitar botão e mostrar spinner
    const originalContent = btnExcluir.innerHTML;
    btnExcluir.disabled = true;
    btnExcluir.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

    // Fazer requisição para excluir
    fetch(`/tarefas/excluir/${tarefaId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            console.log(`📡 Resposta do servidor: ${response.status}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Dados da resposta:', data);

            if (data.sucesso) {
                console.log('✅ Tarefa excluída com sucesso');

                // Remover linha da tabela com animação
                const tr = btnExcluir.closest('tr');
                if (tr) {
                    tr.style.transition = 'opacity 0.3s ease';
                    tr.style.opacity = '0';
                    setTimeout(() => {
                        tr.remove();
                        console.log('✅ Linha removida da tabela');
                    }, 300);
                }

                // Mostrar mensagem de sucesso
                alert('Tarefa excluída com sucesso!');

            } else {
                throw new Error(data.erro || 'Erro desconhecido do servidor');
            }
        })
        .catch(error => {
            console.error('❌ Erro na exclusão:', error);
            alert('Erro ao excluir tarefa: ' + error.message);

            // Restaurar botão
            btnExcluir.disabled = false;
            btnExcluir.innerHTML = originalContent;
        });
}

// Função para verificar status
function verificarStatusExclusao() {
    console.log('🔍 Verificando status da exclusão de tarefas...');

    const botoes = document.querySelectorAll('.btn-excluir-tarefa');
    const configurado = window.exclusaoTarefasConfigurada;

    console.log(`🔍 Botões de exclusão encontrados: ${botoes.length}`);
    console.log(`🔍 Sistema configurado: ${configurado}`);

    if (botoes.length === 0) {
        console.log('⚠️ Nenhum botão de exclusão encontrado');
        return false;
    }

    if (!configurado) {
        console.log('⚠️ Sistema não configurado, aplicando correção...');
        corrigirExclusaoTarefas();
        return true;
    }

    console.log('✅ Sistema funcionando corretamente');
    return true;
}

// Função para forçar reconfiguração
function forcarReconfiguracao() {
    console.log('🔄 Forçando reconfiguração...');
    window.exclusaoTarefasConfigurada = false;
    corrigirExclusaoTarefas();
}

// Configurar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', corrigirExclusaoTarefas);
} else {
    corrigirExclusaoTarefas();
}

// Configurar também no evento load
window.addEventListener('load', corrigirExclusaoTarefas);

// Funções globais para teste
window.corrigirExclusaoTarefas = corrigirExclusaoTarefas;
window.verificarStatusExclusao = verificarStatusExclusao;
window.forcarReconfiguracao = forcarReconfiguracao;

console.log('✅ Correção para exclusão de tarefas carregada!');
console.log('📝 Use verificarStatusExclusao() para verificar o status');
console.log('📝 Use forcarReconfiguracao() para forçar reconfiguração');
