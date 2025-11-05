# 🔄 Converter Usuário Simples em Usuário Completo

## 📋 Visão Geral

Agora é possível **converter usuários simples** (sem login) em **usuários completos** (com email e senha para acessar o sistema).

---

## 🎯 O Que Foi Implementado?

### **Antes:**
```
Usuário Simples
├── Nome: "João Silva"
├── Email: usuario_simples_1730000000@sistema.local (placeholder)
├── Senha: USUARIO_SIMPLES_SEM_LOGIN (placeholder)
└── ❌ Não pode fazer login
```

### **Depois:**
```
Usuário Completo
├── Nome: "João Silva"
├── Email: joao.silva@empresa.com (real)
├── Senha: ******** (criptografada com bcrypt)
└── ✅ Pode fazer login no sistema
```

---

## 🚀 Como Usar

### **1. Acessar Página de Gerenciamento**
```
1. Faça login como administrador
2. Vá para: Dashboard → Admin → Usuários Simples
3. URL: /admin/usuarios_simples
```

### **2. Localizar Usuário Simples**
```
Na tabela, procure o usuário que deseja converter.
Identificação: Badge "Usuário Simples" (verde)
```

### **3. Clicar no Botão de Email**
```
📧 Botão azul com ícone de envelope
```

### **4. Preencher Formulário**
```
┌─────────────────────────────────────┐
│  Adicionar Email e Senha            │
├─────────────────────────────────────┤
│  Email: joao@empresa.com            │
│  Senha: ••••••                      │
│  Confirmar Senha: ••••••            │
│                                     │
│  [Cancelar]  [Converter Usuário]   │
└─────────────────────────────────────┘
```

### **5. Confirmar Conversão**
```
✅ Usuário convertido com sucesso!
✅ Agora pode fazer login com o email fornecido
```

---

## 🔒 Segurança

### **Criptografia de Senha**
```python
import bcrypt

# Senha digitada pelo admin
senha = "senha123"

# Hash gerado com bcrypt (salt automático)
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
# Resultado: $2b$12$randomsalt...hashvalue...

# Armazenado no banco de dados
UPDATE usuarios SET senha_hash = '$2b$12$...' WHERE id = usuario_id
```

### **Características do bcrypt:**
- ✅ **Salt automático** - Cada hash é único
- ✅ **Custo adaptável** - Proteção contra força bruta
- ✅ **Impossível reverter** - Não há como recuperar a senha original
- ✅ **Padrão da indústria** - Usado por milhões de aplicações

---

## ✅ Validações Implementadas

### **1. Email**
```python
# Verifica se email já está em uso
email_check = supabase.table("usuarios").select("id").eq("email", email).execute()
if email_check.data:
    flash('Este email já está em uso por outro usuário.')
```

### **2. Senha**
```python
# Mínimo 6 caracteres
if len(senha) < 6:
    flash('A senha deve ter no mínimo 6 caracteres.')

# Confirmação de senha
if senha != confirmar_senha:
    flash('As senhas não coincidem.')
```

### **3. Campos Obrigatórios**
```python
if not email or not senha:
    flash('Email e senha são obrigatórios.')
```

---

## 🔄 Processo de Conversão

### **Passo a Passo Técnico:**

```python
# 1. Validar dados
if senha != confirmar_senha:
    return error

# 2. Verificar email disponível
email_exists = check_email_in_database(email)
if email_exists:
    return error

# 3. Gerar hash da senha
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

# 4. Atualizar banco de dados
UPDATE usuarios SET 
    email = 'joao@empresa.com',
    senha_hash = '$2b$12$...'
WHERE id = usuario_id

# 5. Remover restrições
# Usuário completo tem acesso total por padrão
restricoes = carregar_restricoes()
del restricoes[usuario_id]
salvar_restricoes(restricoes)
```

---

## 📊 Diferenças entre Tipos de Usuário

