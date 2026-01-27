
from utils.dias_uteis import obter_feriados_banco
import requests

# Simular o que acontece no template
feriados_manuais = obter_feriados_banco()

# Buscar feriados da API BrasilAPI (com nomes)
def obter_feriados_api_completo(ano):
    url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()  # lista de dicts com 'date' e 'name'
        else:
            return []
    except Exception as e:
        print(f"Erro ao buscar feriados API: {e}")
        return []

feriados_api_completo = obter_feriados_api_completo(2026)
feriados_api_dict = {f['date']: f['name'] for f in feriados_api_completo}

print("Testando função isFeriado (com nome real da API):")
print(f"feriados_manuais: {type(feriados_manuais)} = {feriados_manuais}")
print(f"feriados_api_dict: {type(feriados_api_dict)} = {list(feriados_api_dict.items())[:5]}...")

def isFeriado(val):
    # Checar feriados manuais do banco
    if feriados_manuais and feriados_manuais.get(val):
        return feriados_manuais[val]
    # Checar feriados nacionais da API (com nome)
    if feriados_api_dict and val in feriados_api_dict:
        return feriados_api_dict[val]
    return None

# Testar algumas datas
test_dates = ['2026-12-25', '2026-12-31', '2026-01-01', '2026-11-20', '2026-05-01']
for date in test_dates:
    result = isFeriado(date)
    print(f"isFeriado('{date}') = {result}")