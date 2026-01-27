from config.database import supabase

try:
    # Verificar se o projeto existe
    projeto_resp = supabase.table('projetos').select('id, nome').eq('nome', '2702 - WORLD FEV').execute()
    if projeto_resp.data:
        projeto = projeto_resp.data[0]
        print(f'Projeto encontrado: ID={projeto["id"]}, Nome="{projeto["nome"]}"')

        # Contar tarefas do projeto
        tarefas_resp = supabase.table('tarefas').select('id, colecao').eq('projeto_id', projeto['id']).execute()
        tarefas = tarefas_resp.data if tarefas_resp.data else []
        print(f'Total de tarefas no projeto: {len(tarefas)}')

        # Mostrar coleção atual das primeiras 5 tarefas
        for i, tarefa in enumerate(tarefas[:5]):
            colecao_atual = tarefa.get('colecao', 'Nenhuma')
            print(f'Tarefa {i+1}: ID={tarefa["id"]}, Coleção atual="{colecao_atual}"')

        if len(tarefas) > 5:
            print(f'... e mais {len(tarefas) - 5} tarefas')

        # Agora executar a atualização
        print('\nExecutando atualização da coleção...')

        # Atualizar todas as tarefas para ter a coleção "2702 - WORLD FEV"
        update_resp = supabase.table('tarefas').update({
            'colecao': '2702 - WORLD FEV'
        }).eq('projeto_id', projeto['id']).execute()

        print(f'Atualização concluída! {len(update_resp.data) if update_resp.data else 0} tarefas atualizadas.')

        # Verificar resultado
        tarefas_atualizadas_resp = supabase.table('tarefas').select('id, colecao').eq('projeto_id', projeto['id']).eq('colecao', '2702 - WORLD FEV').execute()
        tarefas_atualizadas = tarefas_atualizadas_resp.data if tarefas_atualizadas_resp.data else []
        print(f'Verificação: {len(tarefas_atualizadas)} tarefas agora têm a coleção "2702 - WORLD FEV"')

    else:
        print('Projeto "2702 - WORLD FEV" não encontrado!')

except Exception as e:
    print(f'Erro: {e}')