#!/usr/bin/env python3
"""
Script para investigar os filtros que podem estar causando o problema
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalizar(nome):
    if not nome:
        return ''
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')

def testar_filtros():
    """Testar diferentes cenários de filtros"""
    
    # Buscar dados básicos
    projetos = supabase.table("projetos").select("*").execute().data
    projeto_ids = [projeto['id'] for projeto in projetos]
    
    print(f"📋 Total de projetos: {len(projetos)}")
    print(f"📋 IDs dos projetos: {projeto_ids}")
    
    # Identificar IDs dos projetos problemáticos
    projetos_problema = {}
    for projeto in projetos:
        nome = projeto.get('nome', '')
        if nome in ['2509 - WORLD SET', '2606 - WORLD JUN']:
            projetos_problema[nome] = projeto.get('id')
    
    print(f"\n🎯 Projetos problemáticos:")
    for nome, id_proj in projetos_problema.items():
        print(f"  {nome}: {id_proj}")
    
    # TESTE 1: Buscar TODAS as tarefas sem filtro
    print(f"\n🔍 TESTE 1: Buscar todas as tarefas SEM filtros")
    tarefas_sem_filtro = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute().data or []
    print(f"Total de tarefas encontradas: {len(tarefas_sem_filtro)}")
    
    for nome, id_proj in projetos_problema.items():
        tarefas_do_projeto = [t for t in tarefas_sem_filtro if t.get('projeto_id') == id_proj]
        lancamentos = [t for t in tarefas_do_projeto if normalizar(t.get('nome', '')) == 'lancamento']
        print(f"  {nome}: {len(tarefas_do_projeto)} tarefas, {len(lancamentos)} lançamentos")
    
    # TESTE 2: Simular busca COM filtro de status possível
    print(f"\n🔍 TESTE 2: Testando possíveis filtros de status")
    
    # Verificar que status existem nas tarefas
    todos_status = set()
    for t in tarefas_sem_filtro:
        status = t.get('status')
        if status:
            todos_status.add(status)
    
    print(f"Status encontrados: {sorted(todos_status)}")
    
    # Testar filtro comum que pode estar sendo aplicado
    status_comuns = ['pendente', 'em andamento', 'concluido', 'concluída']
    
    for status_teste in status_comuns:
        print(f"\n  Testando filtro de status: '{status_teste}'")
        tarefas_filtradas = []
        
        # Simular o mesmo processo da aplicação
        for projeto_id in projeto_ids:
            tarefas_projeto = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute()
            if hasattr(tarefas_projeto, 'data') and tarefas_projeto.data:
                tarefas_filtradas.extend(tarefas_projeto.data)
        
        print(f"    Total tarefas ANTES do filtro: {len(tarefas_filtradas)}")
        
        # Aplicar filtro de status (simulando a lógica da aplicação)
        tarefas_com_filtro = [
            t for t in tarefas_filtradas
            if t.get('status') == status_teste or normalizar(t.get('nome', '')) == 'lancamento'
        ]
        
        print(f"    Total tarefas DEPOIS do filtro: {len(tarefas_com_filtro)}")
        
        # Verificar projetos problemáticos
        for nome, id_proj in projetos_problema.items():
            tarefas_do_projeto = [t for t in tarefas_com_filtro if t.get('projeto_id') == id_proj]
            lancamentos = [t for t in tarefas_do_projeto if normalizar(t.get('nome', '')) == 'lancamento']
            print(f"    {nome}: {len(tarefas_do_projeto)} tarefas, {len(lancamentos)} lançamentos")
            
            if len(tarefas_do_projeto) < 15:  # Se tem poucas tarefas, mostrar detalhes
                print(f"    Tarefas encontradas:")
                for t in tarefas_do_projeto:
                    print(f"      - {t.get('nome', '')} | Status: {t.get('status', '')}")
    
    # TESTE 3: Verificar se há filtros de coleção
    print(f"\n🔍 TESTE 3: Verificar coleções das tarefas")
    todas_colecoes = set()
    for t in tarefas_sem_filtro:
        colecao = t.get('colecao')
        if colecao:
            todas_colecoes.add(colecao)
    
    print(f"Coleções encontradas: {sorted(todas_colecoes)}")
    
    # Verificar se as tarefas de lançamento têm coleção específica
    for nome, id_proj in projetos_problema.items():
        print(f"\n  Tarefas de lançamento do {nome}:")
        tarefas_do_projeto = [t for t in tarefas_sem_filtro if t.get('projeto_id') == id_proj]
        lancamentos = [t for t in tarefas_do_projeto if normalizar(t.get('nome', '')) == 'lancamento']
        for l in lancamentos:
            print(f"    - Nome: {l.get('nome', '')}")
            print(f"      Status: {l.get('status', '')}")
            print(f"      Coleção: {l.get('colecao', '')}")
            print(f"      Data: {l.get('data_inicio') or l.get('data_inicio_tarefa')}")

if __name__ == "__main__":
    testar_filtros()