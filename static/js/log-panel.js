/**
 * Painel de Controle de Logs
 * Sistema de Gestão de Projetos v2.0.0
 */

class LogPanel {
    constructor() {
        this.isVisible = false;
        this.panel = null;
        this.logContainer = null;
        this.logs = [];
        this.maxLogs = 100;

        this.init();
    }

    init() {
        // Criar botão flutuante para abrir o painel
        this.createToggleButton();

        // Criar o painel principal
        this.createPanel();

        // Interceptar logs para capturá-los
        this.interceptLogs();

        // Carregar configurações salvas
        this.loadSettings();
    }

    createToggleButton() {
        const button = document.createElement('div');
        button.id = 'log-panel-toggle';
        button.innerHTML = `
            <div style="
                position: fixed; 
                bottom: 20px; 
                right: 20px; 
                z-index: 9998; 
                background: #007bff; 
                color: white; 
                width: 50px; 
                height: 50px; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                cursor: pointer; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                font-size: 20px;
                transition: all 0.3s ease;
            " title="Painel de Logs">
                📝
            </div>
        `;

        button.addEventListener('click', () => this.toggle());
        document.body.appendChild(button);
    }

    createPanel() {
        this.panel = document.createElement('div');
        this.panel.id = 'log-panel';
        this.panel.innerHTML = `
            <div style="
                position: fixed; 
                top: 0; 
                right: 0; 
                width: 500px; 
                height: 100vh; 
                background: #1e1e1e; 
                color: #fff; 
                z-index: 9999; 
                font-family: 'Courier New', monospace; 
                font-size: 12px; 
                display: none;
                flex-direction: column;
                box-shadow: -2px 0 10px rgba(0,0,0,0.5);
            ">
                <!-- Header -->
                <div style="
                    background: #333; 
                    padding: 10px; 
                    border-bottom: 1px solid #555; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;
                ">
                    <h4 style="margin: 0; color: #fff;">📝 Painel de Logs</h4>
                    <div>
                        <button id="log-clear" style="
                            background: #dc3545; 
                            color: white; 
                            border: none; 
                            padding: 5px 10px; 
                            border-radius: 3px; 
                            cursor: pointer; 
                            margin-right: 10px;
                        ">Limpar</button>
                        <button id="log-close" style="
                            background: #6c757d; 
                            color: white; 
                            border: none; 
                            padding: 5px 10px; 
                            border-radius: 3px; 
                            cursor: pointer;
                        ">✕</button>
                    </div>
                </div>
                
                <!-- Controls -->
                <div style="
                    background: #2d2d2d; 
                    padding: 10px; 
                    border-bottom: 1px solid #555;
                ">
                    <div style="margin-bottom: 10px;">
                        <label style="margin-right: 10px; color: #ccc;">Nível Global:</label>
                        <select id="log-level-global" style="
                            background: #444; 
                            color: #fff; 
                            border: 1px solid #555; 
                            padding: 3px; 
                            border-radius: 3px;
                        ">
                            <option value="none">Nenhum</option>
                            <option value="error">Apenas Erros</option>
                            <option value="warn">Warnings + Erros</option>
                            <option value="info">Info + Warnings + Erros</option>
                            <option value="debug">Todos</option>
                        </select>
                    </div>
                    
                    <div style="
                        display: grid; 
                        grid-template-columns: 1fr 1fr; 
                        gap: 10px; 
                        font-size: 11px;
                    ">
                        <div>
                            <label style="color: #ccc;">Módulos:</label>
                            <div id="log-modules" style="margin-top: 5px;"></div>
                        </div>
                        <div>
                            <label style="color: #ccc;">Configurações:</label>
                            <div style="margin-top: 5px;">
                                <label style="display: block; margin-bottom: 5px;">
                                    <input type="checkbox" id="log-show-timestamp" checked> Timestamp
                                </label>
                                <label style="display: block; margin-bottom: 5px;">
                                    <input type="checkbox" id="log-show-module" checked> Módulo
                                </label>
                                <label style="display: block; margin-bottom: 5px;">
                                    <input type="checkbox" id="log-show-category" checked> Categoria
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Log Container -->
                <div id="log-container" style="
                    flex: 1; 
                    overflow-y: auto; 
                    padding: 10px; 
                    background: #000;
                "></div>
                
                <!-- Footer -->
                <div style="
                    background: #333; 
                    padding: 10px; 
                    border-top: 1px solid #555; 
                    text-align: center; 
                    color: #ccc;
                    font-size: 11px;
                ">
                    <span id="log-count">0 logs</span> | 
                    <span id="log-memory">0 KB</span> | 
                    <button id="log-export" style="
                        background: #28a745; 
                        color: white; 
                        border: none; 
                        padding: 3px 8px; 
                        border-radius: 3px; 
                        cursor: pointer; 
                        margin-left: 10px;
                    ">Exportar</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.panel);

        // Configurar eventos
        this.setupEvents();

        // Configurar módulos
        this.setupModules();
    }

    setupEvents() {
        // Botão fechar
        document.getElementById('log-close').addEventListener('click', () => this.hide());

        // Botão limpar
        document.getElementById('log-clear').addEventListener('click', () => this.clearLogs());

        // Botão exportar
        document.getElementById('log-export').addEventListener('click', () => this.exportLogs());

        // Nível global
        document.getElementById('log-level-global').addEventListener('change', (e) => {
            const level = e.target.value;
            if (window.logger) {
                window.logger.level = level;
                localStorage.setItem('logLevel', level);
            }
        });

        // Configurações
        ['timestamp', 'module', 'category'].forEach(setting => {
            document.getElementById(`log-show-${setting}`).addEventListener('change', (e) => {
                if (window.LogConfig) {
                    window.LogConfig.global[`show${setting.charAt(0).toUpperCase() + setting.slice(1)}`] = e.target.checked;
                    window.LogConfig.saveConfig();
                }
            });
        });
    }

    setupModules() {
        const container = document.getElementById('log-modules');

        if (window.LogConfig) {
            Object.entries(window.LogConfig.modules).forEach(([name, config]) => {
                const div = document.createElement('div');
                div.style.marginBottom = '5px';
                div.innerHTML = `
                    <label style="color: #ccc; font-size: 10px;">
                        <input type="checkbox" ${config.enabled ? 'checked' : ''} 
                               onchange="window.LogConfig.updateModuleConfig('${name}', {enabled: this.checked})">
                        ${name}
                    </label>
                    <select onchange="window.LogConfig.updateModuleConfig('${name}', {level: this.value})" 
                            style="
                                background: #444; 
                                color: #fff; 
                                border: 1px solid #555; 
                                padding: 2px; 
                                border-radius: 2px; 
                                margin-left: 5px; 
                                font-size: 10px;
                            ">
                        <option value="none" ${config.level === 'none' ? 'selected' : ''}>Nenhum</option>
                        <option value="error" ${config.level === 'error' ? 'selected' : ''}>Erro</option>
                        <option value="warn" ${config.level === 'warn' ? 'selected' : ''}>Warn</option>
                        <option value="info" ${config.level === 'info' ? 'selected' : ''}>Info</option>
                        <option value="debug" ${config.level === 'debug' ? 'selected' : ''}>Debug</option>
                    </select>
                `;
                container.appendChild(div);
            });
        }
    }

    interceptLogs() {
        // Interceptar console.log, console.info, console.warn, console.error
        const originalMethods = {
            log: console.log,
            info: console.info,
            warn: console.warn,
            error: console.error
        };

        Object.entries(originalMethods).forEach(([method, original]) => {
            console[method] = (...args) => {
                // Chamar método original
                original.apply(console, args);

                // Capturar para o painel
                this.addLog(method, args);
            };
        });
    }

    addLog(level, args) {
        const log = {
            id: Date.now() + Math.random(),
            timestamp: new Date(),
            level: level,
            message: args.map(arg =>
                typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
            ).join(' '),
            raw: args
        };

        this.logs.unshift(log);

        // Limitar número de logs
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(0, this.maxLogs);
        }

        // Atualizar painel se estiver visível
        if (this.isVisible) {
            this.updateLogDisplay();
        }

        // Atualizar contadores
        this.updateCounters();
    }

    updateLogDisplay() {
        if (!this.logContainer) return;

        this.logContainer.innerHTML = this.logs.map(log => {
            const levelColors = {
                error: '#dc3545',
                warn: '#ffc107',
                info: '#17a2b8',
                debug: '#6c757d'
            };

            const color = levelColors[log.level] || '#6c757d';
            const time = log.timestamp.toLocaleTimeString();

            return `
                <div style="
                    margin-bottom: 5px; 
                    padding: 5px; 
                    background: #1a1a1a; 
                    border-left: 3px solid ${color}; 
                    border-radius: 3px;
                ">
                    <div style="
                        display: flex; 
                        justify-content: space-between; 
                        margin-bottom: 3px;
                    ">
                        <span style="color: ${color}; font-weight: bold; text-transform: uppercase;">
                            ${log.level}
                        </span>
                        <span style="color: #666; font-size: 10px;">
                            ${time}
                        </span>
                    </div>
                    <div style="
                        color: #fff; 
                        word-wrap: break-word; 
                        white-space: pre-wrap;
                        font-family: 'Courier New', monospace;
                        font-size: 11px;
                    ">${log.message}</div>
                </div>
            `;
        }).join('');
    }

    updateCounters() {
        const countEl = document.getElementById('log-count');
        const memoryEl = document.getElementById('log-memory');

        if (countEl) {
            countEl.textContent = `${this.logs.length} logs`;
        }

        if (memoryEl) {
            const memory = JSON.stringify(this.logs).length;
            memoryEl.textContent = `${Math.round(memory / 1024)} KB`;
        }
    }

    clearLogs() {
        this.logs = [];
        this.updateLogDisplay();
        this.updateCounters();
    }

    exportLogs() {
        const data = {
            timestamp: new Date().toISOString(),
            logs: this.logs,
            config: window.LogConfig ? window.LogConfig.modules : {}
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    show() {
        this.isVisible = true;
        this.panel.style.display = 'flex';
        this.logContainer = document.getElementById('log-container');
        this.updateLogDisplay();
        this.updateCounters();

        // Carregar configurações atuais
        if (window.logger) {
            document.getElementById('log-level-global').value = window.logger.level;
        }

        if (window.LogConfig) {
            document.getElementById('log-show-timestamp').checked = window.LogConfig.global.showTimestamp;
            document.getElementById('log-show-module').checked = window.LogConfig.global.showModule;
            document.getElementById('log-show-category').checked = window.LogConfig.global.showCategory;
        }
    }

    hide() {
        this.isVisible = false;
        this.panel.style.display = 'none';
    }

    loadSettings() {
        // Carregar configurações salvas
        const savedLevel = localStorage.getItem('logLevel');
        if (savedLevel && window.logger) {
            window.logger.level = savedLevel;
        }
    }
}

// Inicializar painel quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    // Aguardar um pouco para os outros scripts carregarem
    setTimeout(() => {
        window.logPanel = new LogPanel();
    }, 1000);
});

// Função global para abrir o painel
window.showLogPanel = () => {
    if (window.logPanel) {
        window.logPanel.show();
    }
};
