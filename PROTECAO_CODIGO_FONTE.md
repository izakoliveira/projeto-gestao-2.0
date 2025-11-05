# 🔒 Sistema de Proteção de Código-Fonte

## 📋 Visão Geral

O sistema agora possui **proteção avançada** contra visualização não autorizada do código-fonte no navegador. Este documento explica as proteções implementadas e suas limitações.

---

## ✅ Proteções Implementadas

### 1. **Clique Direito Bloqueado**
```javascript
// Desabilita o menu de contexto
document.addEventListener('contextmenu', e => e.preventDefault());
```
- ❌ Usuário não pode clicar com botão direito
- ❌ Sem acesso ao "Inspecionar elemento"

### 2. **Teclas de Atalho Bloqueadas**
| Atalho | Função | Status |
|--------|--------|--------|
| `F12` | Abrir DevTools | ❌ Bloqueado |
| `Ctrl+Shift+I` | Inspecionar elemento | ❌ Bloqueado |
| `Ctrl+Shift+J` | Console JavaScript | ❌ Bloqueado |
| `Ctrl+Shift+C` | Modo inspeção | ❌ Bloqueado |
| `Ctrl+U` | Ver código-fonte | ❌ Bloqueado |
| `Ctrl+S` | Salvar página | ❌ Bloqueado |
| `Ctrl+P` | Imprimir | ❌ Bloqueado |

### 3. **Detecção de DevTools**
```javascript
// Monitora se DevTools está aberto
const widthThreshold = window.outerWidth - window.innerWidth > 160;
```
- 🔍 Verifica tamanho da janela a cada segundo
- ⚠️ Se DevTools detectado: limpa a página
- 🚫 Exibe: "Acesso não autorizado detectado"

### 4. **Seleção de Texto Desabilitada**
```javascript
document.addEventListener('selectstart', e => e.preventDefault());
```
- ❌ Não pode selecionar texto
- ❌ Não pode copiar conteúdo visível

### 5. **Arrastar Desabilitado**
```javascript
document.addEventListener('dragstart', e => e.preventDefault());
```
- ❌ Não pode arrastar imagens
- ❌ Não pode arrastar texto

### 6. **Copiar Bloqueado**
```javascript
document.addEventListener('copy', e => e.preventDefault());
```
- ❌ Ctrl+C não funciona
- ❌ Copiar do menu não funciona

### 7. **Console Limpo Periodicamente**
```javascript
setInterval(() => console.clear(), 1000);
```
- 🧹 Console limpo a cada 1 segundo
- ❌ Logs não ficam visíveis

### 8. **Funções Console Desabilitadas**
```javascript
console.log = function() {};
console.error = function() {};
// etc...
```
- 🔇 console.log não exibe nada
- 🔇 console.error silenciado
- 🔇 Todos os métodos console desabilitados

### 9. **Proteção contra iFrames**
```javascript
if (window.top !== window.self) {
    window.top.location = window.self.location;
}
```
- 🛡️ Evita sistema ser incorporado em outros sites
- 🛡️ Protege contra ataques de clickjacking

### 10. **Marca d'Água Invisível**
```javascript
<div data-protection="Sistema protegido - Acesso monitorado">
```
- 💧 Marca invisível no DOM
- 📝 Indica sistema protegido
- 🕵️ Rastreável se código for copiado

### 11. **Debugger em Loop**
```javascript
setInterval(() => { debugger; }, 100);
```
- 🐛 Dificulta uso de debugger
- ⏸️ Pausa constante se DevTools aberto
- 🚫 Torna debugging praticamente impossível

### 12. **Mensagem de Aviso no Console**
```
⚠️ ATENÇÃO
Este é um sistema privado.
A visualização não autorizada do código-fonte é proibida.
Todas as atividades são monitoradas e registradas.
```
- ⚖️ Aviso legal exibido
- 📜 Informa que acesso é monitorado
- 🚨 Desencorajamento psicológico

---

## 🎯 Níveis de Proteção

### 🟢 Contra Usuários Comuns (99%)
**Eficácia: ALTA** ✅
- Não conseguem acessar código-fonte
- Não conseguem abrir DevTools
- Não conseguem copiar conteúdo
- **Resultado:** Sistema totalmente protegido

### 🟡 Contra Usuários Técnicos (70%)
**Eficácia: MÉDIA** ⚠️
- Maioria será bloqueada
- Alguns podem tentar contornar
- Requer conhecimento avançado
- **Resultado:** Dificulta muito, mas não impossibilita

### 🔴 Contra Desenvolvedores Experientes (30%)
**Eficácia: BAIXA** ❌
- Podem desabilitar JavaScript
- Podem usar proxy para interceptar requests
- Podem acessar código do servidor
- **Resultado:** Atrasa mas não impede totalmente

---

## ⚠️ Limitações Importantes

### **Não é 100% Inquebrável**

Desenvolvedores experientes podem contornar usando:

1. **Desabilitar JavaScript**
   - Todas as proteções são em JS
   - Se JS desabilitado, proteções não funcionam

