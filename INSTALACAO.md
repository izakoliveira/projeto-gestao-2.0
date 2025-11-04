# 🚀 Instalação do Sistema de Gestão de Projetos 2.0

## ✨ Novidade: Credenciais Pré-Configuradas!

🎉 **Atenção:** Este instalador já vem com as credenciais do Supabase pré-configuradas!  
Você não precisa mais copiar e colar URLs e chaves - tudo já está pronto para uso.

📖 Para mais detalhes, consulte: [CREDENCIAIS_PRE_CONFIGURADAS.md](CREDENCIAIS_PRE_CONFIGURADAS.md)

---

## 📋 Pré-requisitos

Antes de instalar o sistema, certifique-se de ter:

- **Windows 10 ou superior**
- **Python 3.8 ou superior** instalado
  - Baixe em: https://www.python.org/downloads/
  - ⚠️ **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação
  - 💡 **OU** deixe o instalador instalar o Python Embedded automaticamente
- **Conexão com a internet** (apenas para a instalação inicial)

## 🎯 Como Instalar

### Método 1: Instalador Automático (Recomendado)

1. **Execute o instalador**:
   - Duplo-clique em `Instalador_Sistema_Gestao.exe`
   - Se aparecer um aviso do Windows Defender, clique em "Mais informações" e depois "Executar assim mesmo"

2. **Configure o sistema**:
   - **Aba "Configuração":**
     - Escolha a pasta onde deseja instalar o sistema (padrão: `C:\Users\SeuUsuário\SistemaGestao`)
     - Marque se deseja criar atalho na área de trabalho
     - Marque se deseja instalar Python Embedded (caso não tenha Python instalado)
   
   - **Aba "Banco de Dados":**
     - ✅ **Nada a fazer!** As credenciais já estão pré-configuradas
     - Os campos aparecerão preenchidos e bloqueados (somente leitura)
   
   - **Aba "Instalação":**
     - Clique em "Instalar Sistema" e aguarde

3. **Aguarde a instalação**:
   - O instalador irá:
     - Verificar se Python está instalado (ou instalar Python Embedded)
     - Extrair os arquivos do sistema
     - Criar um ambiente virtual Python
     - Instalar todas as dependências
     - Configurar o banco de dados com as credenciais pré-configuradas
     - Criar atalhos e scripts de execução

4. **Pronto!**
   - Após a instalação, você pode iniciar o sistema de 4 formas:
     - Duplo-clique no atalho da área de trabalho
     - Execute `Sistema_Gestao_Projetos.exe` na pasta de instalação
     - Execute `executar_sistema.bat` na pasta de instalação
     - Execute `iniciar_oculto.vbs` para rodar em segundo plano (recomendado)

### Método 2: Instalação Manual (Avançado)

Se preferir instalar manualmente:

```bash
# 1. Clone ou baixe o repositório
git clone https://github.com/seu-usuario/sistema-gestao-projetos-2.0.git
cd sistema-gestao-projetos-2.0

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure o arquivo .env
# Copie o arquivo env_example.txt para .env e configure suas variáveis

# 6. Execute o sistema
python app_producao.py
```

## 🌐 Acessando o Sistema

Após iniciar o sistema:

1. O navegador deve abrir automaticamente em: `http://localhost:5000`
2. Se não abrir, acesse manualmente esse endereço
3. Faça login com suas credenciais configuradas

## 🛠️ Configuração do Supabase

Para usar o sistema, você precisa configurar um banco de dados Supabase:

1. **Acesse** https://supabase.com e crie uma conta
2. **Crie um novo projeto**
3. **Obtenha as credenciais**:
   - Vá em Settings > API
   - Copie a URL do projeto
   - Copie a chave `anon/public`
4. **Configure no instalador** ou no arquivo `.env`

## 📂 Estrutura de Pastas

Após a instalação:

```
SistemaGestao/
├── app_producao.py              # Aplicação principal
├── Sistema_Gestao_Projetos.exe  # Launcher (inicia o sistema)
├── executar_sistema.bat         # Script alternativo
├── venv/                        # Ambiente virtual Python
├── static/                      # Arquivos CSS, JS, imagens
├── templates/                   # Templates HTML
├── config/                      # Arquivos de configuração
├── routes/                      # Rotas da aplicação
├── utils/                       # Utilitários
└── .env                        # Variáveis de ambiente
```

## ❗ Solução de Problemas

### Erro: "Python não encontrado"
- Instale Python de python.org
- Certifique-se de marcar "Add Python to PATH" durante a instalação
- Reinicie o computador após instalar o Python

### Erro: "Porta 5000 em uso"
- Feche outros programas que possam estar usando a porta 5000
- Ou edite `app_producao.py` e altere a porta

### Erro: "ModuleNotFoundError"
- Execute: `pip install -r requirements.txt` na pasta do sistema
- Certifique-se de estar com o ambiente virtual ativado

### Sistema não abre no navegador
- Abra manualmente: http://localhost:5000
- Verifique se o servidor iniciou corretamente no console

### Erro de banco de dados
- Verifique se as credenciais do Supabase estão corretas no arquivo `.env`
- Teste a conexão no site do Supabase

## 🔄 Atualizações

Para atualizar o sistema:

1. Execute o instalador novamente
2. Escolha a mesma pasta de instalação
3. O instalador irá atualizar os arquivos

## 📞 Suporte

- **Issues**: Abra uma issue no GitHub
- **Documentação**: Consulte o README.md principal
- **Email**: Seu email de suporte

## 📄 Licença

Este sistema é distribuído sob [sua licença].

---

**Versão**: 2.0  
**Última atualização**: Novembro 2025
