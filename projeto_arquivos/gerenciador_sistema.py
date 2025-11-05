"""
Gerenciador do Sistema de Gestão de Projetos
Inicia o servidor Flask e monitora o navegador, encerrando quando o navegador é fechado
"""
import subprocess
import time
import psutil
import sys
import os
from pathlib import Path

def get_browser_processes():
    """Retorna lista de processos de navegadores conhecidos"""
    browser_names = [
        'chrome.exe', 'msedge.exe', 'firefox.exe', 
        'opera.exe', 'brave.exe', 'iexplore.exe'
    ]
    browsers = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in browser_names:
                # Verificar se está acessando localhost:5000
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('localhost:5000' in str(arg) for arg in cmdline):
                    browsers.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return browsers

def is_server_running():
    """Verifica se o servidor Flask já está rodando"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('app_producao.py' in str(arg) for arg in cmdline):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

def start_server():
    """Inicia o servidor Flask"""
    print("Iniciando servidor Flask...")
    
    # Ativar ambiente virtual e iniciar servidor
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("Erro: Ambiente virtual não encontrado!")
        return None
    
    # Iniciar servidor em processo separado
    server_process = subprocess.Popen(
        [str(venv_python), "app_producao.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    # Aguardar servidor iniciar
    print("Aguardando servidor iniciar...")
    time.sleep(4)
    
    return server_process

def open_browser():
    """Abre o navegador na página de login"""
    print("Abrindo navegador...")
    subprocess.Popen(
        ['cmd', '/c', 'start', 'http://localhost:5000/login'],
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(2)

def monitor_browser(server_process):
    """Monitora se há navegadores acessando o sistema"""
    print("Monitorando navegador...")
    last_browser_time = time.time()
    timeout = 60  # segundos sem navegador antes de encerrar
    
    while True:
        try:
            # Verificar se servidor ainda está rodando
            if server_process.poll() is not None:
                print("Servidor encerrado.")
                break
            
            # Procurar por navegadores acessando localhost:5000
            browsers = get_browser_processes()
            
            if browsers:
                # Navegador ativo, resetar timer
                last_browser_time = time.time()
            else:
                # Sem navegador, verificar timeout
                elapsed = time.time() - last_browser_time
                if elapsed > timeout:
                    print(f"Nenhum navegador ativo há {timeout} segundos. Encerrando servidor...")
                    break
            
            # Aguardar antes de verificar novamente
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"Erro no monitoramento: {e}")
            time.sleep(5)
    
    # Encerrar servidor
    print("Encerrando servidor Flask...")
    try:
        server_process.terminate()
        server_process.wait(timeout=5)
    except:
        server_process.kill()
    
    print("Sistema encerrado.")

def main():
    """Função principal"""
    # Mudar para diretório do script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Verificar se servidor já está rodando
    existing_server = is_server_running()
    
    if existing_server:
        print("Servidor já está rodando. Apenas abrindo navegador...")
        open_browser()
    else:
        # Iniciar novo servidor
        server_process = start_server()
        
        if server_process:
            # Abrir navegador
            open_browser()
            
            # Monitorar navegador e encerrar quando necessário
            monitor_browser(server_process)
        else:
            print("Erro ao iniciar servidor!")
            sys.exit(1)

if __name__ == "__main__":
    main()
