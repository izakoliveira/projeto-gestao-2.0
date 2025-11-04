import requests
import json

# URL da aplicação
url = "http://localhost:5000/relatorio/gantt_excel"

# Dados para teste
data = {
    "projeto_ids": ["1", "2"]
}

headers = {
    "Content-Type": "application/json"
}

print("Fazendo requisição para exportar Excel...")
print(f"URL: {url}")
print(f"Dados: {data}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        # Salvar o arquivo
        with open("test_gantt_export.xlsx", "wb") as f:
            f.write(response.content)
        print("Arquivo Excel salvo como 'test_gantt_export.xlsx'")
    else:
        print(f"Erro: {response.text}")
        
except Exception as e:
    print(f"Erro na requisição: {e}")