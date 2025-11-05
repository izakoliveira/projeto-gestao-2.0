#!/usr/bin/env python3
"""
Script para criar executável do instalador
Gera um arquivo .exe que permite instalar o sistema sem precisar de VSCode ou terminal
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def verificar_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        print("✅ PyInstaller já está instalado")
        return True
    except ImportError:
        print("⚠️ PyInstaller não encontrado")
        return False

def instalar_pyinstaller():
    """Instala PyInstaller"""
    print("📦 Instalando PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller instalado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao instalar PyInstaller: {e}")
        return False

def preparar_arquivos_projeto():
    """Prepara os arquivos do projeto para serem embarcados no executável"""
    print("\n📁 Preparando arquivos do projeto...")
    
    pasta_origem = Path(__file__).parent
    pasta_projeto = pasta_origem / "projeto_arquivos"
    
    # Criar pasta se não existir
    pasta_projeto.mkdir(exist_ok=True)
    
    # Lista de arquivos e pastas essenciais
    items_essenciais = [
        'app_producao.py',
        'requirements.txt',
        'supabase_client.py',  # Funções do Supabase
        'config/',
        'routes/',
        'templates/',
        'static/',
        'utils/',
        'gunicorn.conf.py',
        'restricoes.json'
    ]
    
    # Copiar arquivos essenciais
    for item in items_essenciais:
        origem = pasta_origem / item
        destino = pasta_projeto / item
        
        if origem.exists():
            try:
                if origem.is_file():
                    shutil.copy2(origem, destino)
                    print(f"  ✓ Copiado: {item}")
                else:
                    # Remover pasta destino se existir
                    if destino.exists():
                        shutil.rmtree(destino)
                    shutil.copytree(origem, destino)
                    print(f"  ✓ Copiada pasta: {item}")
            except Exception as e:
                print(f"  ⚠️ Erro ao copiar {item}: {e}")
        else:
            print(f"  ⚠️ Item não encontrado: {item}")
    
    print("✅ Arquivos preparados!")
    return True

def criar_spec_file():
    """Cria o arquivo .spec para PyInstaller"""
    print("\n📝 Criando arquivo de configuração (.spec)...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['instalador_sistema.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('projeto_arquivos', 'projeto_arquivos'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'webbrowser',
        'urllib.request',
        'zipfile',
        'tempfile',
        'pathlib',
        'subprocess',
        'shutil',
        'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Instalador_Sistema_Gestao',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Janela gráfica (sem console)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='sgp_icon.ico',  # Ícone do SGP
)
"""
    
    spec_file = Path(__file__).parent / "Instalador_Sistema_Gestao.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ Arquivo .spec criado: {spec_file}")
    return spec_file

