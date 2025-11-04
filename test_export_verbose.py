import requests
import json
import time

# URL da aplicação
url = "http://localhost:5000/relatorio/gantt_excel"

# Dados para teste - usando IDs reais dos projetos dos logs
data = {
    "projeto_ids": ["8b4cd282-203c-4c2f-a13e-1e0d6b0745dc", "c658bec1-0196-4ad0-b1d9-19b418419223"]
}

headers = {
    "Content-Type": "application/json"
}

print("Fazendo requisição para exportar Excel...")
print(f"URL: {url}")
print(f"Dados: {data}")

try:
    print("Fazendo conexão...")
    response = requests.post(url, json=data, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        # Salvar o arquivo
        with open("test_gantt_export.xlsx", "wb") as f:
            f.write(response.content)
        print("Arquivo Excel salvo como 'test_gantt_export.xlsx'")
        print(f"Tamanho do arquivo: {len(response.content)} bytes")
    else:
        print(f"Erro HTTP {response.status_code}")
        print(f"Headers de resposta: {response.headers}")
        print(f"Conteúdo da resposta: {response.text[:1000]}")
        
except requests.exceptions.ConnectionError as e:
    print(f"Erro de conexão: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout na requisição: {e}")
except Exception as e:
    print(f"Erro na requisição: {e}")
    
print("Teste finalizado.")