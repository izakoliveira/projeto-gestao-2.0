#!/usr/bin/env python3
"""
Script final para testar exatamente o problema do None
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Importar Supabase
try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conectado com sucesso ao Supabase!")
except Exception as e:
    print(f"❌ Erro ao conectar com Supabase: {e}")
    exit(1)

def normalizar(nome):
    """Função para normalizar nomes (mesma do código original)"""
    if not nome:
        return ''
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')

def testar_problema_final():
    """Simular exatamente a parte final que gera o None"""
    
    # Buscar dados
    query = supabase.table("projetos").select("*")
    projetos = query.execute().data
    
    projeto_ids = [projeto['id'] for projeto in projetos]
    tarefas_filtradas = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute().data or []
    
    # Associar tarefas aos projetos (exato como na aplicação)
    for projeto in projetos:
        pid = projeto.get('id')
        tarefas_associadas = []
        for tarefa in tarefas_filtradas:
            tid = tarefa.get('projeto_id')
            if str(tid).strip() == str(pid).strip():
                tarefas_associadas.append(tarefa)
        projeto['tarefas'] = tarefas_associadas
    
    # ===== TESTE EXATAMENTE COMO O CÓDIGO FINAL DA APLICAÇÃO =====
    print('\n[DEBUG] Ordem dos projetos antes do render (SIMULAÇÃO EXATA):')
    for projeto in projetos:
        data_lanc = None  # Inicializar sempre como None
        nome_projeto = projeto.get('nome', 'Sem nome')
        tarefas_lancamento_encontradas = []
        
        for t in projeto.get('tarefas', []):
            nome_tarefa = t.get('nome', '')
            nome_normalizado = normalizar(nome_tarefa)
            if nome_normalizado == 'lancamento':
                data_inicio = t.get('data_inicio')
                data_inicio_tarefa = t.get('data_inicio_tarefa')
                data_final = data_inicio or data_inicio_tarefa
                tarefas_lancamento_encontradas.append({
                    'nome': nome_tarefa,
                    'data_inicio': data_inicio,
                    'data_inicio_tarefa': data_inicio_tarefa,
                    'data_final': data_final
                })
                data_lanc = data_final
                break
        
        # Debug específico para projetos problemáticos
        if nome_projeto in ['2509 - WORLD SET', '2606 - WORLD JUN']:
            print(f"[DEBUG-PROBLEMA] Projeto: {nome_projeto}")
            print(f"[DEBUG-PROBLEMA] Total tarefas no projeto: {len(projeto.get('tarefas', []))}")
            print(f"[DEBUG-PROBLEMA] Tarefas lançamento encontradas: {len(tarefas_lancamento_encontradas)}")
            for tl in tarefas_lancamento_encontradas:
                print(f"[DEBUG-PROBLEMA]   - {tl['nome']}: data_final = {tl['data_final']}")
            
            # Verificar todas as tarefas para garantir que não há problema
            print(f"[DEBUG-PROBLEMA] TODAS as tarefas do projeto:")
            for i, t in enumerate(projeto.get('tarefas', []), 1):
                nome = t.get('nome', '')
                nome_norm = normalizar(nome)
                eh_lancamento = nome_norm == 'lancamento'
                print(f"[DEBUG-PROBLEMA]   {i:2d}. '{nome}' | Normalizada: '{nome_norm}' | É lançamento: {'✅' if eh_lancamento else '❌'}")
                if eh_lancamento:
                    print(f"[DEBUG-PROBLEMA]       data_inicio: {t.get('data_inicio')}")
                    print(f"[DEBUG-PROBLEMA]       data_inicio_tarefa: {t.get('data_inicio_tarefa')}")
        
        print(f"Projeto: {nome_projeto} | Data lançamento: {data_lanc}")
    
    print(f"\n🔍 RESUMO DOS PROJETOS PROBLEMÁTICOS:")
    for projeto in projetos:
        nome_projeto = projeto.get('nome', 'Sem nome')
        if nome_projeto in ['2509 - WORLD SET', '2606 - WORLD JUN']:
            # Testar novamente o processo de busca
            tarefas = projeto.get('tarefas', [])
            lancamento_encontrado = None
            for t in tarefas:
                if normalizar(t.get('nome', '')) == 'lancamento':
                    data = t.get('data_inicio') or t.get('data_inicio_tarefa')
                    lancamento_encontrado = data
                    break
            
            print(f"  {nome_projeto}: Lançamento = {lancamento_encontrado}")
            print(f"    Total tarefas: {len(tarefas)}")
            
            # Contar quantas têm nome 'Lançamento'
            lancamentos = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
            print(f"    Tarefas 'Lançamento': {len(lancamentos)}")
            for l in lancamentos:
                print(f"      - {l.get('nome', '')} | data: {l.get('data_inicio') or l.get('data_inicio_tarefa')}")

if __name__ == "__main__":
    testar_problema_final()