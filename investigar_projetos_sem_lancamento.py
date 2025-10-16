#!/usr/bin/env python3
"""
Script para investigar projetos que não têm data de lançamento
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Verificar se as variáveis foram carregadas
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não foram encontradas no .env")
    exit(1)

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

def investigar_projetos():
    """Investigar projetos sem data de lançamento"""
    
    # Buscar todos os projetos
    try:
        projetos_response = supabase.table("projetos").select("*").execute()
        projetos = projetos_response.data or []
        print(f"📋 Total de projetos encontrados: {len(projetos)}")
    except Exception as e:
        print(f"❌ Erro ao buscar projetos: {e}")
        return
    
    # Buscar todas as tarefas
    try:
        tarefas_response = supabase.table("tarefas").select("*").execute()
        tarefas = tarefas_response.data or []
        print(f"📋 Total de tarefas encontradas: {len(tarefas)}")
    except Exception as e:
        print(f"❌ Erro ao buscar tarefas: {e}")
        return
    
    # Agrupar tarefas por projeto
    tarefas_por_projeto = {}
    for tarefa in tarefas:
        projeto_id = tarefa.get('projeto_id')
        if projeto_id:
            if projeto_id not in tarefas_por_projeto:
                tarefas_por_projeto[projeto_id] = []
            tarefas_por_projeto[projeto_id].append(tarefa)
    
    print("\n" + "="*80)
    print("🔍 INVESTIGANDO PROJETOS SEM DATA DE LANÇAMENTO")
    print("="*80)
    
    projetos_sem_lancamento = []
    projetos_com_lancamento = []
    
    for projeto in projetos:
        projeto_id = projeto.get('id')
        projeto_nome = projeto.get('nome', 'Sem nome')
        tarefas_projeto = tarefas_por_projeto.get(projeto_id, [])
        
        print(f"\n📁 Projeto: {projeto_nome} (ID: {projeto_id})")
        print(f"   Total de tarefas: {len(tarefas_projeto)}")
        
        if not tarefas_projeto:
            print("   ⚠️  Projeto sem nenhuma tarefa")
            projetos_sem_lancamento.append(projeto)
            continue
        
        # Buscar tarefas de lançamento
        tarefas_lancamento = []
        print("   📝 Tarefas do projeto:")
        for tarefa in tarefas_projeto:
            nome_tarefa = tarefa.get('nome', '')
            nome_normalizado = normalizar(nome_tarefa)
            data_inicio = tarefa.get('data_inicio')
            data_inicio_tarefa = tarefa.get('data_inicio_tarefa')
            
            print(f"      - '{nome_tarefa}' | Normalizada: '{nome_normalizado}' | data_inicio: {data_inicio} | data_inicio_tarefa: {data_inicio_tarefa}")
            
            if nome_normalizado == 'lancamento':
                tarefas_lancamento.append(tarefa)
        
        if not tarefas_lancamento:
            print("   ❌ PROJETO SEM TAREFA DE LANÇAMENTO")
            projetos_sem_lancamento.append(projeto)
        else:
            print(f"   ✅ Encontradas {len(tarefas_lancamento)} tarefa(s) de lançamento:")
            tem_data = False
            for tarefa_lanc in tarefas_lancamento:
                data_inicio = tarefa_lanc.get('data_inicio') or tarefa_lanc.get('data_inicio_tarefa')
                if data_inicio:
                    tem_data = True
                    print(f"      ✅ Lançamento com data: {data_inicio}")
                else:
                    print(f"      ❌ Lançamento SEM data: {tarefa_lanc.get('nome')}")
            
            if tem_data:
                projetos_com_lancamento.append(projeto)
            else:
                projetos_sem_lancamento.append(projeto)
    
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    print(f"✅ Projetos com data de lançamento: {len(projetos_com_lancamento)}")
    print(f"❌ Projetos sem data de lançamento: {len(projetos_sem_lancamento)}")
    
    if projetos_sem_lancamento:
        print("\n🚨 PROJETOS SEM DATA DE LANÇAMENTO:")
        for i, projeto in enumerate(projetos_sem_lancamento, 1):
            print(f"{i}. {projeto.get('nome', 'Sem nome')} (ID: {projeto.get('id')})")

if __name__ == "__main__":
    investigar_projetos()