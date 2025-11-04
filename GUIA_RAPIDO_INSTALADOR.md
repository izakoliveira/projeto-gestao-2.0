# 🚀 Guia Rápido de Uso do Instalador

## Para Usuários Finais

### ✨ Instalação (5 minutos)

1. **Execute:** `Instalador_Sistema_Gestao.exe`

2. **Aba "Configuração":**
   - ✅ Deixe a pasta padrão ou escolha outra
   - ✅ Marque "Criar atalho na área de trabalho"
   - ⚠️ Se não tiver Python instalado, marque "Instalar Python Embedded"

3. **Aba "Banco de Dados":**
   - ✅ **Nada a fazer!** Já está configurado

4. **Aba "Instalação":**
   - ✅ Clique em "Instalar Sistema"
   - ⏳ Aguarde 3-5 minutos

5. **Pronto!**

---

### 🖥️ Como Usar Diariamente

#### **Opção 1: Atalho da Área de Trabalho (Recomendado)**
```
1. Duplo-clique no atalho "Sistema Gestão Projetos"
2. Aguarde alguns segundos
3. Navegador abrirá automaticamente em http://localhost:5000
```

#### **Opção 2: Modo Oculto (Mais Limpo)**
```
1. Vá até: C:\Users\SeuUsuário\SistemaGestao
2. Duplo-clique em: iniciar_oculto.vbs
3. Abra navegador manualmente: http://localhost:5000
4. Sistema fica rodando em segundo plano (sem janelas visíveis)
```

#### **Para Parar o Sistema:**
```
1. Vá até: C:\Users\SeuUsuário\SistemaGestao
2. Duplo-clique em: parar_sistema.bat
```

---

### 🌐 Acessando o Sistema

Após iniciar, abra seu navegador favorito e acesse:

```
http://localhost:5000
```

**Primeiro acesso:**
1. Clique em "Cadastrar"
2. Preencha seus dados
3. Faça login

---

## Para Administradores/TI

### 📦 Distribuição em Lote

#### **Distribuir para Equipe:**
```
1. Compilar: python criar_executavel.py
2. Localizar: dist/Instalador_Sistema_Gestao.exe
3. Copiar para: Rede compartilhada, email, pen drive
4. Enviar instruções aos usuários
```

#### **Instalação Remota:**
```powershell
# Via rede compartilhada
\\servidor\instaladores\Instalador_Sistema_Gestao.exe

# Via linha de comando (se suportado futuramente)
Instalador_Sistema_Gestao.exe /S /D=C:\SistemaGestao
```

---

### 🔧 Modificar Credenciais

#### **Para Novo Instalador:**

**Arquivo:** `instalador_sistema.py` (linhas 28-32)

```python
# Altere aqui:
self.supabase_url = tk.StringVar(value="SUA_URL_AQUI")
self.supabase_key = tk.StringVar(value="SUA_CHAVE_AQUI")
self.admin_email = tk.StringVar(value="SEU_EMAIL_AQUI")
```

Recompilar:
```powershell
python criar_executavel.py
```

#### **Para Sistema Já Instalado:**

**Arquivo:** `C:\Users\SeuUsuário\SistemaGestao\.env`

```env
SUPABASE_URL=https://nova-url.supabase.co
SUPABASE_KEY=nova_chave_aqui
ADMIN_EMAIL=novo_email@exemplo.com
```

Reiniciar sistema.

---

### 🐛 Solução Rápida de Problemas

#### **Sistema não inicia:**
```powershell
# 1. Verificar se está rodando
tasklist | findstr python

# 2. Parar tudo
cd C:\Users\SeuUsuário\SistemaGestao
parar_sistema.bat

# 3. Iniciar novamente
iniciar_oculto.vbs
```

#### **Porta 5000 ocupada:**
```powershell
# Ver o que está usando a porta
netstat -ano | findstr :5000

# Matar processo (substitua PID pelo número retornado)
taskkill /PID 1234 /F

# Reiniciar sistema
cd C:\Users\SeuUsuário\SistemaGestao
iniciar_oculto.vbs
```

#### **Erro de dependências:**
```powershell
cd C:\Users\SeuUsuário\SistemaGestao
venv\Scripts\activate
pip install -r requirements.txt
```

#### **Reinstalar do zero:**
```
1. Excluir pasta: C:\Users\SeuUsuário\SistemaGestao
2. Executar instalador novamente
```

---

### 📊 Monitoramento

#### **Ver logs do sistema:**
```powershell
cd C:\Users\SeuUsuário\SistemaGestao
type logs\sistema.log
```

#### **Verificar saúde do banco:**
```
Acesse: https://supabase.com/dashboard/project/zvdpuxggltqejplybzet
```

#### **Ver processos Python ativos:**
```powershell
tasklist | findstr python
```

---

### 🔄 Atualizações

#### **Atualizar Sistema:**

**Método 1: Reinstalar (Recomendado)**
```
1. Executar novo instalador
2. Escolher mesma pasta de instalação
3. Sobrescrever arquivos
4. Configurações (.env) são mantidas
```

**Método 2: Manual (Avançado)**
```powershell
cd C:\Users\SeuUsuário\SistemaGestao\projeto
git pull origin main
venv\Scripts\activate
pip install -r requirements.txt
```

---

### 📋 Checklist de Deploy

- [ ] Compilar instalador: `python criar_executavel.py`
- [ ] Testar em máquina limpa (sem Python)
- [ ] Verificar credenciais do Supabase estão corretas
- [ ] Testar instalação e primeira execução
- [ ] Testar login e funcionalidades principais
- [ ] Documentar versão e data do build
- [ ] Criar pasta compartilhada na rede
- [ ] Copiar `Instalador_Sistema_Gestao.exe` para rede
- [ ] Enviar instruções para usuários
- [ ] Agendar suporte para primeiras instalações

---

## 📱 Contatos de Suporte

**Email:** izak.gomes59@gmail.com  
**Sistema:** Sistema de Gestão de Projetos 2.0  
**Versão:** 2.1  
**Última Atualização:** 2025-01-15

---

## 🔗 Links Úteis

- **Documentação Completa:** [RESUMO_MELHORIAS_INSTALADOR.md](RESUMO_MELHORIAS_INSTALADOR.md)
- **Credenciais:** [CREDENCIAIS_PRE_CONFIGURADAS.md](CREDENCIAIS_PRE_CONFIGURADAS.md)
- **Instalação Detalhada:** [INSTALACAO.md](INSTALACAO.md)
- **Supabase Dashboard:** https://supabase.com/dashboard

---

## 💡 Dicas Pro

### Para Usuários:

💡 **Use o modo oculto:** Sistema fica invisível no background  
💡 **Adicione aos favoritos:** http://localhost:5000  
💡 **Ctrl+F5:** Atualiza página limpando cache  

### Para Administradores:

💡 **Compile em VM limpa:** Garante compatibilidade máxima  
💡 **Versione os instaladores:** Ex: `Instalador_v2.1_20250115.exe`  
💡 **Teste em Windows 10 e 11:** Compatibilidade  
💡 **Use rede local:** Deploy mais rápido que email  

---

**📌 Lembre-se:** Este instalador já vem com tudo pré-configurado.  
Usuários só precisam clicar e usar! 🎉
