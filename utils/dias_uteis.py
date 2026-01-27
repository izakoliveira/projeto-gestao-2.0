from datetime import date, timedelta
import requests
import json
# Removido import do supabase para evitar erro na inicialização
# from config.database import supabase

# Cache global para feriados (para evitar múltiplas chamadas à API)
_cache_feriados = {}
_cache_feriados_completos = {}

def obter_feriados_banco():
    """
    Obtém todos os feriados manuais do banco de dados
    Retorna um dicionário com data como chave e nome como valor
    """
    try:
        from config.database import supabase  # Import movido para dentro da função
        result = supabase.table('feriados').select('data, nome').execute()
        feriados_db = {item['data']: item['nome'] for item in result.data}
        return feriados_db
    except Exception as e:
        print(f"⚠️ Erro ao obter feriados do banco: {str(e)}")
        return {}

def obter_feriados_ano_completos(ano):
    """
    Obtém feriados completos de um ano específico da API BrasilAPI
    Retorna lista com objetos contendo date, name, type
    Com cache para evitar múltiplas requisições
    """
    if ano in _cache_feriados_completos:
        return _cache_feriados_completos[ano]

    try:
        url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            feriados_api = response.json()
            _cache_feriados_completos[ano] = feriados_api
            return feriados_api
        else:
            print(f"⚠️ Não foi possível obter feriados de {ano}: {response.status_code}")
            _cache_feriados_completos[ano] = []
            return []

    except Exception as e:
        print(f"⚠️ Erro ao obter feriados de {ano}: {str(e)}")
        _cache_feriados_completos[ano] = []
        return []

def obter_feriados_ano(ano):
    """
    Obtém feriados de um ano específico da API BrasilAPI
    Com cache para evitar múltiplas requisições
    """
    if ano in _cache_feriados:
        return _cache_feriados[ano]

    try:
        url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            feriados_api = response.json()
            # Converter para set de datas no formato YYYY-MM-DD
            feriados = {feriado['date'] for feriado in feriados_api}
            _cache_feriados[ano] = feriados
            return feriados
        else:
            print(f"⚠️ Não foi possível obter feriados de {ano}: {response.status_code}")
            _cache_feriados[ano] = set()
            return set()

    except Exception as e:
        print(f"⚠️ Erro ao obter feriados de {ano}: {str(e)}")
        _cache_feriados[ano] = set()
        return set()

def dias_uteis_entre_datas(data_inicio, data_fim, feriados_manuais=None):
    """
    Calcula dias úteis entre duas datas (segunda a sexta-feira)
    Considera feriados nacionais brasileiros da API BrasilAPI
    e feriados manuais do banco de dados
    Versão otimizada sem numpy para produção
    """
    if not data_inicio or not data_fim:
        return 0
    
    # Aceita string 'YYYY-MM-DD' ou objeto date
    if isinstance(data_inicio, str):
        data_inicio = date.fromisoformat(data_inicio)
    if isinstance(data_fim, str):
        data_fim = date.fromisoformat(data_fim)
    
    # Se data_fim for antes de data_inicio, retorna 0
    if data_fim < data_inicio:
        return 0
    
    # Obter anos envolvidos no período
    anos = set()
    data_atual = data_inicio
    while data_atual <= data_fim:
        anos.add(data_atual.year)
        data_atual += timedelta(days=1)
    
    # Obter feriados da API
    feriados_api = set()
    for ano in anos:
        feriados_api.update(obter_feriados_ano(ano))
    
    # Obter feriados do banco de dados
    feriados_db = obter_feriados_banco()
    
    # Combinar todos os feriados (feriados_db agora é um dict, então pegamos as chaves)
    todos_feriados = feriados_api.union(set(feriados_db.keys()))
    
    # Adicionar feriados manuais passados como parâmetro (se fornecidos)
    # Calcular dias úteis
    dias_uteis = 0
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        # 0 = segunda, 6 = domingo
        # Segunda a sexta são dias úteis (0-4)
        if data_atual.weekday() < 5:
            # Verificar se é feriado
            data_str = data_atual.isoformat()
            if data_str not in todos_feriados:
                dias_uteis += 1
        data_atual += timedelta(days=1)

    return dias_uteis
