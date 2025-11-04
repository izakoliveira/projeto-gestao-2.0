# Instalador do Sistema de Gestão de Projetos 2.0

## 📋 Sobre o Instalador

Este executável foi criado para facilitar a instalação do Sistema de Gestão de Projetos 2.0 em qualquer máquina Windows, sem a necessidade de configuração manual do ambiente Python.

## 🚀 Como Usar

### Opção 1: Executável Standalone (Recomendado)
1. Execute o arquivo `INSTALAR.bat` (detecta automaticamente a melhor versão) ou
2. Navegue até a pasta `dist/` e execute `Instalador_Sistema_Gestao_v3.exe`
3. Siga as instruções na interface gráfica

> **💡 Dica**: A versão v3.0 inclui todos os arquivos embarcados e funciona 100% offline!

### Opção 2: Script Python (para desenvolvedores)
1. Execute o script `instalador_sistema.py` diretamente
2. Certifique-se de ter Python 3.8+ instalado

## 🛠️ O que o Instalador Faz

O instalador automaticamente:

1. **Extrai Arquivos do Sistema** ⭐ NOVO
   - Extrai arquivos embarcados no executável (v3.0)
   - Fallback: baixa do GitHub se necessário
   - Fallback: usa arquivos locais como última opção

2. **Verifica Dependências**
   - Verifica se Python está instalado
   - Verifica se pip está disponível
   - Instala dependências se necessário

3. **Instala Dependências Python**
   - Cria ambiente virtual isolado
   - Instala todas as bibliotecas necessárias do `requirements.txt`
   - Flask, SQLAlchemy, Pandas, e outras dependências

4. **Configuração do Ambiente**
   - Cria arquivo `.env` com configurações personalizadas
   - Configura variáveis de ambiente necessárias
   - Permite configurar Supabase, email, etc.

5. **Criação de Scripts**
   - Cria scripts de execução para Windows e Linux
   - Cria atalhos na área de trabalho (opcional)
   - Configura ambiente de produção

6. **Inicialização do Sistema**
   - Oferece opção para iniciar o sistema imediatamente
   - Configura o servidor local na porta 5000

### 🎯 **Versões Disponíveis:**

| Versão | Tamanho | Características | Recomendação |
|--------|---------|----------------|--------------|
| **v3.0** | ~11MB | Arquivos embarcados, 100% offline | ⭐ **Recomendado** |
| v2.0 | ~10MB | Download do GitHub + fallback local | Alternativa |
| v1.0 | ~10MB | Apenas arquivos locais | Legado |

## 📁 Estrutura Criada

Após a instalação, a seguinte estrutura será criada:

```
sistema-gestao-projetos/
├── app_producao.py          # Aplicação principal
├── requirements.txt         # Dependências Python
├── .env                    # Configurações de ambiente
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── templates/              # Templates HTML
├── migrations/             # Scripts de migração do banco
└── database.db            # Banco de dados SQLite
```

## 🔧 Configurações Padrão

- **Servidor**: http://localhost:5000
- **Banco de Dados**: SQLite (database.db)
- **Modo**: Produção
- **Debug**: Desabilitado por padrão

## 🌐 Após a Instalação

1. O sistema estará disponível em: `http://localhost:5000`
2. Para parar o servidor: Pressione `Ctrl+C` no terminal
3. Para reiniciar: Execute `python app_producao.py` na pasta do projeto

## 📝 Configurações Personalizadas

Para personalizar as configurações:

1. Edite o arquivo `.env` criado na pasta do projeto
2. Modifique as variáveis conforme necessário:
   ```
   DATABASE_URL=sqlite:///database.db
   SECRET_KEY=sua_chave_secreta_aqui
   FLASK_ENV=production
   ```

## ❗ Solução de Problemas

### Erro: "Python não encontrado"
- Instale Python 3.8+ de python.org
- Certifique-se de adicionar Python ao PATH

### Erro: "Permissões insuficientes"
- Execute o instalador como Administrador
- Verifique permissões da pasta de destino

### Erro: "Porta 5000 em uso"
- Feche outros aplicativos usando a porta 5000
- Ou modifique a porta no arquivo `app_producao.py`

### Banco de dados corrompido
- Delete o arquivo `database.db`
- Execute o sistema novamente (será recriado automaticamente)

## 🔄 Atualizações

Para atualizar o sistema:
1. Baixe a nova versão
2. Execute o instalador novamente
3. Escolha a opção de atualização quando solicitado

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Abra uma issue no repositório do projeto
- Consulte a documentação completa no README.md principal

## 📄 Licença

Este instalador e o sistema são distribuídos sob a mesma licença do projeto principal.

---

**Versão do Instalador**: 1.0  
**Data de Criação**: 21 de outubro de 2025  
**Compatibilidade**: Windows 10/11, Python 3.8+