| Característica | Usuário Simples | Usuário Completo |
|----------------|-----------------|------------------|
| **Nome** | ✅ Sim | ✅ Sim |
| **Email Real** | ❌ Placeholder | ✅ Real |
| **Senha** | ❌ Placeholder | ✅ Criptografada |
| **Fazer Login** | ❌ Não | ✅ Sim |
| **Criar Projetos** | ❌ Não | ✅ Sim |
| **Editar Tarefas** | ❌ Não | ✅ Sim |
| **Ver Dashboards** | ❌ Não | ✅ Sim |
| **Receber Emails** | ❌ Não | ✅ Sim |
| **Responsável por Tarefas** | ✅ Sim | ✅ Sim |

---

## 🎨 Interface Visual

### **Tabela de Usuários:**

```
┌──────────────────────────────────────────────────────────────┐
│ Nome              │ Tipo                │ Ações              │
├──────────────────────────────────────────────────────────────┤
│ João Silva        │ [Usuário Simples]   │ [📧] [🗑️]         │
│ Maria Santos      │ [Usuário com Email] │      [🗑️]         │
│ Pedro Costa       │ [Usuário Simples]   │ [📧] [🗑️]         │
└──────────────────────────────────────────────────────────────┘

Legenda:
📧 = Adicionar Email/Senha (converte para usuário completo)
🗑️ = Excluir usuário
```

### **Modal de Conversão:**

```
╔═════════════════════════════════════════╗
║  🔄 Adicionar Email e Senha             ║
╠═════════════════════════════════════════╣
║                                         ║
║  ℹ️ Converter o usuário João Silva     ║
║     em usuário completo com acesso      ║
║     ao sistema.                         ║
║                                         ║
║  Email:                                 ║
║  ┌──────────────────────────────────┐  ║
║  │ joao@empresa.com                 │  ║
║  └──────────────────────────────────┘  ║
║  Este será o email de login             ║
║                                         ║
║  Senha:                                 ║
║  ┌──────────────────────────────────┐  ║
║  │ ••••••••                         │  ║
║  └──────────────────────────────────┘  ║
║  Mínimo 6 caracteres                    ║
║                                         ║
║  Confirmar Senha:                       ║
║  ┌──────────────────────────────────┐  ║
║  │ ••••••••                         │  ║
║  └──────────────────────────────────┘  ║
║                                         ║
║  [ Cancelar ]    [ Converter Usuário ] ║
╚═════════════════════════════════════════╝
```

---

## 💡 Casos de Uso

### **Caso 1: Estagiário Efetivado**
```
Situação: Estagiário era usuário simples, foi efetivado
Ação: Converter para usuário completo
Resultado: Pode acessar sistema, criar projetos, etc.
```

### **Caso 2: Colaborador Externo Promovido**
```
Situação: Freelancer virou funcionário fixo
Ação: Converter para usuário completo
Resultado: Acesso total ao sistema
```

### **Caso 3: Usuário Temporário que Ficou**
```
Situação: Criado como simples "só para ver tarefas"
Ação: Converter para usuário completo
Resultado: Pode fazer login e trabalhar normalmente
```

---

## 🔧 Código Relevante

### **Arquivo:** `projeto_arquivos/routes/admin.py`

```python
if acao == 'converter':
    usuario_id = request.form.get('usuario_id')
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '')
    confirmar_senha = request.form.get('confirmar_senha', '')
    
    # Validações
    if not email or not senha:
        flash('Email e senha são obrigatórios.')
        return redirect(url_for('admin.gerenciar_usuarios_simples'))
    
    if senha != confirmar_senha:
        flash('As senhas não coincidem.')
        return redirect(url_for('admin.gerenciar_usuarios_simples'))
    
    if len(senha) < 6:
        flash('A senha deve ter no mínimo 6 caracteres.')
        return redirect(url_for('admin.gerenciar_usuarios_simples'))
    
    # Verificar se o email já está em uso
    email_check = supabase.table("usuarios").select("id").eq("email", email).execute()
    if email_check.data:
        flash('Este email já está em uso por outro usuário.')
        return redirect(url_for('admin.gerenciar_usuarios_simples'))
    
    # Converter usuário
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    resp = supabase.table("usuarios").update({
        "email": email,
        "senha_hash": senha_hash
    }).eq("id", usuario_id).execute()
    
    if resp.data:
        # Remover restrições (acesso total)
        restricoes = carregar_restricoes()
        if usuario_id in restricoes:
            del restricoes[usuario_id]
            salvar_restricoes(restricoes)
        
        flash(f'Usuário convertido com sucesso! Agora pode fazer login com o email {email}')
```

