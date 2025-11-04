import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def testar_selecao_multiplos_projetos():
    """Testa a seleção de múltiplos projetos na interface web"""
    
    print("🧪 Testando seleção de múltiplos projetos na interface...")
    
    # Configurar Chrome para execução silenciosa
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem abrir janela
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navegar para a página de projetos
        print("📱 Acessando http://localhost:5000/projetos...")
        driver.get("http://localhost:5000/projetos")
        
        # Aguardar a página carregar
        wait = WebDriverWait(driver, 10)
        
        # Verificar se a página carregou
        print("⏳ Aguardando página carregar...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Buscar o select de nomes (pode ser nome-desktop ou nome-mobile)
        nome_select = None
        try:
            nome_select = driver.find_element(By.ID, "nome-desktop")
            print("✅ Encontrou nome-desktop")
        except:
            try:
                nome_select = driver.find_element(By.ID, "nome-mobile")  
                print("✅ Encontrou nome-mobile")
            except:
                print("❌ Não encontrou select de nomes")
                return
        
        if nome_select:
            # Verificar se há opções no select
            options = nome_select.find_elements(By.TAG_NAME, "option")
            print(f"📋 Encontradas {len(options)} opções no select")
            
            if len(options) > 1:
                # Selecionar os 2 primeiros projetos (ignorar primeira opção se for "Todos")
                select_obj = Select(nome_select)
                opcoes_projetos = [opt for opt in options if opt.get_attribute("value") != ""]
                
                if len(opcoes_projetos) >= 2:
                    print(f"✅ Selecionando 2 projetos...")
                    
                    # Selecionar múltiplas opções
                    select_obj.select_by_index(1)  # Primeiro projeto
                    select_obj.select_by_index(2)  # Segundo projeto
                    
                    print("📋 Projetos selecionados:")
                    selected = select_obj.all_selected_options
                    for opt in selected:
                        print(f"   - {opt.text}")
                    
                    # Executar JavaScript para verificar window.projetosData
                    projetos_data = driver.execute_script("return window.projetosData;")
                    print(f"📊 window.projetosData length: {len(projetos_data) if projetos_data else 0}")
                    
                    if projetos_data and len(projetos_data) > 0:
                        print("📊 Primeira entrada:")
                        primeiro = projetos_data[0]
                        print(f"   Nome: {primeiro.get('nome', 'Sem nome')}")
                        print(f"   ID: {primeiro.get('id', 'Sem ID')}")
                    
                    # Simular clique no botão de exportar Excel
                    try:
                        btn_excel = driver.find_element(By.ID, "btn-exportar-excel")
                        print("🔍 Simulando clique no botão Excel...")
                        driver.execute_script("arguments[0].click();", btn_excel)
                        
                        # Aguardar um pouco para ver os logs no console
                        time.sleep(2)
                        
                        # Capturar logs do console
                        logs = driver.get_log('browser')
                        print("📝 Logs do console:")
                        for log in logs:
                            if 'GANTT EXCEL DEBUG' in log['message']:
                                print(f"   {log['message']}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao clicar no botão: {e}")
                else:
                    print("❌ Não há projetos suficientes para testar")
            else:
                print("❌ Nenhuma opção encontrada no select")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000/projetos", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
            testar_selecao_multiplos_projetos()
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
    except:
        print("❌ Servidor não está rodando em localhost:5000")