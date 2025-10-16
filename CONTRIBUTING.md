# Contribuindo para o Sistema de Gestão de Projetos 2.0

Obrigado por seu interesse em contribuir! Este documento fornece diretrizes e informações sobre como contribuir para este projeto.

## 🚀 Como Contribuir

### 1. **Fork e Clone**
```bash
# Fork do repositório no GitHub
git clone https://github.com/SEU_USUARIO/sistema-gestao-projetos-2.0.git
cd sistema-gestao-projetos-2.0
```

### 2. **Configuração do Ambiente**
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements_producao.txt

# Configurar .env (copie de env_example.txt)
cp env_example.txt .env
# Preencha com suas credenciais do Supabase
```

### 3. **Criar Branch para Feature**
```bash
git checkout -b feature/nome-da-sua-feature
# ou
git checkout -b fix/nome-do-bug-corrigido
```

## 📋 Tipos de Contribuição

### 🐛 **Reportar Bugs**
- Use o template de issue para bugs
- Inclua passos para reproduzir
- Adicione screenshots se relevante
- Especifique versão e ambiente

### ✨ **Sugerir Features**
- Descreva o problema que a feature resolve
- Explique a solução proposta
- Considere alternativas
- Adicione mockups se aplicável

### 🔧 **Correções de Código**
- Siga o padrão de código existente
- Adicione comentários quando necessário
- Teste suas alterações
- Atualize documentação se relevante

## 🎯 Áreas Prioritárias

### **Frontend/UX**
- Melhorias na interface responsiva
- Otimizações de performance
- Acessibilidade (WCAG)
- Novos componentes reutilizáveis

### **Backend/API**
- Otimizações de consultas SQL
- Implementação de cache
- API REST endpoints
- Testes automatizados

### **DevOps/Deploy**
- CI/CD com GitHub Actions
- Monitoramento e logs
- Backup strategies
- Security improvements

### **Documentação**
- Guias de usuário
- Documentação técnica
- Tutoriais em vídeo
- Exemplos de código

## 📝 Padrões de Código

### **Python/Flask**
```python
# Use type hints
def criar_projeto(nome: str, descricao: str) -> dict:
    """
    Cria um novo projeto no sistema.
    
    Args:
        nome: Nome do projeto
        descricao: Descrição do projeto
        
    Returns:
        dict: Dados do projeto criado
    """
    pass

# Siga PEP 8
# Use docstrings
# Nomeação em português para business logic
# Nomeação em inglês para código técnico
```

### **JavaScript**
```javascript
// Use ES6+
// Comentários em português
// Funções puras quando possível
// Event listeners organizados

function atualizarGantt(projetos) {
    // Lógica clara e comentada
}
```

### **HTML/CSS**
```html
<!-- Semantic HTML -->
<!-- Classes BEM quando apropriado -->
<!-- Mobile-first responsive -->
```

## 🧪 Testes

### **Executar Testes**
```bash
# Testes unitários
python -m pytest tests/

# Testes de integração
python test_producao.py

# Testes manuais
python testar_excel_direto.py
```

### **Escrever Testes**
- Teste casos de sucesso e erro
- Mock integrações externas
- Use fixtures para dados de teste
- Nomeação descritiva dos testes

## 📤 Processo de Pull Request

### **Antes de Abrir PR**
- [ ] Código testado localmente
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Commit messages descritivos
- [ ] Branch atualizada com main

### **Template de PR**
```markdown
## Descrição
Breve descrição das mudanças

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
Passos para testar as mudanças

## Checklist
- [ ] Código testado
- [ ] Documentação atualizada
- [ ] Testes passando
```

## 🎨 UI/UX Guidelines

### **Design System**
- Cores consistentes com tema atual
- Espaçamentos múltiplos de 8px
- Tipografia hierárquica clara
- Ícones da mesma família

### **Responsive Design**
```css
/* Mobile First */
.component {
    /* Mobile styles */
}

@media (min-width: 768px) {
    /* Tablet styles */
}

@media (min-width: 1024px) {
    /* Desktop styles */
}
```

### **Acessibilidade**
- Contrast ratio mínimo 4.5:1
- Navegação por teclado
- Screen reader friendly
- Focus indicators visíveis

## 🚀 Deploy e Release

### **Versionamento**
- Seguir [Semantic Versioning](https://semver.org/)
- MAJOR.MINOR.PATCH
- Tags no formato v2.1.0

### **Release Process**
1. Atualizar CHANGELOG.md
2. Criar PR para main
3. Merge após review
4. Criar tag de release
5. Deploy automático

## 🤝 Comunidade

### **Comunicação**
- Issues para discussões técnicas
- Discussions para ideias gerais
- Email para questões privadas

### **Code of Conduct**
- Seja respeitoso e inclusivo
- Aceite feedback construtivo
- Ajude outros desenvolvedores
- Mantenha discussões focadas no projeto

## 📚 Recursos Úteis

### **Documentação**
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Supabase Docs](https://supabase.com/docs)
- [Frappe Gantt](https://frappe.io/gantt)

### **Ferramentas**
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Obrigado por contribuir! 🎉**

Toda contribuição, não importa quão pequena, é valiosa para o projeto.