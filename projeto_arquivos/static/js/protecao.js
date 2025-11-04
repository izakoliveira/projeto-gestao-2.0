/**
 * Sistema de Proteção contra Visualização de Código-Fonte
 * Dificulta (não impossibilita) a visualização do código
 */

(function() {
    'use strict';

    // 1. Desabilitar clique direito
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    }, false);

    // 2. Desabilitar teclas de atalho comuns
    document.addEventListener('keydown', function(e) {
        // F12 (DevTools)
        if (e.keyCode === 123) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+Shift+I (DevTools)
        if (e.ctrlKey && e.shiftKey && e.keyCode === 73) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+Shift+J (Console)
        if (e.ctrlKey && e.shiftKey && e.keyCode === 74) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+Shift+C (Inspecionar elemento)
        if (e.ctrlKey && e.shiftKey && e.keyCode === 67) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+U (Ver código-fonte)
        if (e.ctrlKey && e.keyCode === 85) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+S (Salvar página)
        if (e.ctrlKey && e.keyCode === 83) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+P (Imprimir - pode revelar código)
        if (e.ctrlKey && e.keyCode === 80) {
            e.preventDefault();
            return false;
        }
    }, false);

    // 3. Detectar DevTools aberto (método avançado)
    let devtoolsOpen = false;
    const threshold = 160;
    
    const detectDevTools = () => {
        const widthThreshold = window.outerWidth - window.innerWidth > threshold;
        const heightThreshold = window.outerHeight - window.innerHeight > threshold;
        
        if (widthThreshold || heightThreshold) {
            if (!devtoolsOpen) {
                devtoolsOpen = true;
                // Redirecionar ou limpar página
                document.body.innerHTML = '<h1 style="text-align:center; margin-top:50px;">⚠️ Acesso não autorizado detectado</h1>';
            }
        } else {
            devtoolsOpen = false;
        }
    };
    
    // Verificar a cada segundo
    setInterval(detectDevTools, 1000);

    // 4. Desabilitar seleção de texto
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    }, false);

    // 5. Desabilitar arrastar texto/imagens
    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
    }, false);

    // 6. Desabilitar copiar
    document.addEventListener('copy', function(e) {
        e.preventDefault();
        return false;
    }, false);

    // 7. Limpar console periodicamente
    setInterval(function() {
        console.clear();
    }, 1000);

    // 8. Ofuscar console
    console.log = function() {};
    console.info = function() {};
    console.warn = function() {};
    console.error = function() {};
    console.debug = function() {};

    // 9. Detectar ferramentas de debug
    const devtools = /./;
    devtools.toString = function() {
        devtoolsOpen = true;
        return 'DevTools detectado!';
    };

    // 10. Proteger contra iframes não autorizados
    if (window.top !== window.self) {
        window.top.location = window.self.location;
    }

    // 11. Adicionar marca d'água invisível no DOM
    const watermark = document.createElement('div');
    watermark.style.display = 'none';
    watermark.setAttribute('data-protection', 'Sistema protegido - Acesso monitorado');
    document.body.appendChild(watermark);

    // 12. Desabilitar debugger
    setInterval(function() {
        debugger;
    }, 100);

})();

// Mensagem de aviso no console (executada antes da proteção)
console.log('%c⚠️ ATENÇÃO', 'color: red; font-size: 40px; font-weight: bold;');
console.log('%cEste é um sistema privado.', 'font-size: 20px;');
console.log('%cA visualização não autorizada do código-fonte é proibida.', 'font-size: 16px;');
console.log('%cTodas as atividades são monitoradas e registradas.', 'font-size: 16px;');