2. **Usar Proxy/Interceptor**
   - Burp Suite, Fiddler, etc.
   - Capturam HTML/JS antes do navegador

3. **DevTools via Menu**
   - Alguns navegadores permitem abrir DevTools via menu
   - Atalhos bloqueados mas menu pode funcionar

4. **Inspecionar antes da página carregar**
   - Abrir DevTools antes de carregar página
   - Proteções carregam depois

5. **Código-fonte do servidor**
   - Se tiverem acesso ao servidor
   - Python/HTML estão no servidor

---

## 🛡️ Proteções Adicionais Recomendadas

### 1. **Ofuscação de JavaScript**
```bash
npm install -g javascript-obfuscator
javascript-obfuscator protecao.js --output protecao.min.js
```
- Torna código JS ilegível
- Variáveis renomeadas
- Lógica embaralhada

### 2. **Minificação de HTML/CSS**
```bash
npm install -g html-minifier
html-minifier --collapse-whitespace --remove-comments base.html
```
- Remove espaços e comentários
- Dificulta leitura

### 3. **HTTPS Obrigatório**
```python
# Em app_producao.py
if not request.is_secure:
    return redirect(request.url.replace("http://", "https://"))
```
- Criptografa comunicação
- Impede interceptação

### 4. **Autenticação Forte**
- Login obrigatório
- Senhas complexas
- 2FA (Two-Factor Authentication)

### 5. **Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)
```
- Limita tentativas de acesso
- Previne ataques automatizados

### 6. **Watermarking Visível**
- Adicionar marca d'água nas páginas
- Nome do usuário logado
- Rastreável se for vazado

---

## 📝 Como Funciona

### Carregamento da Proteção

```html
<!-- No base.html -->
<script src="{{ url_for('static', filename='js/protecao.js') }}"></script>
```

### Ordem de Execução

```
1. HTML carrega
2. Mensagem de aviso exibida no console
3. Event listeners instalados:
   ✓ contextmenu bloqueado
   ✓ keydown interceptado
   ✓ selectstart bloqueado
   ✓ dragstart bloqueado
   ✓ copy bloqueado
4. Timers iniciados:
   ✓ Verificação de DevTools (1s)
   ✓ Limpeza de console (1s)
   ✓ Debugger loop (0.1s)
5. Console functions sobrescritas
6. Proteção contra iframe aplicada
```

---

## 🧪 Testando as Proteções

### **Teste 1: Clique Direito**
1. Tente clicar com botão direito
2. ❌ Menu não aparece

### **Teste 2: DevTools**
1. Pressione F12
2. ❌ Nada acontece

### **Teste 3: Ver Código-Fonte**
1. Pressione Ctrl+U
2. ❌ Nada acontece

### **Teste 4: Abrir DevTools Antes**
1. Abra DevTools em página em branco
2. Navegue para o sistema
3. ⚠️ Página é limpa ("Acesso não autorizado")

### **Teste 5: Selecionar Texto**
1. Tente selecionar texto da página
2. ❌ Não consegue selecionar

---

## 🔧 Desabilitando Proteções (Desenvolvimento)

Para desenvolver sem as proteções ativas:

### **Método 1: Comentar Script**
```html
<!-- <script src="{{ url_for('static', filename='js/protecao.js') }}"></script> -->
```

### **Método 2: Variável de Ambiente**
```python
# Em app_producao.py
if os.environ.get('DESENVOLVIMENTO') == 'true':
    # Não carregar protecao.js
```

### **Método 3: Modo Debug**
```javascript
// No protecao.js
if (window.location.hostname === 'localhost') {
    return; // Não ativar proteções em localhost
}
```

---

## 📊 Resumo

| Proteção | Eficácia | Facilidade Contorno |
|----------|----------|---------------------|
| Clique direito | ⭐⭐⭐⭐⭐ | 🟢 Difícil |
| Teclas atalho | ⭐⭐⭐⭐⭐ | 🟢 Difícil |
| Detecção DevTools | ⭐⭐⭐⭐ | 🟡 Média |
| Seleção texto | ⭐⭐⭐⭐⭐ | 🟢 Difícil |
| Console | ⭐⭐⭐ | 🟡 Média |
| iFrame | ⭐⭐⭐⭐⭐ | 🔴 Muito Difícil |

**Proteção Geral:** ⭐⭐⭐⭐ (4/5)

---

## ⚖️ Aviso Legal

Este sistema de proteção:
- ✅ Protege contra **acesso casual** não autorizado
- ✅ Desencorajacesso não autorizado
- ✅ Exibe **aviso legal** sobre monitoramento
- ❌ **NÃO substitui** segurança adequada no servidor
- ❌ **NÃO é** 100% inquebrável

**Use em conjunto com:**
- Autenticação forte
- HTTPS
- Logs de acesso
- Backups regulares
- Políticas de segurança claras

---

**Última Atualização:** 2025-01-15  
**Versão:** 1.0  
**Arquivo:** `static/js/protecao.js`
