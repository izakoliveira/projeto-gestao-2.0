/**
 * Sistema de Logging Configurável
 * Sistema de Gestão de Projetos v2.0.0
 */

class Logger {
    constructor() {
        this.enabled = this.getLogLevel() !== 'none';
        this.level = this.getLogLevel();
        this.prefix = '[SGP]';

        // Configurar nível de log baseado na URL ou localStorage
        this.setupLogLevel();
    }

    getLogLevel() {
        // Verificar se está em modo de desenvolvimento
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return localStorage.getItem('logLevel') || 'debug';
        }

        // Em produção, logs mínimos por padrão
        return localStorage.getItem('logLevel') || 'warn';
    }

    setupLogLevel() {
        // Permitir mudar o nível via URL (ex: ?log=debug)
        const urlParams = new URLSearchParams(window.location.search);
        const logParam = urlParams.get('log');

        if (logParam) {
            this.level = logParam;
            localStorage.setItem('logLevel', logParam);
        }

        // Removido botão flutuante de alternância de logs
    }

    // Removido método createLogToggle()

    shouldLog(level) {
        if (!this.enabled) return false;

        const levels = {
            'none': 0,
            'error': 1,
            'warn': 2,
            'info': 3,
            'debug': 4
        };

        return levels[this.level] >= levels[level];
    }

    formatMessage(level, message, ...args) {
        const timestamp = new Date().toLocaleTimeString();
        const emoji = {
            'error': '❌',
            'warn': '⚠️',
            'info': 'ℹ️',
            'debug': '🔍'
        }[level] || '📝';

        return `${emoji} ${this.prefix} [${level.toUpperCase()}] ${timestamp}: ${message}`;
    }

    error(message, ...args) {
        if (this.shouldLog('error')) {
            console.error(this.formatMessage('error', message), ...args);
        }
    }

    warn(message, ...args) {
        if (this.shouldLog('warn')) {
            console.warn(this.formatMessage('warn', message), ...args);
        }
    }

    info(message, ...args) {
        if (this.shouldLog('info')) {
            console.info(this.formatMessage('info', message), ...args);
        }
    }

    debug(message, ...args) {
        if (this.shouldLog('debug')) {
            console.log(this.formatMessage('debug', message), ...args);
        }
    }

    // Método para substituir console.log global
    replaceConsole() {
        if (this.level === 'none') {
            // Desabilitar todos os logs
            window.console.log = () => { };
            window.console.info = () => { };
            window.console.warn = () => { };
            window.console.debug = () => { };
            // Manter apenas erros
            window.console.error = console.error;
        } else if (this.level === 'error') {
            // Apenas erros
            window.console.log = () => { };
            window.console.info = () => { };
            window.console.warn = () => { };
            window.console.debug = () => { };
        } else if (this.level === 'warn') {
            // Erros e warnings
            window.console.log = () => { };
            window.console.info = () => { };
            window.console.debug = () => { };
        } else if (this.level === 'info') {
            // Erros, warnings e info
            window.console.log = () => { };
            window.console.debug = () => { };
        }
        // Se for 'debug', manter todos os logs
    }
}

// Criar instância global
window.logger = new Logger();

// Aplicar configurações de log
window.logger.replaceConsole();

// Função global para logs rápidos
window.log = {
    error: (...args) => window.logger.error(...args),
    warn: (...args) => window.logger.warn(...args),
    info: (...args) => window.logger.info(...args),
    debug: (...args) => window.logger.debug(...args)
};

// Log de inicialização
window.logger.info('Sistema de logging inicializado', {
    level: window.logger.level,
    enabled: window.logger.enabled,
    url: window.location.href
});

console.log('🚀 Logger configurado! Use ?log=debug na URL para ativar logs detalhados');
