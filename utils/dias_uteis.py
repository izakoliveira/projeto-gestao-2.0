from datetime import date, timedelta

def dias_uteis_entre_datas(data_inicio, data_fim):
    """
    Calcula dias úteis entre duas datas (segunda a sexta-feira)
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
    
    # Calcula dias úteis manualmente
    dias_uteis = 0
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        # 0 = segunda, 6 = domingo
        # Segunda a sexta são dias úteis (0-4)
        if data_atual.weekday() < 5:
            dias_uteis += 1
        data_atual += timedelta(days=1)
    
    return dias_uteis
