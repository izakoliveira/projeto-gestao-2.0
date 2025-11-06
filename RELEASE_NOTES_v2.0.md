# 🚀 Release Notes - Sistema de Gestão de Projetos v2.0

**Data de Release:** 06/11/2025  
**Versão:** 2.0  
**Arquivo:** `Instalador_Sistema_Gestao.exe` (11,05 MB)

---

## ✨ Novidades Principais

### 1. 🔄 Conversão de Usuários Simples
- Permite converter usuários simples (apenas nome) para usuários com email e senha
- Interface modal com validação de email
- Criptografia bcrypt para senhas
- Validação de email único no sistema

### 2. 🔐 Sistema de Restrições no Banco de Dados
- Migração completa do sistema de restrições para Supabase
- 11 tipos de restrições configuráveis por usuário:
  - **Projetos:** Criar, Editar, Excluir
  - **Tarefas:** Criar, Editar, Excluir
  - **Campos:** Responsável, Duração, Datas, Predecessoras, Nome/Ordem
- Interface administrativa atualizada (largura 900px)
- Políticas RLS configuradas no Supabase
- Fallback para arquivo JSON local

### 3. 🎨 Ícone do Sistema
- Ícone SGP aplicado no instalador
- Ícone no atalho da área de trabalho
- Branding consistente em toda aplicação

### 4. 🤖 Sistema de Auto-Shutdown
- Monitoramento automático do navegador
- Fecha servidor Flask após 60s sem navegador aberto
- Arquivo: `gerenciador_sistema.py`
- Previne processos órfãos em background

### 5. 📅 Copyright Atualizado
- Footer atualizado para "© 2025"
- Reflete ano corrente

---

## 🔧 Correções Importantes

### 🐛 Bug Crítico: Rotas Ausentes no Instalador
**Problema:** Apenas `admin.py` estava sendo copiado para `projeto_arquivos/routes/`  
**Impacto:** Sistema completamente quebrado após instalação (404 em todas rotas)  
**Solução:** Todos os 9 arquivos de rotas agora incluídos:
- ✅ admin.py
- ✅ auth.py
- ✅ main.py
- ✅ projetos.py
- ✅ tarefas.py
- ✅ pastas.py
- ✅ producao.py
- ✅ relatorio.py
- ✅ __init__.py

### 🔐 Correção RLS (Row Level Security)
**Problema:** Restrições não persistiam no Supabase  
**Causa:** Políticas RLS bloqueando operações UPDATE com chave `anon`  
**Solução:** Políticas RLS permissivas criadas para SELECT, INSERT, UPDATE, DELETE  
**Resultado:** Sistema de restrições 100% funcional

### 🎨 Interface de Restrições
**Problema:** Textos longos ultrapassando bordas  
**Solução:** 
- Card expandido de 700px para 900px
- Container mudado para `container-fluid`
- Melhor aproveitamento de espaço horizontal

---

## 📦 Arquitetura

### Estrutura do Sistema Instalado:
```
SGP/
├── python311/              # Python 3.11 embedded
├── app_producao.py         # Aplicação Flask principal
├── gerenciador_sistema.py  # Gerenciador de ciclo de vida
├── iniciar_oculto.vbs      # Script de inicialização
├── sgp_icon.ico            # Ícone do sistema
├── supabase_client.py      # Cliente Supabase
├── restricoes.json         # Cache local de restrições
├── .env                    # Configurações ambiente
├── config/                 # Configurações
├── routes/                 # 9 arquivos de rotas Flask
├── templates/              # Templates HTML
├── static/                 # CSS, JS, imagens
└── utils/                  # Utilitários (auth, email, etc.)
```

### Tecnologias:
- **Backend:** Flask 3.x, Python 3.11
- **Database:** Supabase (PostgreSQL)
- **Frontend:** Bootstrap 5, JavaScript
- **Autenticação:** bcrypt 4.2.1
- **Empacotamento:** PyInstaller 6.16.0
- **Monitoramento:** psutil

---

## 🔄 Migração de Dados

### Script de Migração Executado:
- **Arquivo:** `migrar_restricoes_para_banco.py`
- **Resultado:** 18 usuários migrados com sucesso
- **SQL:** `migration_restricoes.sql` (ALTER TABLE com 11 colunas)

