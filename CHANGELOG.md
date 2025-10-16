# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-10-16

### ✨ Adicionado
- **Sistema completo de gestão de projetos** com interface web Flask
- **Gráfico de Gantt interativo** com visualização desktop e mobile
- **Exportação para Excel** com múltiplas abas (Dados + Gantt por projeto)
- **Coluna Responsável** nas abas Excel do Gantt
- **Relatórios em PDF** com formatação profissional
- **Sistema de notificações por email** automáticas
- **Interface responsiva** otimizada para mobile e desktop
- **Sistema de autenticação** completo com controle de acesso
- **Gestão de dependências** entre tarefas
- **Filtros avançados** por status, coleção e datas
- **Duplicação de projetos** com templates
- **PWA (Progressive Web App)** configurado

### 🔧 Corrigido
- **Foreign key constraints** na exclusão de projetos
- **Alinhamento da legenda de cores** com a ordem dos projetos
- **Barras do Gantt** não ultrapassando visualmente as datas finais
- **Números centralizados** nos relatórios (colunas de datas e dias)
- **Bloqueio de planilhas** removido para permitir edição completa

### 🚀 Deploy
- **Configuração Docker** completa
- **Deploy automático** para Render.com
- **Scripts de VPS** para deploy manual
- **Nginx configuration** para produção
- **Guias de deploy** detalhados

### 📚 Documentação
- **README.md** completo com badges e instruções
- **Documentação técnica** detalhada
- **Guias de correções** implementadas
- **Changelog** estruturado
- **Licença MIT** incluída

## [Em Desenvolvimento]

### 🎯 Próximas Funcionalidades Planejadas
- [ ] **API REST** completa para integração externa
- [ ] **Dashboard analytics** com métricas avançadas
- [ ] **Sistema de comentários** nas tarefas
- [ ] **Anexos de arquivos** nas tarefas e projetos
- [ ] **Integração com calendários** externos (Google, Outlook)
- [ ] **Sistema de backup** automático
- [ ] **Temas customizáveis** da interface
- [ ] **Relatórios personalizáveis** com templates
- [ ] **Webhooks** para integrações externas
- [ ] **Multiplataforma mobile** (React Native/Flutter)

### 🔧 Melhorias Técnicas Planejadas
- [ ] **GitHub Actions** para CI/CD automático
- [ ] **Testes automatizados** (pytest)
- [ ] **Monitoramento** com logs estruturados
- [ ] **Cache Redis** para performance
- [ ] **Websockets** para atualizações em tempo real
- [ ] **Containerização** otimizada
- [ ] **Documentação API** com Swagger/OpenAPI
- [ ] **Performance profiling** e otimizações
- [ ] **Security audit** completo
- [ ] **Backup strategies** implementadas

---

## Versões Anteriores

### [1.x.x] - Desenvolvimento Inicial
- Desenvolvimento iterativo com correções pontuais
- Base do sistema Flask implementada
- Integração inicial com Supabase
- Templates básicos criados