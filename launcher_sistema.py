#!/usr/bin/env python3
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
    print("  Sistema de Gestão de Projetos 2.0")
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
