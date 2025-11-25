import sys
sys.path.append('.')
from config.database import supabase
from datetime import datetime

# Buscar alguns projetos e suas tarefas
projetos = supabase.table('projetos').select('id, nome').limit(5).execute()

for p in projetos.data:
    tarefas = supabase.table('tarefas').select('nome, status, data_fim').eq('projeto_id', p['id']).execute()
    
    print(f"\nProjeto: {p['nome']}")
    print(f"Tarefas: {len(tarefas.data)}")
    
    if not tarefas.data:
        print("Status: Normal (sem tarefas)")
        continue
    
    # Funções auxiliares
    def is_concluida(status):
        s = (status or '').strip().lower()
        return s in ['concluido', 'concluida', 'concluído', 'concluída']
    
    def is_em_progresso(status):
        s = (status or '').strip().lower()
        return s in ['em progresso', 'em_progresso', 'progresso', 'pendente']
    
    def is_atrasada(tarefa):
        status = tarefa.get('status', '')
        if is_concluida(status):
            return False
        data_fim = tarefa.get('data_fim')
        if data_fim:
            try:
                data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
                return data_fim_dt < datetime.now(data_fim_dt.tzinfo)
            except:
                return False
        return False
    
    # Verificar status
    todas_concluidas = all(is_concluida(t.get('status', '')) for t in tarefas.data)
    alguma_em_progresso = any(is_em_progresso(t.get('status', '')) for t in tarefas.data)
    alguma_atrasada = any(is_atrasada(t) for t in tarefas.data)
    
    print(f"Todas concluídas: {todas_concluidas}")
    print(f"Alguma em progresso: {alguma_em_progresso}")
    print(f"Alguma atrasada: {alguma_atrasada}")
    
    for t in tarefas.data:
        print(f"  - {t['nome']}: {t['status']} (concluida={is_concluida(t['status'])}, em_progresso={is_em_progresso(t['status'])}, atrasada={is_atrasada(t)})")
    
    if todas_concluidas:
        status_final = 'Concluído'
    elif alguma_atrasada:
        status_final = 'Atrasado'
    elif alguma_em_progresso:
        status_final = 'Em Progresso'
    else:
        status_final = 'Normal'
    
    print(f"Status final: {status_final}")