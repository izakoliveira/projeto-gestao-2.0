/**
 * Configuração de Logs por Módulo
 * Sistema de Gestão de Projetos v2.0.0
 */

window.LogConfig = {
    // Configurações por módulo
    modules: {
        'gantt': {
            enabled: true,
            level: 'warn', // Apenas warnings e erros por padrão
            categories: {
                'rendering': false,    // Logs de renderização
                'events': false,       // Logs de eventos
                'calculations': false, // Logs de cálculos
                'errors': true         // Sempre mostrar erros
            }
        },
        'predecessoras': {
            enabled: true,
            level: 'info', // Info, warnings e erros
            categories: {
                'validation': true,    // Validações importantes
                'calculations': false, // Cálculos detalhados
                'events': false,       // Eventos de input
                'errors': true         // Sempre mostrar erros
            }
        },
        'tarefas': {
            enabled: true,
            level: 'warn',
            categories: {
                'crud': false,         // Operações CRUD
                'validation': false,   // Validações
                'events': false,       // Eventos
                'errors': true         // Sempre mostrar erros
            }
        },
        'projetos': {
            enabled: true,
            level: 'warn',
            categories: {
                'loading': false,      // Carregamento de dados
                'rendering': false,    // Renderização
                'events': false,       // Eventos
                'errors': true         // Sempre mostrar erros
            }
        },
        'auth': {
            enabled: true,
            level: 'info', // Info, warnings e erros
            categories: {
                'login': true,         // Logins importantes
                'sessions': false,     // Sessões
                'permissions': true,   // Permissões
                'errors': true         // Sempre mostrar erros
            }
        }
    },

    // Configurações globais
    global: {
        showTimestamp: true,
        showModule: true,
        showCategory: true,
        maxLogs: 100, // Limitar número de logs em memória
        autoClean: true // Limpar logs antigos automaticamente
    },

    // Método para verificar se um log deve ser exibido
    shouldLog(module, category, level) {
        if (!this.modules[module]) {
            return level === 'error'; // Sempre mostrar erros
        }

        const moduleConfig = this.modules[module];
        
        if (!moduleConfig.enabled) {
            return level === 'error';
        }

        // Verificar nível do módulo
        const levels = ['none', 'error', 'warn', 'info', 'debug'];
        const moduleLevel = levels.indexOf(moduleConfig.level);
        const currentLevel = levels.indexOf(level);
        
        if (currentLevel > moduleLevel) {
            return false;
        }

        // Verificar categoria específica
        if (category && moduleConfig.categories[category] !== undefined) {
            return moduleConfig.categories[category];
        }

        return true;
    },

    // Método para obter configuração de um módulo
    getModuleConfig(module) {
        return this.modules[module] || { enabled: false, level: 'none' };
    },

    // Método para atualizar configuração de um módulo
    updateModuleConfig(module, config) {
        if (this.modules[module]) {
            Object.assign(this.modules[module], config);
            localStorage.setItem('logConfig', JSON.stringify(this.modules));
        }
    },

    // Método para salvar configurações
    saveConfig() {
        localStorage.setItem('logConfig', JSON.stringify(this.modules));
    },

    // Método para carregar configurações salvas
    loadConfig() {
        const saved = localStorage.getItem('logConfig');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                Object.assign(this.modules, parsed);
            } catch (e) {
                console.warn('Erro ao carregar configuração de logs:', e);
            }
        }
    },

    // Método para resetar configurações
    resetConfig() {
        localStorage.removeItem('logConfig');
        location.reload();
    }
};

// Carregar configurações salvas
LogConfig.loadConfig();

// Função global para logs com módulo e categoria
window.logModule = function(module, category, level, message, ...args) {
    if (LogConfig.shouldLog(module, category, level)) {
        const timestamp = LogConfig.global.showTimestamp ? `[${new Date().toLocaleTimeString()}]` : '';
        const moduleTag = LogConfig.global.showModule ? `[${module.toUpperCase()}]` : '';
        const categoryTag = LogConfig.global.showCategory && category ? `[${category.toUpperCase()}]` : '';
        
        const prefix = `${timestamp}${moduleTag}${categoryTag}`.replace(/^\[/, '').replace(/\]$/, '');
        const fullMessage = `${prefix}: ${message}`;
        
        switch (level) {
            case 'error':
                console.error(fullMessage, ...args);
                break;
            case 'warn':
                console.warn(fullMessage, ...args);
                break;
            case 'info':
                console.info(fullMessage, ...args);
                break;
            case 'debug':
                console.log(fullMessage, ...args);
                break;
            default:
                console.log(fullMessage, ...args);
        }
    }
};

// Log de inicialização
window.logModule('system', 'init', 'info', 'Configuração de logs carregada', {
    modules: Object.keys(LogConfig.modules),
    global: LogConfig.global
});