### **Arquivo:** `projeto_arquivos/templates/admin_usuarios_simples.html`

```html
<!-- Botão de converter -->
{% if usuario.email.endswith('@sistema.local') %}
<button type="button" class="btn btn-primary btn-sm me-1" 
        data-bs-toggle="modal" 
        data-bs-target="#modalConverter{{ usuario.id }}"
        title="Adicionar email e senha">
    <i class="fas fa-envelope"></i>
</button>
{% endif %}

<!-- Modal de conversão -->
<div class="modal fade" id="modalConverter{{ usuario.id }}">
    <!-- ... formulário ... -->
</div>
```

---

## 📝 Dependências Adicionadas

### **requirements.txt:**
```txt
bcrypt==4.2.1
```

### **Instalação:**
```bash
pip install bcrypt==4.2.1
```

---

## ⚠️ Avisos Importantes

### **1. Não Há Reversão**
```
⚠️ Após converter, NÃO É POSSÍVEL reverter para usuário simples
   O usuário terá email e senha permanentemente
```

### **2. Email Único**
```
⚠️ Cada email só pode ser usado por um usuário
   Verifique se o email está disponível antes
```

### **3. Senha Inicial**
```
ℹ️ O administrador define a senha inicial
   O usuário pode alterá-la após fazer login
```

### **4. Restrições Removidas**
```
ℹ️ Ao converter, todas as restrições são removidas
   Usuário completo tem acesso total por padrão
   Configure restrições manualmente se necessário
```

---

## 🧪 Testando a Funcionalidade

### **Teste 1: Conversão Básica**
```
1. Criar usuário simples "Teste Conversão"
2. Clicar no botão de email (📧)
3. Preencher:
   - Email: teste@conversao.com
   - Senha: senha123
   - Confirmar: senha123
4. Clicar em "Converter Usuário"
5. ✅ Verificar mensagem de sucesso
6. ✅ Fazer logout e login com novo email
```

### **Teste 2: Email Duplicado**
```
1. Tentar converter com email já existente
2. ❌ Deve mostrar erro: "Email já está em uso"
```

### **Teste 3: Senhas Não Coincidem**
```
1. Preencher senha: senha123
2. Confirmar senha: senha456
3. ❌ Deve mostrar erro: "Senhas não coincidem"
```

### **Teste 4: Senha Curta**
```
1. Preencher senha: 123
2. ❌ Deve mostrar erro: "Mínimo 6 caracteres"
```

---

## 📊 Resumo

| Aspecto | Detalhes |
|---------|----------|
| **Funcionalidade** | Converter usuário simples em completo |
| **Localização** | /admin/usuarios_simples |
| **Permissão** | Apenas administradores |
| **Criptografia** | bcrypt com salt automático |
| **Validações** | Email único, senha ≥6 chars, confirmação |
| **Efeito** | Remove restrições, permite login |
| **Reversível** | ❌ Não |

---

## 🎯 Benefícios

✅ **Flexibilidade** - Comece simples, converta depois  
✅ **Segurança** - Senhas criptografadas com bcrypt  
✅ **Validação** - Múltiplas camadas de verificação  
✅ **UX** - Interface intuitiva com modal  
✅ **Automação** - Remove restrições automaticamente  

---

**Última Atualização:** 2025-11-05  
**Versão:** 1.0  
**Arquivos Modificados:**
- `projeto_arquivos/routes/admin.py`
- `projeto_arquivos/templates/admin_usuarios_simples.html`
- `requirements.txt`
