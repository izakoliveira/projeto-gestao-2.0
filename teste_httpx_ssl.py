import httpx

try:
    response = httpx.get("https://www.google.com", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:100]}")
except Exception as e:
    print(f"Erro ao acessar https://www.google.com: {e}")
