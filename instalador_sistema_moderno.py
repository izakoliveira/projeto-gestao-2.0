#!/usr/bin/env python3
"""
Instalador do SGP - Sistema de Gestão de Projetos 2.0
Interface Moderna Estilo Windows 11
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

class InstaladorModerno:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SGP - Sistema de Gestão de Projetos 2.0")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        # Cores Windows 11
        self.cor_fundo = "#F3F3F3"  # Cinza claro
        self.cor_card = "#FFFFFF"    # Branco
        self.cor_primaria = "#0078D4"  # Azul Windows
        self.cor_texto = "#1F1F1F"   # Cinza escuro
        self.cor_texto_suave = "#616161"  # Cinza médio
        self.cor_sucesso = "#107C10"  # Verde
        self.cor_aviso = "#FF8C00"    # Laranja
        
        # Configurar cores da janela
        self.root.configure(bg=self.cor_fundo)
        
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
        self.instalar_python_embarcado = tk.BooleanVar(value=False)
        
        # Inicializar python_info
        self.python_info = {"instalado": False, "versao": None, "comando": None, "tem_venv": False}
        
        # Etapa atual (para navegação wizard)
        self.etapa_atual = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface moderna"""
        # Container principal com padding
        main_container = tk.Frame(self.root, bg=self.cor_fundo)
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header com gradiente simulado
        self.criar_header(main_container)
        
        # Container de conteúdo (cards)
        self.content_frame = tk.Frame(main_container, bg=self.cor_fundo)
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Footer com botões (CRIAR ANTES de mostrar tela)
        self.criar_footer(main_container)
        
        # Mostrar tela inicial (DEPOIS de criar botões)
        self.mostrar_tela_bem_vindo()
        
    def criar_header(self, parent):
        """Cria o header moderno com gradiente"""
        header = tk.Frame(parent, bg=self.cor_primaria, height=120)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # Ícone grande (emoji como placeholder)
        icon_label = tk.Label(
            header,
            text="📊",
            font=("Segoe UI", 48),
            bg=self.cor_primaria,
            fg="white"
        )
        icon_label.pack(pady=(20, 5))
        
        # Título
        title_label = tk.Label(
            header,
            text="Sistema de Gestão de Projetos",
            font=("Segoe UI", 20, "bold"),
            bg=self.cor_primaria,
            fg="white"
        )
        title_label.pack()
        
        # Subtítulo
        subtitle_label = tk.Label(
            header,
            text="Instalador v2.0",
            font=("Segoe UI", 11),
            bg=self.cor_primaria,
            fg="white"
        )
        subtitle_label.pack()
        
    def criar_footer(self, parent):
        """Cria o footer com botões modernos"""
        self.footer = tk.Frame(parent, bg=self.cor_fundo, height=80)
        self.footer.pack(fill="x", side="bottom", padx=40, pady=(0, 20))
        self.footer.pack_propagate(False)
        
        # Separador
        separator = tk.Frame(self.footer, bg="#E0E0E0", height=1)
        separator.pack(fill="x", pady=(0, 20))
        
        # Container de botões
        self.btn_container = tk.Frame(self.footer, bg=self.cor_fundo)
        self.btn_container.pack(fill="x")
        
        # Botão Cancelar (esquerda)
        self.btn_cancelar = self.criar_botao_moderno(
            self.btn_container,
            text="Cancelar",
            command=self.root.quit,
            primary=False
        )
        self.btn_cancelar.pack(side="left")
        
        # Botões Voltar e Avançar (direita)
        self.btn_voltar = self.criar_botao_moderno(
            self.btn_container,
            text="← Voltar",
            command=self.voltar_etapa,
            primary=False
        )
        self.btn_voltar.pack(side="right", padx=(10, 0))
        
        self.btn_avancar = self.criar_botao_moderno(
            self.btn_container,
            text="Avançar →",
            command=self.avancar_etapa,
            primary=True
        )
        self.btn_avancar.pack(side="right")
        
        # Inicialmente só mostra botão de avançar
        self.btn_voltar.pack_forget()
        
    def criar_botao_moderno(self, parent, text, command, primary=False):
        """Cria um botão com estilo moderno"""
        if primary:
            bg_color = self.cor_primaria
            fg_color = "white"
            hover_color = "#005A9E"
        else:
            bg_color = "#E8E8E8"
            fg_color = self.cor_texto
            hover_color = "#D8D8D8"
        
        # Frame para simular border radius
        btn_frame = tk.Frame(parent, bg=bg_color, highlightthickness=0)
        
        btn = tk.Label(
            btn_frame,
            text=text,
            font=("Segoe UI", 10, "bold" if primary else "normal"),
            bg=bg_color,
            fg=fg_color,
            padx=30,
            pady=12,
            cursor="hand2"
        )
        btn.pack(padx=1, pady=1)
        
        # Eventos de hover
        def on_enter(e):
            btn.config(bg=hover_color)
            btn_frame.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
            btn_frame.config(bg=bg_color)
        
        def on_click(e):
            command()
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)
        
        return btn_frame
        
    def criar_card(self, parent, titulo=None):
        """Cria um card moderno com sombra"""
        # Frame externo para sombra
        shadow_frame = tk.Frame(parent, bg="#D0D0D0")
        shadow_frame.pack(fill="both", expand=True, pady=5)
        
        # Card principal
        card = tk.Frame(shadow_frame, bg=self.cor_card)
        card.pack(fill="both", expand=True, padx=2, pady=2)
        
        if titulo:
            titulo_label = tk.Label(
                card,
                text=titulo,
                font=("Segoe UI", 14, "bold"),
                bg=self.cor_card,
                fg=self.cor_texto,
                anchor="w"
            )
            titulo_label.pack(fill="x", padx=25, pady=(20, 10))
        
        # Container de conteúdo do card
        content = tk.Frame(card, bg=self.cor_card)
        content.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        return content
        
    def mostrar_tela_bem_vindo(self):
        """Tela de boas-vindas moderna"""
        self.limpar_conteudo()
        
        card = self.criar_card(self.content_frame)
        
        # Ícone grande
        icon = tk.Label(
            card,
            text="🚀",
            font=("Segoe UI", 72),
            bg=self.cor_card
        )
        icon.pack(pady=(40, 20))
        
        # Título de boas-vindas
        titulo = tk.Label(
            card,
            text="Bem-vindo ao Instalador!",
            font=("Segoe UI", 24, "bold"),
            bg=self.cor_card,
            fg=self.cor_texto
        )
        titulo.pack(pady=(0, 10))
        
        # Descrição
        desc = tk.Label(
            card,
            text="Este assistente irá guiá-lo através da instalação\ndo Sistema de Gestão de Projetos 2.0",
            font=("Segoe UI", 11),
            bg=self.cor_card,
            fg=self.cor_texto_suave,
            justify="center"
        )
        desc.pack(pady=(0, 30))
        
        # Lista de recursos
        recursos_frame = tk.Frame(card, bg=self.cor_card)
        recursos_frame.pack(pady=20)
        
        recursos = [
            ("✓", "Instalação automatizada", self.cor_sucesso),
            ("✓", "Banco de dados pré-configurado", self.cor_sucesso),
            ("✓", "Ambiente Python isolado", self.cor_sucesso),
            ("✓", "Atalho na área de trabalho", self.cor_sucesso)
        ]
        
        for icone, texto, cor in recursos:
            item_frame = tk.Frame(recursos_frame, bg=self.cor_card)
            item_frame.pack(fill="x", pady=5)
            
            tk.Label(
                item_frame,
                text=icone,
                font=("Segoe UI", 12, "bold"),
                bg=self.cor_card,
                fg=cor,
                width=3
            ).pack(side="left")
            
            tk.Label(
                item_frame,
                text=texto,
                font=("Segoe UI", 11),
                bg=self.cor_card,
                fg=self.cor_texto,
                anchor="w"
            ).pack(side="left", fill="x")
        
        # Atualizar botões
        self.btn_avancar.pack()
        self.btn_voltar.pack_forget()
        
    def mostrar_tela_configuracao(self):
        """Tela de configuração moderna"""
        self.limpar_conteudo()
        
        card = self.criar_card(self.content_frame, "Configuração da Instalação")
        
        # Pasta de instalação
        pasta_label = tk.Label(
            card,
            text="Local de Instalação",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_card,
            fg=self.cor_texto,
            anchor="w"
        )
        pasta_label.pack(fill="x", pady=(10, 5))
        
        pasta_frame = tk.Frame(card, bg=self.cor_card)
        pasta_frame.pack(fill="x", pady=(0, 20))
        
        pasta_entry = tk.Entry(
            pasta_frame,
            textvariable=self.pasta_instalacao,
            font=("Segoe UI", 10),
            bg="white",
            fg=self.cor_texto,
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground="#D0D0D0",
            highlightcolor=self.cor_primaria
        )
        pasta_entry.pack(side="left", fill="x", expand=True, ipady=8)
        
        btn_procurar = tk.Button(
            pasta_frame,
            text="📁 Procurar",
            font=("Segoe UI", 9),
            bg="#E8E8E8",
            fg=self.cor_texto,
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.escolher_pasta
        )
        btn_procurar.pack(side="right", padx=(10, 0))
        
        # Status do Python
        python_label = tk.Label(
            card,
            text="Ambiente Python",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_card,
            fg=self.cor_texto,
            anchor="w"
        )
        python_label.pack(fill="x", pady=(20, 5))
        
        python_info = self._verificar_python_instalado()
        self.python_info = python_info
        
        # Card de status
        status_frame = tk.Frame(card, bg="#F8F8F8", relief="flat", bd=1)
        status_frame.pack(fill="x", pady=(0, 20))
        
        if python_info["instalado"]:
            status_icon = tk.Label(
                status_frame,
                text="✓",
                font=("Segoe UI", 16, "bold"),
                bg="#F8F8F8",
                fg=self.cor_sucesso
            )
            status_icon.pack(side="left", padx=(15, 10), pady=10)
            
            status_text = tk.Label(
                status_frame,
                text=f"Python {python_info['versao']} detectado",
                font=("Segoe UI", 10),
                bg="#F8F8F8",
                fg=self.cor_texto
            )
            status_text.pack(side="left", pady=10)
        else:
            status_icon = tk.Label(
                status_frame,
                text="⚠",
                font=("Segoe UI", 16, "bold"),
                bg="#F8F8F8",
                fg=self.cor_aviso
            )
            status_icon.pack(side="left", padx=(15, 10), pady=10)
            
            status_text = tk.Label(
                status_frame,
                text="Python não detectado - será instalado automaticamente",
                font=("Segoe UI", 10),
                bg="#F8F8F8",
                fg=self.cor_texto
            )
            status_text.pack(side="left", pady=10)
            
            self.instalar_python_embarcado.set(True)
        
        # Opções
        opcoes_label = tk.Label(
            card,
            text="Opções",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_card,
            fg=self.cor_texto,
            anchor="w"
        )
        opcoes_label.pack(fill="x", pady=(20, 10))
        
        # Checkboxes modernos
        self.criar_checkbox_moderno(
            card,
            "Criar atalho na área de trabalho",
            self.criar_desktop_shortcut
        )
        
        self.criar_checkbox_moderno(
            card,
            "Instalar dependências automaticamente",
            self.instalar_dependencias
        )
        
        # Atualizar botões
        self.btn_voltar.pack(side="right", padx=(10, 0))
        self.btn_avancar.pack(side="right")
        
    def criar_checkbox_moderno(self, parent, texto, variable):
        """Cria um checkbox com estilo moderno"""
        frame = tk.Frame(parent, bg=self.cor_card)
        frame.pack(fill="x", pady=5)
        
        check = tk.Checkbutton(
            frame,
            text=texto,
            variable=variable,
            font=("Segoe UI", 10),
            bg=self.cor_card,
            fg=self.cor_texto,
            activebackground=self.cor_card,
            activeforeground=self.cor_texto,
            selectcolor="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        check.pack(anchor="w")
        
    def mostrar_tela_instalacao(self):
        """Tela de instalação com progresso"""
        self.limpar_conteudo()
        
        card = self.criar_card(self.content_frame, "Instalando...")
        
        # Status atual
        self.status_label = tk.Label(
            card,
            text="Preparando instalação...",
            font=("Segoe UI", 12),
            bg=self.cor_card,
            fg=self.cor_texto,
            anchor="w"
        )
        self.status_label.pack(fill="x", pady=(20, 10))
        
        # Barra de progresso moderna
        progress_container = tk.Frame(card, bg="#E8E8E8", height=8)
        progress_container.pack(fill="x", pady=(0, 20))
        progress_container.pack_propagate(False)
        
        self.progress_bar = tk.Frame(progress_container, bg=self.cor_primaria, width=0)
        self.progress_bar.pack(side="left", fill="y")
        
        # Log de instalação
        log_frame = tk.Frame(card, bg="white", relief="flat", bd=1)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 9),
            bg="white",
            fg="#333333",
            relief="flat",
            bd=0,
            yscrollcommand=scrollbar.set,
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar.config(command=self.log_text.yview)
        
        # Ocultar botões durante instalação
        self.btn_voltar.pack_forget()
        self.btn_avancar.pack_forget()
        self.btn_cancelar.pack_forget()
        
        # Iniciar instalação
        threading.Thread(target=self.executar_instalacao, daemon=True).start()
        
    def mostrar_tela_concluido(self):
        """Tela de conclusão"""
        self.limpar_conteudo()
        
        card = self.criar_card(self.content_frame)
        
        # Ícone de sucesso
        icon = tk.Label(
            card,
            text="✓",
            font=("Segoe UI", 72, "bold"),
            bg=self.cor_card,
            fg=self.cor_sucesso
        )
        icon.pack(pady=(40, 20))
        
        # Título
        titulo = tk.Label(
            card,
            text="Instalação Concluída!",
            font=("Segoe UI", 24, "bold"),
            bg=self.cor_card,
            fg=self.cor_texto
        )
        titulo.pack(pady=(0, 10))
        
        # Mensagem
        msg = tk.Label(
            card,
            text=f"O sistema foi instalado com sucesso em:\n{self.pasta_instalacao.get()}",
            font=("Segoe UI", 11),
            bg=self.cor_card,
            fg=self.cor_texto_suave,
            justify="center"
        )
        msg.pack(pady=(0, 30))
        
        # Informações
        info_frame = tk.Frame(card, bg="#F8F8F8", relief="flat")
        info_frame.pack(fill="x", padx=40, pady=20)
        
        info_text = tk.Label(
            info_frame,
            text="💡 Para iniciar o sistema, execute o arquivo 'executar_sistema.bat'\n"
                 "ou use o atalho criado na área de trabalho.",
            font=("Segoe UI", 10),
            bg="#F8F8F8",
            fg=self.cor_texto,
            justify="center"
        )
        info_text.pack(pady=15, padx=15)
        
        # Atualizar botões
        self.btn_avancar.pack_forget()
        self.btn_voltar.pack_forget()
        self.btn_cancelar.pack_forget()
        
        # Botão Concluir
        btn_concluir = self.criar_botao_moderno(
            self.btn_container,
            text="Concluir",
            command=self.root.quit,
            primary=True
        )
        btn_concluir.pack(side="right")
        
    def limpar_conteudo(self):
        """Limpa o conteúdo atual"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def avancar_etapa(self):
        """Avança para próxima etapa"""
        self.etapa_atual += 1
        
        if self.etapa_atual == 1:
            self.mostrar_tela_configuracao()
        elif self.etapa_atual == 2:
            if self.validar_configuracoes():
                self.mostrar_tela_instalacao()
            else:
                self.etapa_atual -= 1
                
    def voltar_etapa(self):
        """Volta para etapa anterior"""
        self.etapa_atual -= 1
        
        if self.etapa_atual == 0:
            self.mostrar_tela_bem_vindo()
        elif self.etapa_atual == 1:
            self.mostrar_tela_configuracao()
            
    def escolher_pasta(self):
        """Permite escolher a pasta de instalação"""
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_instalacao.set(pasta)
            
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.root.update()
            
        # Atualizar status
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message.split('\n')[0])
            
    def atualizar_progresso(self, porcentagem):
        """Atualiza a barra de progresso"""
        if hasattr(self, 'progress_bar'):
            largura = int((self.content_frame.winfo_width() - 100) * (porcentagem / 100))
            self.progress_bar.config(width=largura)
            self.root.update()
    
    def _verificar_python_instalado(self):
        """Verifica se Python está instalado"""
        comandos = ["python", "python3", "py"]
        
        for comando in comandos:
            try:
                result = subprocess.run([comando, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    versao = result.stdout.strip().replace("Python ", "")
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
        
    def validar_configuracoes(self):
        """Valida as configurações antes da instalação"""
        if not self.pasta_instalacao.get():
            messagebox.showerror("Erro", "Selecione uma pasta de instalação")
            return False
            
        pasta_destino = Path(self.pasta_instalacao.get())
        
        if pasta_destino.exists() and any(pasta_destino.iterdir()):
            resposta = messagebox.askyesnocancel(
                "Pasta já existe",
                f"A pasta já contém arquivos. Deseja limpar e continuar?",
                icon='warning'
            )
            
            if resposta is None:
                return False
            elif resposta:
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], 
                                 capture_output=True, timeout=10)
                    time.sleep(2)
                    shutil.rmtree(pasta_destino)
                    time.sleep(1)
                    pasta_destino.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível limpar a pasta: {e}")
                    return False
        
        try:
            pasta_destino.mkdir(parents=True, exist_ok=True)
            test_file = pasta_destino / ".test_permission"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar pasta: {e}")
            return False
            
        return True
        
    def executar_instalacao(self):
        """Executa o processo de instalação (simplificado para demo)"""
        try:
            etapas = [
                ("Verificando ambiente...", 10),
                ("Copiando arquivos...", 30),
                ("Criando ambiente virtual...", 50),
                ("Instalando dependências...", 70),
                ("Configurando sistema...", 85),
                ("Criando atalhos...", 95),
                ("Finalizando...", 100)
            ]
            
            for mensagem, progresso in etapas:
                self.log_message(f"✓ {mensagem}")
                self.atualizar_progresso(progresso)
                time.sleep(1)  # Simular trabalho
            
            self.log_message("\n✅ Instalação concluída com sucesso!")
            time.sleep(1)
            
            # Mostrar tela de conclusão
            self.root.after(0, self.mostrar_tela_concluido)
            
        except Exception as e:
            self.log_message(f"\n❌ Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro durante instalação: {e}")

def main():
    """Função principal"""
    app = InstaladorModerno()
    app.root.mainloop()

if __name__ == "__main__":
    main()
