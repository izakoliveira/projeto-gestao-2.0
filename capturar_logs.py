import requests
import time

time.sleep(2)
try:
    r = requests.get('http://localhost:5000/projetos', allow_redirects=False, timeout=10)
    print(f"Status: {r.status_code}")
except:
    print("Erro de conexão")