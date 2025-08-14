from datetime import datetime

def validar_projeto(nome, data_inicio, data_fim):
    """
    Valida os dados de um projeto.
    
    Args:
        nome (str): Nome do projeto
        data_inicio (str): Data de início no formato YYYY-MM-DD
        data_fim (str): Data de fim no formato YYYY-MM-DD
    
    Returns:
        str or None: Mensagem de erro ou None se válido
    """
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

def normaliza_opcional(valor):
    """
    Normaliza valores opcionais, retornando None se vazio.
    
    Args:
        valor: Valor a ser normalizado
    
    Returns:
        Valor normalizado ou None
    """
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor.strip() if valor.strip() else None
    return valor

def is_mobile_device(user_agent):
    """
    Detecta se o dispositivo é mobile baseado no User-Agent.
    
    Args:
        user_agent (str): User-Agent string
    
    Returns:
        bool: True se for mobile, False caso contrário
    """
    if not user_agent:
        return False
    
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'blackberry', 'windows phone']
    user_agent_lower = user_agent.lower()
    
    return any(keyword in user_agent_lower for keyword in mobile_keywords)

def verificar_tarefa_atrasada(tarefa):
    """
    Verifica se uma tarefa está atrasada usando ambas as lógicas:
<<<<<<< HEAD
    - Lógica 1: Tarefa pendente com data de início passada (excluindo hoje)
    - Lógica 2: Tarefa não concluída com data de fim passada (excluindo hoje)
=======
    - Lógica 1: Tarefa pendente com data de início passada
    - Lógica 2: Tarefa não concluída com data de fim passada
>>>>>>> 698d000a8693e7182ddc0758b886033e51767c3f
    
    Args:
        tarefa (dict): Dicionário com dados da tarefa
    
    Returns:
        bool: True se a tarefa está atrasada, False caso contrário
    """
    status = tarefa.get('status', '').lower()
    data_fim = tarefa.get('data_fim') or tarefa.get('data_fim_tarefa')
    data_inicio = tarefa.get('data_inicio') or tarefa.get('data_inicio_tarefa')
<<<<<<< HEAD
    
    # Usar apenas a data (sem hora) para comparação
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # LÓGICA 1: Tarefa pendente com data de início passada (excluindo hoje)
    if status == 'pendente' and data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio.split('T')[0], '%Y-%m-%d')
            if data_inicio_obj < hoje:  # Apenas datas ANTERIORES a hoje
=======
    hoje = datetime.now()
    
    # LÓGICA 1: Tarefa pendente com data de início passada
    if status == 'pendente' and data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio.split('T')[0], '%Y-%m-%d')
            if data_inicio_obj < hoje:
>>>>>>> 698d000a8693e7182ddc0758b886033e51767c3f
                return True
        except:
            pass
    
<<<<<<< HEAD
    # LÓGICA 2: Tarefa não concluída com data de fim passada (excluindo hoje)
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim.split('T')[0], '%Y-%m-%d')
            if data_fim_obj < hoje and status not in ['concluída', 'concluida']:  # Apenas datas ANTERIORES a hoje
=======
    # LÓGICA 2: Tarefa não concluída com data de fim passada
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim.split('T')[0], '%Y-%m-%d')
            if data_fim_obj < hoje and status not in ['concluída', 'concluida']:
>>>>>>> 698d000a8693e7182ddc0758b886033e51767c3f
                return True
        except:
            pass
    
    return False

def contar_tarefas_atrasadas(tarefas):
    """
    Conta quantas tarefas estão atrasadas em uma lista.
    
    Args:
        tarefas (list): Lista de dicionários com dados das tarefas
    
    Returns:
        int: Número de tarefas atrasadas
    """
    return sum(1 for tarefa in tarefas if verificar_tarefa_atrasada(tarefa)) 