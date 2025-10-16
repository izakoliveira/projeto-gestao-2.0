import supabase_client

# Relatório de tarefas e projetos

def listar_tarefas_por_projeto():
    supabase = supabase_client.get_client()
    tarefas = supabase.table("tarefas").select("id, nome, projeto_id").execute().data
    projetos = supabase.table("projetos").select("id, nome").execute().data
    projetos_dict = {p['id']: p['nome'] for p in projetos}
    print("--- RELATÓRIO DE TAREFAS POR PROJETO ---")
    for tarefa in tarefas:
        projeto_nome = projetos_dict.get(tarefa['projeto_id'], 'Projeto não encontrado')
        print(f"Tarefa: {tarefa['id']} | Nome: {tarefa['nome']} | Projeto: {projeto_nome} ({tarefa['projeto_id']})")

if __name__ == "__main__":
    listar_tarefas_por_projeto()
