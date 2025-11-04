#!/usr/bin/env python3
"""
Instalador do Sistema de Gestão de Projetos 2.0
Automatiza a instalação e configuração completa do sistema
"""

import os
import sys
import subprocess
import shutil
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
from pathlib import Path
import time
import urllib.request
import zipfile
import tempfile

class InstaladorSistema:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instalador - Sistema de Gestão de Projetos 2.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Arquivo de configurações salvas
        self.config_file = Path.home() / ".sistema_gestao_config.json"
        
        # Variáveis de configuração
        self.pasta_instalacao = tk.StringVar(value=str(Path.home() / "SistemaGestao"))
        
        # Credenciais pré-configuradas do Supabase
        self.supabase_url = tk.StringVar(value="https://zvdpuxggltqejplybzet.supabase.co")
        self.supabase_key = tk.StringVar(value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI")
        self.admin_email = tk.StringVar(value="izak.gomes59@gmail.com")
        
        self.criar_desktop_shortcut = tk.BooleanVar(value=True)
        self.instalar_dependencias = tk.BooleanVar(value=True)
        self.instalar_python_embarcado = tk.BooleanVar(value=False)  # Nova opção
        
        # Inicializar python_info com valor padrão
        self.python_info = {"instalado": False, "versao": None, "comando": None, "tem_venv": False}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Título
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(title_frame, text="Sistema de Gestão de Projetos 2.0", 
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(title_frame, text="Instalador Automático", 
                 font=("Arial", 12)).pack()
        
        # Notebook para abas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba 1: Configurações Básicas
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configurações")
        self.setup_config_tab(config_frame)
        
        # Aba 2: Configurações do Supabase
        supabase_frame = ttk.Frame(notebook)
        notebook.add(supabase_frame, text="Banco de Dados")
        self.setup_supabase_tab(supabase_frame)
        
        # Aba 3: Instalação
        install_frame = ttk.Frame(notebook)
        notebook.add(install_frame, text="Instalação")
        self.setup_install_tab(install_frame)
        
        # Botões principais
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(button_frame, text="Instalar Sistema", 
                  command=self.iniciar_instalacao).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Sair", 
                  command=self.root.quit).pack(side="right", padx=5)
        
    def setup_config_tab(self, parent):
        """Configura a aba de configurações básicas"""
        # Pasta de instalação
        ttk.Label(parent, text="Pasta de Instalação:").pack(anchor="w", pady=5)
        pasta_frame = ttk.Frame(parent)
        pasta_frame.pack(fill="x", pady=5)
        
        ttk.Entry(pasta_frame, textvariable=self.pasta_instalacao, width=50).pack(side="left", fill="x", expand=True)
        ttk.Button(pasta_frame, text="Procurar", command=self.escolher_pasta).pack(side="right", padx=5)
        
        # Opções
        ttk.Checkbutton(parent, text="Instalar dependências Python automaticamente", 
                       variable=self.instalar_dependencias).pack(anchor="w", pady=5)
        ttk.Checkbutton(parent, text="Criar atalho na área de trabalho", 
                       variable=self.criar_desktop_shortcut).pack(anchor="w", pady=5)
        
        # Verificar se Python está instalado
        python_status = self._verificar_python_instalado()
        if not python_status["instalado"]:
            ttk.Label(parent, text="⚠️ Python não detectado no sistema!", 
                     foreground="red", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,0))
            ttk.Checkbutton(parent, text="Baixar e instalar Python embarcado (sem instalação no sistema)", 
                           variable=self.instalar_python_embarcado).pack(anchor="w", pady=5)
            self.instalar_python_embarcado.set(True)  # Marcar por padrão
        else:
            ttk.Label(parent, text=f"✅ Python {python_status['versao']} detectado", 
                     foreground="green", font=("Arial", 10)).pack(anchor="w", pady=(10,0))
        
        # Email do administrador
        ttk.Label(parent, text="Email do Administrador:").pack(anchor="w", pady=(20,5))
        ttk.Entry(parent, textvariable=self.admin_email, width=50).pack(anchor="w", pady=5)
        
    def setup_supabase_tab(self, parent):
        """Configura a aba do Supabase"""
        ttk.Label(parent, text="Configuração do Banco de Dados Supabase", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Informação de que está pré-configurado
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill="x", pady=10)
        
        ttk.Label(info_frame, text="✅ Credenciais PRÉ-CONFIGURADAS", 
                 font=("Arial", 10, "bold"), foreground="green").pack()
        ttk.Label(info_frame, text="As credenciais do Supabase já estão configuradas neste instalador.", 
                 font=("Arial", 9)).pack()
        
        ttk.Label(parent, text="URL do Supabase:").pack(anchor="w", pady=5)
        url_entry = ttk.Entry(parent, textvariable=self.supabase_url, width=70, state="readonly")
        url_entry.pack(fill="x", pady=5)
        
        ttk.Label(parent, text="Chave do Supabase (anon key):").pack(anchor="w", pady=5)
        key_entry = ttk.Entry(parent, textvariable=self.supabase_key, width=70, show="*", state="readonly")
        key_entry.pack(fill="x", pady=5)
        
        # Instruções
        instructions = """
ℹ️ INFORMAÇÃO IMPORTANTE:

Este instalador já vem com as credenciais do Supabase pré-configuradas.
Você não precisa fazer nada nesta aba - tudo está pronto para uso!

O sistema se conectará automaticamente ao banco de dados durante a instalação.

Se futuramente precisar alterar as credenciais, você pode editar o arquivo .env
na pasta de instalação do sistema.
        """
        
        text_widget = tk.Text(parent, height=10, wrap="word")
        text_widget.insert("1.0", instructions)
        text_widget.config(state="disabled")
        text_widget.pack(fill="x", pady=10)
        
    def setup_install_tab(self, parent):
        """Configura a aba de instalação"""
        self.log_text = tk.Text(parent, height=20, wrap="word")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Barra de progresso
        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.progress.pack(fill="x", pady=5)
        
    def escolher_pasta(self):
        """Permite escolher a pasta de instalação"""
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_instalacao.set(pasta)
            
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def _verificar_python_instalado(self):
        """Verifica se Python está instalado no sistema e se tem módulo venv"""
        comandos = ["python", "python3", "py"]
        
        for comando in comandos:
            try:
                # Verificar versão
                result = subprocess.run([comando, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    versao = result.stdout.strip().replace("Python ", "")
                    
                    # Verificar se tem módulo venv
                    venv_check = subprocess.run([comando, "-m", "venv", "--help"], 
                                              capture_output=True, text=True, timeout=5)
                    
                    tem_venv = venv_check.returncode == 0
                    
                    return {
                        "instalado": True, 
                        "versao": versao, 
                        "comando": comando,
                        "tem_venv": tem_venv
                    }
            except:
                continue
        
        return {"instalado": False, "versao": None, "comando": None, "tem_venv": False}
        
    def iniciar_instalacao(self):
        """Inicia o processo de instalação em thread separada"""
        self.log_message("🔘 Botão de instalação clicado")
        
        if not self.validar_configuracoes():
            self.log_message("❌ Validação de configurações falhou")
            return
            
        self.log_message("✅ Configurações validadas - iniciando instalação")
        self.progress.start()
        threading.Thread(target=self.executar_instalacao, daemon=True).start()
        
    def validar_configuracoes(self):
        """Valida as configurações antes da instalação"""
        if not self.pasta_instalacao.get():
            messagebox.showerror("Erro", "Selecione uma pasta de instalação")
            return False
            
        if not self.supabase_url.get() or not self.supabase_key.get():
            messagebox.showerror("Erro", "Configure as credenciais do Supabase")
            return False
        
        # Verificar permissões de escrita na pasta
        pasta_destino = Path(self.pasta_instalacao.get())
        
        # Se a pasta já existe, perguntar se quer limpar
        if pasta_destino.exists() and any(pasta_destino.iterdir()):
            resposta = messagebox.askyesnocancel(
                "Pasta já existe",
                f"A pasta de instalação já contém arquivos:\n{pasta_destino}\n\n"
                "⚠️ IMPORTANTE: Se houver uma instalação anterior, é recomendado limpar.\n\n"
                "Deseja REMOVER TUDO e fazer instalação limpa?\n\n"
                "• Sim = Remove tudo e instala (RECOMENDADO)\n"
                "• Não = Tenta instalar por cima (pode dar erro)\n"
                "• Cancelar = Escolher outra pasta",
                icon='warning'
            )
            
            if resposta is None:  # Cancelar
                return False
            elif resposta:  # Sim - remover tudo
                try:
                    self.log_message(f"🗑️ Removendo pasta existente: {pasta_destino}")
                    
                    # Matar processos Python primeiro
                    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], 
                                 capture_output=True, timeout=10)
                    subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/T"], 
                                 capture_output=True, timeout=10)
                    time.sleep(2)
                    
                    # Remover pasta
                    shutil.rmtree(pasta_destino)
                    time.sleep(1)
                    self.log_message("✓ Pasta antiga removida com sucesso")
                    
                    # Recriar pasta vazia
                    pasta_destino.mkdir(parents=True, exist_ok=True)
                    
                except Exception as e:
                    messagebox.showerror(
                        "Erro ao Limpar",
                        f"Não foi possível remover a pasta existente.\n\n"
                        f"Erro: {e}\n\n"
                        "Tente:\n"
                        "1. Fechar todos os programas\n"
                        "2. Abrir Gerenciador de Tarefas e finalizar python.exe\n"
                        "3. Tentar novamente"
                    )
                    return False
        
        try:
            # Criar a pasta se não existir
            pasta_destino.mkdir(parents=True, exist_ok=True)
            
            # Testar permissão de escrita
            test_file = pasta_destino / ".test_permission"
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            messagebox.showerror(
                "Erro de Permissão", 
                f"Sem permissão de escrita na pasta:\n{pasta_destino}\n\n"
                "Sugestões:\n"
                "1. Execute o instalador como Administrador\n"
                "2. Escolha outra pasta (ex: C:\\SistemaGestao)\n"
                "3. Desative temporariamente o antivírus"
            )
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar pasta: {e}")
            return False
            
        return True
        
    def executar_instalacao(self):
        """Executa o processo de instalação"""
        try:
            self.log_message("🚀 Iniciando instalação do Sistema de Gestão de Projetos 2.0...")
            self.log_message(f"🔍 Executável atual: {sys.executable}")
            self.log_message(f"🔍 Script atual: {__file__}")
            
            # Verificar Python antes de começar
            self.log_message("🔍 Verificando Python no sistema...")
            python_info = self._verificar_python_instalado()
            self.python_info = python_info  # Guardar para uso posterior
            
            if python_info["instalado"]:
                self.log_message(f"  ✓ Python {python_info['versao']} encontrado")
                if python_info.get("tem_venv"):
                    self.log_message(f"  ✓ Módulo venv disponível")
                else:
                    self.log_message(f"  ⚠️ Módulo venv NÃO disponível")
                    self.log_message(f"  🔄 Ativando instalação de Python Embedded automaticamente...")
                    self.instalar_python_embarcado.set(True)
            else:
                self.log_message(f"  ⚠️ Python não encontrado no sistema")
                self.log_message(f"  🔄 Ativando instalação de Python Embedded automaticamente...")
                self.instalar_python_embarcado.set(True)
            
            # Criar pasta de instalação
            pasta_destino = Path(self.pasta_instalacao.get())
            pasta_destino.mkdir(parents=True, exist_ok=True)
            self.log_message(f"📁 Pasta de instalação criada: {pasta_destino}")
            
            # Copiar arquivos do sistema
            self.log_message("🔄 Iniciando cópia de arquivos...")
            self.copiar_arquivos_sistema(pasta_destino)
            self.log_message("✅ Arquivos copiados com sucesso")
            
            # Decidir qual Python usar ANTES de qualquer instalação
            python_path = None
            precisa_python_embarcado = (
                self.instalar_python_embarcado.get() or  # Usuário marcou manualmente
                not self.python_info.get("instalado", False) or  # Python não instalado
                not self.python_info.get("tem_venv", False)  # Python sem venv
            )
            
            # Instalar Python embarcado se necessário
            if precisa_python_embarcado:
                self.log_message("🔄 Baixando e instalando Python embarcado...")
                self.log_message(f"   Motivo: " + (
                    "Opção marcada pelo usuário" if self.instalar_python_embarcado.get() else
                    "Python não encontrado no sistema" if not self.python_info.get("instalado") else
                    "Python do sistema não possui módulo venv"
                ))
                
                python_path = self.instalar_python_portable(pasta_destino)
                if python_path:
                    self.log_message(f"✅ Python embarcado instalado em: {python_path}")
                else:
                    self.log_message("❌ Erro ao instalar Python embarcado")
                    raise Exception("Falha na instalação do Python embarcado")
            
            # Criar ambiente virtual
            if self.instalar_dependencias.get():
                self.log_message("🔄 Iniciando criação de ambiente virtual...")
                self.criar_ambiente_virtual(pasta_destino, python_path)
                self.log_message("✅ Ambiente virtual criado com sucesso")
            else:
                self.log_message("⏭️ Pulando criação de ambiente virtual (desmarcado)")
                
            # Configurar arquivo .env
            self.log_message("🔄 Criando arquivo de configuração...")
            self.criar_arquivo_env(pasta_destino)
            self.log_message("✅ Arquivo .env criado com sucesso")
            
            # Criar launcher executável
            self.criar_launcher_executavel(pasta_destino)
            
            # Criar scripts de execução
            self.log_message("🔄 Criando scripts de execução...")
            self.criar_scripts_execucao(pasta_destino)
            self.log_message("✅ Scripts criados com sucesso")
            
            # Criar atalho na área de trabalho
            if self.criar_desktop_shortcut.get():
                self.log_message("🔄 Criando atalho na área de trabalho...")
                self.criar_atalho_desktop(pasta_destino)
                self.log_message("✅ Atalho criado com sucesso")
            else:
                self.log_message("⏭️ Pulando criação de atalho (desmarcado)")
                
            self.log_message("✅ Instalação concluída com sucesso!")
            self.log_message(f"📍 Sistema instalado em: {pasta_destino}")
            self.log_message("🎉 Você pode executar o sistema usando o arquivo 'executar_sistema.bat'")
            
            # Mostrar mensagem de sucesso SEM executar nada
            self.root.after(0, lambda: messagebox.showinfo("Sucesso", 
                f"Sistema instalado com sucesso!\n\nLocalização: {pasta_destino}\n\nExecute 'executar_sistema.bat' para iniciar."))
            
        except Exception as e:
            error_msg = f"Erro durante a instalação: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            # Mostrar erro na thread principal
            self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
        finally:
            self.progress.stop()
            self.log_message("🔚 Processo de instalação finalizado")
            
    def copiar_arquivos_sistema(self, destino):
        """Copia os arquivos do sistema incluídos no executável"""
        self.log_message("📦 Extraindo arquivos do sistema...")
        
        try:
            # Tentar primeiro os arquivos incluídos no executável
            if self._copiar_arquivos_embarcados(destino):
                return
                
            # Fallback: tentar baixar do GitHub
            self.log_message("📦 Tentando baixar do repositório...")
            if self._baixar_do_github(destino):
                return
                
            # Último fallback: arquivos locais
            self.log_message("📦 Tentando arquivos locais...")
            self._copiar_arquivos_local(destino)
            
        except Exception as e:
            self.log_message(f"❌ Erro durante cópia de arquivos: {str(e)}")
            raise
    
    def _copiar_arquivos_embarcados(self, destino):
        """Copia arquivos embarcados no executável"""
        try:
            # Quando executado como executável PyInstaller, os arquivos ficam em sys._MEIPASS
            if hasattr(sys, '_MEIPASS'):
                base_path = Path(sys._MEIPASS) / "projeto_arquivos"
            else:
                # Executando como script Python normal
                base_path = Path(__file__).parent
            
            if not base_path.exists():
                return False
                
            self.log_message("  � Extraindo arquivos embarcados...")
            
            # Arquivos e pastas essenciais
            items_para_copiar = [
                'app_producao.py',
                'requirements.txt',
                'supabase_client.py',
                'config/',
                'routes/',
                'templates/',
                'static/',
                'utils/',
                'gunicorn.conf.py',
                'restricoes.json'
            ]
            
            sucesso = False
            for item in items_para_copiar:
                origem = base_path / item
                destino_item = destino / item
                
                if origem.exists():
                    if origem.is_file():
                        shutil.copy2(origem, destino_item)
                        self.log_message(f"  ✓ Extraído: {item}")
                        sucesso = True
                    else:
                        shutil.copytree(origem, destino_item, dirs_exist_ok=True)
                        self.log_message(f"  ✓ Extraída pasta: {item}")
                        sucesso = True
                        
            return sucesso
            
        except Exception as e:
            self.log_message(f"  ❌ Erro ao extrair arquivos embarcados: {str(e)}")
            return False
    
    def _baixar_do_github(self, destino):
        """Baixa arquivos do repositório GitHub"""
        try:
            # URL do repositório no GitHub
            repo_url = "https://github.com/izakoliveira/sistema-gestao-projetos-2.0/archive/refs/heads/main.zip"
            
            # Criar pasta temporária
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_file = temp_path / "repo.zip"
                
                # Baixar o repositório
                self.log_message("  📥 Baixando repositório...")
                urllib.request.urlretrieve(repo_url, zip_file)
                
                # Extrair o arquivo ZIP
                self.log_message("  📂 Extraindo arquivos...")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Encontrar a pasta extraída
                extracted_folders = [f for f in temp_path.iterdir() if f.is_dir()]
                if not extracted_folders:
                    return False
                
                repo_folder = extracted_folders[0]
                
                # Arquivos e pastas essenciais para copiar
                items_para_copiar = [
                    'app_producao.py',
                    'requirements.txt',
                    'supabase_client.py',
                    'config/',
                    'routes/',
                    'templates/',
                    'static/',
                    'utils/',
                    'gunicorn.conf.py',
                    'restricoes.json'
                ]
                
                # Copiar arquivos necessários
                sucesso = False
                for item in items_para_copiar:
                    origem = repo_folder / item
                    destino_item = destino / item
                    
                    if origem.exists():
                        if origem.is_file():
                            shutil.copy2(origem, destino_item)
                            self.log_message(f"  ✓ Baixado: {item}")
                            sucesso = True
                        else:
                            shutil.copytree(origem, destino_item, dirs_exist_ok=True)
                            self.log_message(f"  ✓ Baixada pasta: {item}")
                            sucesso = True
                            
                return sucesso
                        
        except Exception as e:
            self.log_message(f"❌ Erro ao baixar do GitHub: {str(e)}")
            return False
    
    def _copiar_arquivos_local(self, destino):
        """Método fallback para copiar arquivos da pasta local"""
        self.log_message("📦 Tentando copiar arquivos locais...")
        
        # Obter pasta atual do instalador
        pasta_origem = Path(__file__).parent
        
        # Arquivos e pastas essenciais para copiar
        items_para_copiar = [
            'app_producao.py',
            'requirements.txt',
            'supabase_client.py',
            'config/',
            'routes/',
            'templates/',
            'static/',
            'utils/',
            'gunicorn.conf.py',
            'restricoes.json'
        ]
        
        for item in items_para_copiar:
            origem = pasta_origem / item
            destino_item = destino / item
            
            if origem.exists():
                if origem.is_file():
                    shutil.copy2(origem, destino_item)
                    self.log_message(f"  ✓ Copiado: {item}")
                else:
                    shutil.copytree(origem, destino_item, dirs_exist_ok=True)
                    self.log_message(f"  ✓ Copiada pasta: {item}")
            else:
                self.log_message(f"  ⚠️ Item não encontrado: {item}")
    
    def instalar_python_portable(self, destino):
        """Baixa e instala Python embarcado (portátil)"""
        try:
            self.log_message("  📥 Baixando Python embarcado 3.11...")
            
            # URL do Python embarcado (embed/portable)
            python_url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
            python_dir = destino / "python_embedded"
            python_dir.mkdir(exist_ok=True)
            
            # Baixar Python
            zip_path = destino / "python_embed.zip"
            self.log_message(f"  📦 Baixando de: {python_url}")
            urllib.request.urlretrieve(python_url, zip_path)
            self.log_message("  ✓ Download concluído")
            
            # Extrair
            self.log_message("  📂 Extraindo arquivos...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(python_dir)
            
            # Remover zip
            zip_path.unlink()
            self.log_message("  ✓ Python embarcado extraído")
            
            # Baixar get-pip.py
            self.log_message("  📥 Baixando get-pip...")
            pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = python_dir / "get-pip.py"
            urllib.request.urlretrieve(pip_url, get_pip_path)
            
            # Habilitar pip no Python embarcado
            pth_file = None
            for file in python_dir.glob("*._pth"):
                pth_file = file
                break
            
            if pth_file:
                content = pth_file.read_text()
                if "import site" not in content:
                    pth_file.write_text(content.replace("#import site", "import site"))
            
            # Instalar pip
            python_exe = python_dir / "python.exe"
            self.log_message("  🔧 Instalando pip...")
            result = subprocess.run([str(python_exe), str(get_pip_path)], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log_message("  ✓ Pip instalado com sucesso")
            
            # IMPORTANTE: Python Embedded precisa ter venv instalado via pip
            self.log_message("  🔧 Verificando módulo venv...")
            venv_check = subprocess.run([str(python_exe), "-m", "venv", "--help"],
                                       capture_output=True, text=True, timeout=10)
            
            if venv_check.returncode != 0:
                self.log_message("  ⚠️ Módulo venv não encontrado, instalando...")
                # Python Embedded não vem com venv, precisa instalar
                result = subprocess.run([str(python_exe), "-m", "pip", "install", "virtualenv"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.log_message("  ✓ virtualenv instalado (substituto para venv)")
                else:
                    self.log_message(f"  ⚠️ Não foi possível instalar virtualenv: {result.stderr}")
            else:
                self.log_message("  ✓ Módulo venv disponível")
            
            return python_exe
            
        except Exception as e:
            self.log_message(f"  ❌ Erro ao instalar Python embarcado: {str(e)}")
            return None
                
    def criar_ambiente_virtual(self, destino, python_path=None):
        """Cria ambiente virtual e instala dependências"""
        self.log_message("🐍 Criando ambiente virtual Python...")
        
        try:
            # Usar Python embarcado se fornecido, senão encontrar no sistema
            if python_path:
                python_executable = str(python_path)
                self.log_message(f"  🔍 Usando Python embarcado: {python_executable}")
            else:
                python_executable = self._encontrar_python_sistema()
                self.log_message(f"  🔍 Usando Python: {python_executable}")
            
            # Criar ambiente virtual
            venv_path = destino / "venv"
            self.log_message(f"  📁 Criando venv em: {venv_path}")
            
            # Se a pasta venv já existe, tentar remover
            if venv_path.exists():
                self.log_message(f"  ⚠️ Pasta venv já existe, tentando remover...")
                
                # Primeiro, tentar matar processos Python que possam estar usando a pasta
                try:
                    self.log_message(f"  🔄 Encerrando processos Python anteriores...")
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "python.exe", "/T"],
                        capture_output=True,
                        timeout=10
                    )
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "pythonw.exe", "/T"],
                        capture_output=True,
                        timeout=10
                    )
                    time.sleep(2)  # Aguardar processos encerrarem
                except:
                    pass  # Não falha se não houver processos
                
                # Agora tentar remover a pasta
                tentativas = 3
                for i in range(tentativas):
                    try:
                        if venv_path.exists():
                            shutil.rmtree(venv_path, ignore_errors=False)
                            self.log_message(f"  ✓ Pasta antiga removida")
                            time.sleep(1)
                            break
                    except PermissionError as e:
                        if i < tentativas - 1:
                            self.log_message(f"  ⚠️ Tentativa {i+1}/{tentativas} falhou, aguardando...")
                            time.sleep(3)
                        else:
                            self.log_message(f"  ❌ Erro ao remover pasta antiga após {tentativas} tentativas")
                            raise Exception(
                                "Não foi possível remover a pasta venv existente.\n\n"
                                "SOLUÇÕES:\n"
                                "1. Feche TODOS os programas Python que estejam rodando\n"
                                "2. Feche o VS Code e outros editores\n"
                                "3. Abra o Gerenciador de Tarefas (Ctrl+Shift+Esc)\n"
                                "4. Finalize todos os processos 'python.exe' e 'pythonw.exe'\n"
                                "5. Tente instalar novamente\n\n"
                                f"OU escolha outra pasta de instalação (não: {destino})"
                            )
                    except Exception as e:
                        raise Exception(f"Erro inesperado ao remover venv: {e}")
            
            # Verificar permissões de escrita
            try:
                test_file = destino / "test_permission.tmp"
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                raise Exception(f"Sem permissão de escrita na pasta: {destino}\nErro: {e}")
            
            # Tentar criar ambiente virtual com venv
            self.log_message("  🔧 Tentando criar com 'python -m venv'...")
            result = subprocess.run(
                [python_executable, "-m", "venv", str(venv_path)], 
                capture_output=True, 
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.log_message(f"  ⚠️ Falha com venv: {result.stderr}")
                self.log_message(f"  🔧 Tentando criar com 'virtualenv'...")
                
                # Tentar com virtualenv como fallback
                result = subprocess.run(
                    [python_executable, "-m", "virtualenv", str(venv_path)], 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    self.log_message(f"  ❌ Erro com virtualenv também:")
                    self.log_message(f"     STDOUT: {result.stdout}")
                    self.log_message(f"     STDERR: {result.stderr}")
                    raise Exception(
                        "Não foi possível criar ambiente virtual.\n\n"
                        "O Python usado não possui 'venv' nem 'virtualenv'.\n\n"
                        "SOLUÇÃO:\n"
                        "Marque a opção 'Instalar Python Embedded' e tente novamente."
                    )
                else:
                    self.log_message("  ✓ Ambiente virtual criado com virtualenv")
            else:
                self.log_message("  ✓ Ambiente virtual criado com venv")
            
            # Determinar o executável pip
            if os.name == "nt":  # Windows
                pip_path = venv_path / "Scripts" / "pip.exe"
                python_path = venv_path / "Scripts" / "python.exe"
            else:  # Linux/Mac
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"
                
            # Verificar se os executáveis foram criados
            if not python_path.exists():
                raise Exception(f"Python não foi criado em: {python_path}")
            if not pip_path.exists():
                raise Exception(f"Pip não foi criado em: {pip_path}")
                
            self.log_message(f"  🔍 Python venv: {python_path}")
            self.log_message(f"  🔍 Pip venv: {pip_path}")
            
            # Atualizar pip
            self.log_message("  ⬆️ Atualizando pip...")
            result = subprocess.run(
                [str(python_path), "-m", "pip", "install", "--upgrade", "pip"], 
                capture_output=True, 
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.log_message(f"  ⚠️ Aviso ao atualizar pip: {result.stderr}")
                # Não falha aqui, apenas avisa
            else:
                self.log_message("  ✓ Pip atualizado")
            
            # Verificar se requirements.txt existe
            requirements_file = destino / "requirements.txt"
            if not requirements_file.exists():
                raise Exception(f"Arquivo requirements.txt não encontrado em: {requirements_file}")
                
            self.log_message("  📦 Instalando dependências...")
            
            # Instalar dependências
            result = subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_file)], 
                capture_output=True, 
                text=True,
                timeout=600  # 10 minutos para instalar dependências
            )
            
            if result.returncode != 0:
                self.log_message(f"  ❌ Erro ao instalar dependências:")
                self.log_message(f"     STDOUT: {result.stdout}")
                self.log_message(f"     STDERR: {result.stderr}")
                raise Exception(f"Falha ao instalar dependências: {result.stderr}")
                
            self.log_message("  ✓ Dependências instaladas")
            
        except subprocess.TimeoutExpired as e:
            self.log_message(f"  ❌ Timeout na operação: {str(e)}")
            raise Exception(f"Timeout durante criação do ambiente virtual: {str(e)}")
        except Exception as e:
            self.log_message(f"  ❌ Erro no ambiente virtual: {str(e)}")
            raise
    
    def _encontrar_python_sistema(self):
        """Encontra o Python real do sistema ao invés do executável PyInstaller"""
        try:
            # Opção 1: Tentar python no PATH
            result = subprocess.run(["python", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Verificar se tem módulo venv
                venv_check = subprocess.run(["python", "-m", "venv", "--help"], 
                                          capture_output=True, text=True, timeout=10)
                if venv_check.returncode == 0:
                    self.log_message(f"  🔍 Python encontrado no PATH: {result.stdout.strip()}")
                    return "python"
                else:
                    self.log_message(f"  ⚠️ Python no PATH não tem módulo venv")
        except:
            pass
        
        try:
            # Opção 2: Tentar python3 no PATH  
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Verificar se tem módulo venv
                venv_check = subprocess.run(["python3", "-m", "venv", "--help"], 
                                          capture_output=True, text=True, timeout=10)
                if venv_check.returncode == 0:
                    self.log_message(f"  🔍 Python3 encontrado no PATH: {result.stdout.strip()}")
                    return "python3"
                else:
                    self.log_message(f"  ⚠️ Python3 no PATH não tem módulo venv")
        except:
            pass
            
        # Opção 3: Verificar localizações comuns do Python no Windows
        possible_paths = [
            r"C:\Python311\python.exe",
            r"C:\Python310\python.exe", 
            r"C:\Python39\python.exe",
            r"C:\Users\{}\AppData\Local\Programs\Python\Python311\python.exe".format(os.getenv('USERNAME')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python310\python.exe".format(os.getenv('USERNAME')),
            r"C:\Program Files\Python311\python.exe",
            r"C:\Program Files\Python310\python.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # Verificar se tem módulo venv
                        venv_check = subprocess.run([path, "-m", "venv", "--help"], 
                                                  capture_output=True, text=True, timeout=10)
                        if venv_check.returncode == 0:
                            self.log_message(f"  🔍 Python encontrado em: {path} - {result.stdout.strip()}")
                            return path
                        else:
                            self.log_message(f"  ⚠️ Python em {path} não tem módulo venv")
                except:
                    continue
        
        # Opção 4: Usar o py launcher do Windows
        try:
            result = subprocess.run(["py", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Verificar se tem módulo venv
                venv_check = subprocess.run(["py", "-m", "venv", "--help"], 
                                          capture_output=True, text=True, timeout=10)
                if venv_check.returncode == 0:
                    self.log_message(f"  🔍 Python encontrado via py launcher: {result.stdout.strip()}")
                    return "py"
                else:
                    self.log_message(f"  ⚠️ Python via py launcher não tem módulo venv")
        except:
            pass
            
        # Se chegou até aqui, não encontrou Python com venv
        self.log_message("  ❌ Nenhum Python com módulo venv encontrado no sistema")
        raise Exception(
            "Python não encontrado ou não possui módulo venv.\n\n"
            "SOLUÇÃO:\n"
            "Marque a opção 'Instalar Python Embedded' na aba de Configuração\n"
            "e clique em Instalar novamente.\n\n"
            "OU instale Python 3.8+ completo de python.org"
        )
        
    def criar_arquivo_env(self, destino):
        """Cria o arquivo .env com as configurações"""
        self.log_message("⚙️ Criando arquivo de configuração...")
        
        env_content = f"""# Configurações do Supabase
SUPABASE_URL={self.supabase_url.get()}
SUPABASE_KEY={self.supabase_key.get()}

# Chave secreta do Flask
FLASK_SECRET_KEY={os.urandom(24).hex()}

# Configurações de email
ADMIN_EMAIL={self.admin_email.get()}

# Configurações de ambiente
FLASK_ENV=production
FLASK_APP=app_producao.py
"""
        
        env_file = destino / ".env"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
            
        self.log_message("  ✓ Arquivo .env criado")
        
    def criar_scripts_execucao(self, destino):
        """Cria scripts para executar o sistema"""
        self.log_message("📜 Criando scripts de execução...")
        
        # Script Windows (.bat) - Janela Normal
        bat_content = f"""@echo off
cd /d "{destino}"
call venv\\Scripts\\activate
echo Iniciando Sistema de Gestao de Projetos 2.0...
echo.
echo Sistema rodando em: http://localhost:5000
echo.
echo Para parar o sistema, feche esta janela ou pressione Ctrl+C
echo.
start "" http://localhost:5000
python app_producao.py
pause
"""
        
        bat_file = destino / "executar_sistema.bat"
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_content)
        
        # Script Windows Minimizado (.bat)
        bat_min_content = f"""@echo off
cd /d "{destino}"
start /MIN cmd /c "call venv\\Scripts\\activate && python app_producao.py"
timeout /t 3 /nobreak >nul
start "" http://localhost:5000
echo.
echo Sistema iniciado em segundo plano (janela minimizada)
echo Acesse: http://localhost:5000
echo.
echo Para parar o sistema:
echo 1. Procure pela janela minimizada do CMD na barra de tarefas
echo 2. Ou abra o Gerenciador de Tarefas e finalize python.exe
echo.
pause
"""
        
        bat_min_file = destino / "executar_minimizado.bat"
        with open(bat_min_file, "w", encoding="utf-8") as f:
            f.write(bat_min_content)
        
        # Script VBS para execução oculta (sem janela)
        vbs_content = f"""Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{destino}"
WshShell.Run "cmd /c call venv\\Scripts\\activate && python app_producao.py", 0, False
WScript.Sleep 3000
WshShell.Run "http://localhost:5000"
Set WshShell = Nothing
"""
        
        vbs_file = destino / "iniciar_oculto.vbs"
        with open(vbs_file, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        
        # Script para parar o sistema
        stop_content = f"""@echo off
echo Parando Sistema de Gestao de Projetos...
taskkill /F /IM python.exe /T 2>nul
if %errorlevel% equ 0 (
    echo Sistema parado com sucesso!
) else (
    echo Nenhum processo Python encontrado.
)
pause
"""
        
        stop_file = destino / "parar_sistema.bat"
        with open(stop_file, "w", encoding="utf-8") as f:
            f.write(stop_content)
            
        # Script Linux/Mac (.sh)
        sh_content = f"""#!/bin/bash
cd "{destino}"
source venv/bin/activate
echo "Iniciando Sistema de Gestao de Projetos 2.0..."
python app_producao.py
"""
        
        sh_file = destino / "executar_sistema.sh"
        with open(sh_file, "w", encoding="utf-8") as f:
            f.write(sh_content)
            
        # Tornar executável no Linux/Mac
        if os.name != "nt":
            os.chmod(sh_file, 0o755)
            
        self.log_message("  ✓ Scripts de execução criados")
        self.log_message("  ✓ Script minimizado criado")
        self.log_message("  ✓ Script oculto criado (.vbs)")
        self.log_message("  ✓ Script para parar sistema criado")
        
    def criar_atalho_desktop(self, destino):
        """Cria atalho na área de trabalho"""
        try:
            self.log_message("🖥️ Criando atalho na área de trabalho...")
            
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                desktop = Path.home() / "Área de Trabalho"
                
            if desktop.exists():
                atalho_path = desktop / "Sistema de Gestão de Projetos.lnk"
                
                # No Windows, usar um .bat simples
                if os.name == "nt":
                    bat_atalho = desktop / "Sistema de Gestão de Projetos.bat"
                    with open(bat_atalho, "w", encoding="utf-8") as f:
                        f.write(f'@echo off\ncd /d "{destino}"\ncall executar_sistema.bat')
                    self.log_message("  ✓ Atalho criado na área de trabalho")
                else:
                    # Para Linux, criar um .desktop file
                    desktop_file_content = f"""[Desktop Entry]
Name=Sistema de Gestão de Projetos
Comment=Sistema de Gestão de Projetos 2.0
Exec={destino}/executar_sistema.sh
Icon=applications-office
Terminal=true
Type=Application
Categories=Office;
"""
                    desktop_file = desktop / "sistema-gestao-projetos.desktop"
                    with open(desktop_file, "w", encoding="utf-8") as f:
                        f.write(desktop_file_content)
                    os.chmod(desktop_file, 0o755)
                    self.log_message("  ✓ Atalho criado na área de trabalho")
            else:
                self.log_message("  ⚠️ Área de trabalho não encontrada")
                
        except Exception as e:
            self.log_message(f"  ⚠️ Erro ao criar atalho: {str(e)}")


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

def is_admin():
    """Verifica se o script está rodando como administrador"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def main():
    """Função principal"""
    # No Windows, avisar se não for administrador
    if os.name == 'nt' and not is_admin():
        root = tk.Tk()
        root.withdraw()  # Esconder janela principal temporariamente
        
        resposta = messagebox.askyesno(
            "Privilégios de Administrador",
            "⚠️ O instalador não está rodando como Administrador.\n\n"
            "Isso pode causar erros de permissão durante a instalação.\n\n"
            "Recomendações:\n"
            "• Clique com botão direito no instalador\n"
            "• Selecione 'Executar como administrador'\n\n"
            "Deseja continuar mesmo assim?",
            icon='warning'
        )
        
        root.destroy()
        
        if not resposta:
            sys.exit(0)
    
    app = InstaladorSistema()
    app.root.mainloop()

if __name__ == "__main__":
    main()