# Sistema de Logging Configurável

## 📋 Visão Geral

O Sistema de Gestão de Projetos 2.0 inclui um sistema de logging avançado e configurável que permite controlar os logs exibidos no console do navegador de forma granular.

## 🚀 Funcionalidades

### 1. **Controle de Níveis Globais**
- **none**: Desabilita todos os logs
- **error**: Apenas erros
- **warn**: Warnings + Erros
- **info**: Info + Warnings + Erros
- **debug**: Todos os logs

### 2. **Controle por Módulo**
- **gantt**: Logs relacionados ao gráfico Gantt
- **predecessoras**: Logs de validação de predecessoras
- **tarefas**: Logs de operações de tarefas
- **projetos**: Logs de carregamento e renderização
- **auth**: Logs de autenticação e permissões

### 3. **Controle por Categoria**
- **rendering**: Logs de renderização
- **events**: Logs de eventos
- **calculations**: Logs de cálculos
- **validation**: Logs de validação
- **errors**: Sempre ativo para erros

## 🎛️ Como Usar

### **Método 1: Via URL (Mais Rápido)**
```
http://localhost:5000/?log=debug    # Ativar todos os logs
http://localhost:5000/?log=warn     # Apenas warnings e erros
http://localhost:5000/?log=error    # Apenas erros
http://localhost:5000/?log=none     # Desabilitar todos
```

### **Método 2: Via Painel de Controle**
1. Clique no botão flutuante azul (📝) no canto inferior direito
2. Use o painel para configurar logs por módulo
3. Ajuste o nível global
4. Configure exibição de timestamp, módulo e categoria

### **Método 3: Via Console do Navegador**
```javascript
// Mudar nível global
window.logger.level = 'debug';

// Mudar configuração de módulo
window.LogConfig.updateModuleConfig('gantt', { level: 'warn' });

// Ver configurações atuais
console.log(window.LogConfig.modules);

// Abrir painel de controle
window.showLogPanel();
```

## 📱 Interface Visual

### **Botão Flutuante**
- **Posição**: Canto inferior direito
- **Cor**: Azul (#007bff)
- **Ícone**: 📝
- **Função**: Abrir/fechar painel de controle

### **Painel de Controle**
- **Posição**: Lado direito da tela
- **Largura**: 500px
- **Altura**: 100% da tela
- **Tema**: Escuro (IDE-like)

## ⚙️ Configurações Padrão

### **Desenvolvimento (localhost)**
```javascript
{
    "logLevel": "debug",
    "modules": {
        "gantt": { "level": "warn" },
        "predecessoras": { "level": "info" },
        "tarefas": { "level": "warn" },
        "projetos": { "level": "warn" },
        "auth": { "level": "info" }
    }
}
```

### **Produção**
```javascript
{
    "logLevel": "warn",
    "modules": {
        "gantt": { "level": "error" },
        "predecessoras": { "level": "warn" },
        "tarefas": { "level": "error" },
        "projetos": { "level": "error" },
        "auth": { "level": "warn" }
    }
}
```

## 🔧 Personalização

### **Adicionar Novo Módulo**
```javascript
window.LogConfig.modules.novoModulo = {
    enabled: true,
    level: 'info',
    categories: {
        'feature1': true,
        'feature2': false,
        'errors': true
    }
};
```

### **Usar Logs com Módulo**
```javascript
// Log simples
window.log.debug('Mensagem de debug');

// Log com módulo e categoria
window.logModule('gantt', 'rendering', 'debug', 'Renderizando Gantt...');

// Log com dados
window.log.info('Dados carregados', { projetos: 5, tarefas: 25 });
```

## 📊 Monitoramento

### **Estatísticas em Tempo Real**
- Contador de logs
- Uso de memória
- Histórico de logs
- Exportação de logs

### **Exportação**
- Formato: JSON
- Inclui: Logs, configurações, timestamp
- Nome: `logs-YYYY-MM-DDTHH-MM-SS.json`

## 🚨 Solução de Problemas

### **Logs Não Aparecem**
1. Verificar se o nível global não está em 'none'
2. Verificar se o módulo está habilitado
3. Verificar se a categoria está ativa
4. Recarregar a página

### **Painel Não Abre**
1. Verificar se os scripts foram carregados
2. Verificar console para erros JavaScript
3. Aguardar 1 segundo após carregamento da página
4. Usar `window.showLogPanel()` no console

### **Configurações Não Salvam**
1. Verificar localStorage do navegador
2. Verificar se não há bloqueio de cookies
3. Usar modo privado para teste
4. Verificar permissões do navegador

## 🔒 Segurança

### **Em Produção**
- Logs mínimos por padrão
- Erros sempre visíveis
- Configurações restritas
- Sem informações sensíveis

### **Em Desenvolvimento**
- Logs detalhados por padrão
- Configurações flexíveis
- Debug completo
- Painel de controle ativo

## 📚 Exemplos Práticos

### **Desabilitar Logs de Gantt**
```javascript
window.LogConfig.updateModuleConfig('gantt', { level: 'none' });
```

### **Ativar Apenas Validações de Predecessoras**
```javascript
window.LogConfig.updateModuleConfig('predecessoras', { 
    level: 'info',
    categories: {
        'validation': true,
        'calculations': false,
        'events': false
    }
});
```

### **Configuração Temporária para Debug**
```javascript
// Salvar configuração atual
const configAtual = JSON.stringify(window.LogConfig.modules);

// Configurar para debug
Object.values(window.LogConfig.modules).forEach(mod => {
    mod.level = 'debug';
    mod.enabled = true;
});

// Restaurar configuração
setTimeout(() => {
    window.LogConfig.modules = JSON.parse(configAtual);
}, 30000); // 30 segundos
```

## 🎯 Dicas de Uso

1. **Desenvolvimento**: Use `?log=debug` na URL para logs completos
2. **Testes**: Configure módulos específicos para o que está testando
3. **Produção**: Mantenha logs em nível 'warn' ou 'error'
4. **Debug**: Use o painel de controle para ajustes finos
5. **Performance**: Desabilite logs desnecessários em produção

---

**✅ Sistema de Logging configurado e funcionando!**

Para mais informações, consulte o código em `static/js/logger.js`, `static/js/log-config.js` e `static/js/log-panel.js`.
