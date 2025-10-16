from datetime import date, timedelta
import numpy as np

def dias_uteis_entre_datas(data_inicio, data_fim):
    if not data_inicio or not data_fim:
        return 0
    # Aceita string 'YYYY-MM-DD' ou objeto date
    if isinstance(data_inicio, str):
        data_inicio = date.fromisoformat(data_inicio)
    if isinstance(data_fim, str):
        data_fim = date.fromisoformat(data_fim)
    # Gera array de datas entre início e fim
    dias = np.busday_count(data_inicio, data_fim + timedelta(days=1))
    return dias
