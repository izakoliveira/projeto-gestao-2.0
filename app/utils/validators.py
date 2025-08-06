"""
Validação de dados de entrada
=============================
"""

from datetime import datetime

def validar_projeto(nome, data_inicio, data_fim):
    """Valida os dados de um projeto"""
    if not nome:
        return "O nome do projeto é obrigatório!"
    
    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        if data_inicio > data_fim:
            return "A data de início não pode ser posterior à data de término."
    except ValueError:
        return "As datas devem estar no formato AAAA-MM-DD."

    return None  # Se tudo estiver ok

def validar_tarefa(nome, duracao, data_inicio, data_fim):
    """Valida os dados de uma tarefa"""
    if not nome:
        return "O nome da tarefa é obrigatório!"
    
    if duracao is None or duracao <= 0:
        return "A duração deve ser maior que zero."
    
    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        if data_inicio > data_fim:
            return "A data de início não pode ser posterior à data de término."
    except ValueError:
        return "As datas devem estar no formato AAAA-MM-DD."

    return None

def validar_email(email):
    """Valida formato de email"""
    if not email or '@' not in email:
        return "Email inválido."
    return None

def validar_senha(senha):
    """Valida força da senha"""
    if not senha or len(senha) < 6:
        return "A senha deve ter pelo menos 6 caracteres."
    return None

def normaliza_opcional(valor):
    """Normaliza valores opcionais"""
    if valor == '' or valor is None:
        return None
    return valor 