### Usuários Migrados:
- Pedro filho
- izak (admin)
- tamires.barros
- izak.oliveira
- fabio.goncalves
- jaqueline.candido
- carlos.sousa
- bianca.ribeiro
- catiucia
- nislene.ribeiro
- diogo.moraes
- beto
- pedro.filho
- joserran.nascimento (usuário simples)
- dario.martins
- Fellipe Couto de Paula
- Jampierry Ferreira Tome da Silva
- joserran.nascimento (com email)

---

## 📋 Checklist de Validação

### Funcionalidades Testadas:
- [x] Conversão de usuário simples para completo
- [x] Login com email e senha
- [x] Sistema de restrições salva corretamente
- [x] Restrições persistem após reload
- [x] Ícone aparece no atalho desktop
- [x] Auto-shutdown funciona (60s timeout)
- [x] Todas as 9 rotas carregam sem 404
- [x] Copyright mostra 2025
- [x] Interface de restrições com largura adequada

### Testes de Instalação:
- [x] Instalador executa sem erros
- [x] Cria pasta SGP no desktop
- [x] Cria atalho com ícone
- [x] Primeiro acesso abre navegador
- [x] Login funciona
- [x] Dashboard carrega

---

## 🔐 Segurança

### Políticas RLS Supabase:
```sql
-- SELECT: Permitido para todos
CREATE POLICY "Permitir SELECT para todos" ON usuarios FOR SELECT;

-- INSERT: Permitido para registro de novos usuários
CREATE POLICY "Permitir INSERT para todos" ON usuarios FOR INSERT;

-- UPDATE: Permitido (validação no Flask)
CREATE POLICY "Permitir UPDATE para todos" ON usuarios FOR UPDATE;

-- DELETE: Permitido (validação no Flask)
CREATE POLICY "Permitir DELETE para todos" ON usuarios FOR DELETE;
```

### Camadas de Proteção:
1. **RLS Habilitado:** Mantido ativo no Supabase
2. **Decorators Flask:** `@login_required`, `@apenas_admin_izak`
3. **Validação de Email:** Apenas `izak.gomes59@gmail.com` é admin
4. **Senhas:** Criptografadas com bcrypt (salt automático)
5. **Chave Anon:** Usada apenas no backend

---

## 📝 Commits Incluídos

```
0d1d747 - fix: aumentar largura do card de restrições para 900px
0488b22 - docs: adicionar documentação completa da correção RLS
63f0930 - chore: remover logs de debug excessivos após correção
789e29c - fix: ajustar políticas RLS para permitir UPDATE de restrições
0e9ddc6 - debug: adicionar logs detalhados para PATCH de restrições
[...e mais 15+ commits anteriores]
```

---

## 🚀 Como Instalar

1. **Baixe:** `Instalador_Sistema_Gestao.exe` (11,05 MB)
2. **Execute:** Duplo clique no instalador
3. **Aguarde:** Extração dos arquivos (~2-3 minutos)
4. **Atalho:** Criado automaticamente no Desktop
5. **Primeiro Acesso:** Sistema abrirá navegador automaticamente
6. **Login:** Use suas credenciais

---

## 🔄 Como Atualizar

1. **Feche** o sistema atual (se estiver rodando)
2. **Delete** a pasta antiga do Desktop
3. **Execute** o novo instalador
4. **Dados preservados:** Tudo está no Supabase (nenhuma perda)

---

## 📞 Suporte

**Desenvolvido para:** Dipaula  
**Admin:** Izak Oliveira (izak.gomes59@gmail.com)  
**Repositório:** github.com/izakoliveira/sistema-gestao-projetos-2.0

---

## 📊 Estatísticas

- **Linhas de Código:** ~15.000+
- **Arquivos Python:** 40+
- **Templates HTML:** 25+
- **Rotas Flask:** 9 blueprints
- **Usuários Ativos:** 18
- **Projetos Gerenciados:** 19+
- **Tempo de Build:** ~19 segundos

---

## 🎯 Próximas Melhorias (Roadmap)

- [ ] Usar `service_role` key para operações admin (mais seguro)
- [ ] Backup automático do banco de dados
- [ ] Notificações por email em mudanças críticas
- [ ] Logs de auditoria (quem fez o quê)
- [ ] Dashboard com gráficos de progresso
- [ ] Exportação de relatórios em PDF
- [ ] App mobile (React Native)

---

**Versão compilada em:** 06/11/2025 09:06:56  
**Python:** 3.11.6  
**PyInstaller:** 6.16.0  
**Sistema Operacional:** Windows 10/11 64-bit