def compilar_executavel(spec_file):
    """Compila o executável usando PyInstaller"""
    print("\n🔨 Compilando executável...")
    print("⏳ Isso pode levar alguns minutos...")
    
    try:
        # Executar PyInstaller
        cmd = ["pyinstaller", "--clean", str(spec_file)]
        print(f"Executando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("\n✅ Compilação concluída com sucesso!")
        print("\n📦 Executável criado em: dist/Instalador_Sistema_Gestao.exe")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro durante a compilação:")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

def criar_launcher_sistema():
    """Cria um launcher simples para iniciar o sistema após instalação"""
    print("\n🚀 Criando launcher do sistema...")
    
    launcher_code = '''#!/usr/bin/env python3
"""
Launcher do Sistema de Gestão de Projetos 2.0
Inicia o sistema automaticamente abrindo o navegador
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def iniciar_sistema():
    """Inicia o servidor Flask e abre o navegador"""
    print("=" * 50)
    print("  SGP - Sistema de Gestão de Projetos 2.0")
    print("=" * 50)
    print()
    print("🚀 Iniciando sistema...")
    
    # Determinar a pasta do sistema
    if hasattr(sys, '_MEIPASS'):
        # Executando como executável
        pasta_sistema = Path(sys._MEIPASS).parent
    else:
        # Executando como script
        pasta_sistema = Path(__file__).parent
    
    # Mudar para o diretório do sistema
    os.chdir(pasta_sistema)
    
    # Ativar ambiente virtual
    if os.name == 'nt':  # Windows
        python_exe = pasta_sistema / "venv" / "Scripts" / "python.exe"
        activate_script = pasta_sistema / "venv" / "Scripts" / "activate.bat"
    else:  # Linux/Mac
        python_exe = pasta_sistema / "venv" / "bin" / "python"
        activate_script = pasta_sistema / "venv" / "bin" / "activate"
    
    if not python_exe.exists():
        print("❌ Ambiente virtual não encontrado!")
        print(f"Procurado em: {python_exe}")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    # Iniciar o servidor Flask
    app_file = pasta_sistema / "app_producao.py"
    
    if not app_file.exists():
        print("❌ Arquivo app_producao.py não encontrado!")
        print(f"Procurado em: {app_file}")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    print("✅ Ambiente virtual encontrado")
    print("✅ Arquivo principal encontrado")
    print()
    print("🌐 Iniciando servidor...")
    print("📍 URL: http://localhost:5000")
    print()
    print("⚠️  Para parar o servidor, pressione Ctrl+C")
    print()
    
    # Aguardar 2 segundos antes de abrir o navegador
    time.sleep(2)
    
    # Abrir navegador
    try:
        webbrowser.open("http://localhost:5000")
        print("✅ Navegador aberto!")
    except Exception as e:
        print(f"⚠️  Não foi possível abrir o navegador automaticamente: {e}")
        print("📍 Abra manualmente: http://localhost:5000")
    
    print()
    
    # Iniciar o servidor
    try:
        subprocess.run([str(python_exe), str(app_file)], check=True)
    except KeyboardInterrupt:
        print()
        print("🛑 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar o sistema: {e}")
        input("Pressione Enter para sair...")
        sys.exit(1)

if __name__ == "__main__":
    iniciar_sistema()
'''
    
    launcher_file = Path(__file__).parent / "launcher_sistema.py"
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print(f"✅ Launcher criado: {launcher_file}")
    
    # Criar .spec para o launcher
    launcher_spec = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher_sistema.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['webbrowser', 'subprocess'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Sistema_Gestao_Projetos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mostrar console para logs
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='sgp_icon.ico',
)
"""
    
    spec_launcher = Path(__file__).parent / "Launcher_Sistema.spec"
    with open(spec_launcher, 'w', encoding='utf-8') as f:
        f.write(launcher_spec)
    
    print(f"✅ Spec do launcher criado: {spec_launcher}")
    return launcher_file, spec_launcher

def compilar_launcher(spec_file):
    """Compila o launcher"""
    print("\n🔨 Compilando launcher...")
    
    try:
        cmd = ["pyinstaller", "--clean", str(spec_file)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Launcher compilado: dist/Sistema_Gestao_Projetos.exe")
        return True
    except Exception as e:
        print(f"❌ Erro ao compilar launcher: {e}")
        return False

def atualizar_instalador_com_launcher():
    """Atualiza o instalador para incluir o launcher"""
    print("\n📝 Atualizando instalador para incluir o launcher...")
    
    instalador_file = Path(__file__).parent / "instalador_sistema.py"
    
    # Ler o instalador atual
    with open(instalador_file, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Verificar se já tem a função de criar launcher
    if "def criar_launcher_executavel" not in conteudo:
        # Adicionar função para copiar o launcher
        funcao_launcher = '''
    def criar_launcher_executavel(self, destino):
        """Copia o executável launcher para a pasta de instalação"""
        self.log_message("🚀 Copiando launcher do sistema...")
        
        try:
            # Procurar o launcher
            launcher_origem = None
            
            # Opção 1: Launcher embarcado no instalador
            if hasattr(sys, '_MEIPASS'):
                launcher_origem = Path(sys._MEIPASS) / "Sistema_Gestao_Projetos.exe"
            
            # Opção 2: Launcher na pasta dist
            if not launcher_origem or not launcher_origem.exists():
                launcher_origem = Path(__file__).parent / "dist" / "Sistema_Gestao_Projetos.exe"
            
            # Opção 3: Launcher na pasta raiz
            if not launcher_origem or not launcher_origem.exists():
                launcher_origem = Path(__file__).parent / "Sistema_Gestao_Projetos.exe"
            
            if launcher_origem and launcher_origem.exists():
                launcher_destino = destino / "Sistema_Gestao_Projetos.exe"
                shutil.copy2(launcher_origem, launcher_destino)
                self.log_message(f"  ✓ Launcher copiado para: {launcher_destino}")
                
                # Atualizar scripts para usar o launcher
                self._atualizar_scripts_com_launcher(destino)
                return True
            else:
                self.log_message("  ⚠️ Launcher não encontrado, usando scripts .bat")
                return False
                
        except Exception as e:
            self.log_message(f"  ⚠️ Erro ao copiar launcher: {str(e)}")
            return False
    
    def _atualizar_scripts_com_launcher(self, destino):
        """Atualiza os scripts .bat para usar o launcher"""
        try:
            # Script simplificado que apenas executa o launcher
            bat_content = f"""@echo off
cd /d "{destino}"
Sistema_Gestao_Projetos.exe
"""
            
            bat_file = destino / "executar_sistema.bat"
            with open(bat_file, "w", encoding="utf-8") as f:
                f.write(bat_content)
            
            self.log_message("  ✓ Scripts atualizados para usar launcher")
            
        except Exception as e:
            self.log_message(f"  ⚠️ Erro ao atualizar scripts: {str(e)}")
'''
        
        # Adicionar a função antes do método main
        conteudo = conteudo.replace(
            "def main():",
            funcao_launcher + "\ndef main():"
        )
        
        # Adicionar chamada no método executar_instalacao
        if "self.criar_launcher_executavel(pasta_destino)" not in conteudo:
            conteudo = conteudo.replace(
                "# Criar scripts de execução",
                "# Criar launcher executável\n            self.criar_launcher_executavel(pasta_destino)\n            \n            # Criar scripts de execução"
            )
        
        # Salvar instalador atualizado
        with open(instalador_file, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("✅ Instalador atualizado!")
    else:
        print("✅ Instalador já possui suporte ao launcher")

def criar_readme_instalacao():
    """Cria um README com instruções de instalação"""
    print("\n📄 Criando README de instalação...")
    
    readme_content = """# 🚀 Instalação do Sistema de Gestão de Projetos 2.0

## 📋 Pré-requisitos

Antes de instalar o sistema, certifique-se de ter:

- **Windows 10 ou superior**
- **Python 3.8 ou superior** instalado
  - Baixe em: https://www.python.org/downloads/
  - ⚠️ **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação
- **Conexão com a internet** (apenas para a instalação inicial)

## 🎯 Como Instalar

### Método 1: Instalador Automático (Recomendado)

1. **Execute o instalador**:
   - Duplo-clique em `Instalador_Sistema_Gestao.exe`
   - Se aparecer um aviso do Windows Defender, clique em "Mais informações" e depois "Executar assim mesmo"

2. **Configure o sistema**:
   - Escolha a pasta onde deseja instalar o sistema
   - Configure as credenciais do Supabase (banco de dados)
   - Marque as opções desejadas (atalho na área de trabalho, etc.)

3. **Aguarde a instalação**:
   - O instalador irá:
     - Extrair os arquivos do sistema
     - Criar um ambiente virtual Python
     - Instalar todas as dependências
     - Configurar o banco de dados
     - Criar atalhos e scripts de execução

4. **Pronto!**
   - Após a instalação, você pode iniciar o sistema de 3 formas:
     - Duplo-clique no atalho da área de trabalho
     - Execute `Sistema_Gestao_Projetos.exe` na pasta de instalação
     - Execute `executar_sistema.bat` na pasta de instalação

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
venv\\Scripts\\activate
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
"""
    
    readme_file = Path(__file__).parent / "INSTALACAO.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ README criado: {readme_file}")

def main():
    """Função principal"""
    print("=" * 60)
    print("  CRIADOR DE EXECUTÁVEL - Sistema de Gestão de Projetos 2.0")
    print("=" * 60)
    print()
    
    # 1. Verificar e instalar PyInstaller
    if not verificar_pyinstaller():
        if not instalar_pyinstaller():
            print("\n❌ Não foi possível instalar PyInstaller")
            print("Execute manualmente: pip install pyinstaller")
            return
    
    # 2. Preparar arquivos do projeto
    if not preparar_arquivos_projeto():
        print("\n❌ Erro ao preparar arquivos")
        return
    
    # 3. Criar launcher do sistema
    launcher_file, launcher_spec = criar_launcher_sistema()
    
    # 4. Compilar o launcher
    print("\n" + "=" * 60)
    print("  COMPILANDO LAUNCHER")
    print("=" * 60)
    if not compilar_launcher(launcher_spec):
        print("\n⚠️ Erro ao compilar launcher, mas continuando...")
    
    # 5. Atualizar instalador para incluir launcher
    atualizar_instalador_com_launcher()
    
    # 6. Criar arquivo .spec do instalador
    spec_file = criar_spec_file()
    
    # 7. Compilar executável do instalador
    print("\n" + "=" * 60)
    print("  COMPILANDO INSTALADOR")
    print("=" * 60)
    if not compilar_executavel(spec_file):
        print("\n❌ Erro ao compilar instalador")
        return
    
    # 8. Criar README
    criar_readme_instalacao()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("  ✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("📦 Arquivos criados:")
    print("  - dist/Instalador_Sistema_Gestao.exe (instalador)")
    print("  - dist/Sistema_Gestao_Projetos.exe (launcher)")
    print("  - INSTALACAO.md (instruções)")
    print()
    print("🚀 Próximos passos:")
    print("  1. Teste o instalador: dist/Instalador_Sistema_Gestao.exe")
    print("  2. Distribua o instalador para seus usuários")
    print("  3. Leia INSTALACAO.md para instruções detalhadas")
    print()
    print("💡 Dica: Você pode criar um ícone personalizado editando os arquivos .spec")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPressione Enter para sair...")
