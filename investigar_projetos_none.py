#!/usr/bin/env python3
"""
Script para investigar especificamente os projetos que retornam None
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

def investigar_projetos_especificos():
    """Investigar projetos específicos que retornam None"""
    
    # Projetos que estão com problema
    projetos_problema = ['2509 - WORLD SET', '2606 - WORLD JUN']
    
    # Buscar todos os projetos
    try:
        projetos_response = supabase.table("projetos").select("*").execute()
        projetos = projetos_response.data or []
    except Exception as e:
        print(f"❌ Erro ao buscar projetos: {e}")
        return
    
    # Buscar todas as tarefas
    try:
        tarefas_response = supabase.table("tarefas").select("*").execute()
        tarefas = tarefas_response.data or []
    except Exception as e:
        print(f"❌ Erro ao buscar tarefas: {e}")
        return
    
    # Filtrar apenas os projetos com problema
    projetos_filtrados = [p for p in projetos if p.get('nome', '') in projetos_problema]
    
    print(f"🔍 Investigando {len(projetos_filtrados)} projetos com problema...")
    
    for projeto in projetos_filtrados:
        projeto_id = projeto.get('id')
        projeto_nome = projeto.get('nome', 'Sem nome')
        
        print(f"\n" + "="*80)
        print(f"🔎 INVESTIGANDO: {projeto_nome} (ID: {projeto_id})")
        print("="*80)
        
        # Buscar tarefas deste projeto
        tarefas_projeto = [t for t in tarefas if t.get('projeto_id') == projeto_id]
        print(f"📋 Total de tarefas encontradas: {len(tarefas_projeto)}")
        
        # Listar todas as tarefas
        print(f"\n📝 TODAS AS TAREFAS DO PROJETO:")
        for i, tarefa in enumerate(tarefas_projeto, 1):
            nome = tarefa.get('nome', '')
            nome_normalizado = normalizar(nome)
            data_inicio = tarefa.get('data_inicio')
            data_inicio_tarefa = tarefa.get('data_inicio_tarefa')
            print(f"  {i:2d}. '{nome}'")
            print(f"      Normalizada: '{nome_normalizado}'")
            print(f"      data_inicio: {data_inicio}")
            print(f"      data_inicio_tarefa: {data_inicio_tarefa}")
            print(f"      É lançamento? {'✅ SIM' if nome_normalizado == 'lancamento' else '❌ NÃO'}")
            print()
        
        # Buscar tarefas de lançamento especificamente
        print(f"🎯 BUSCANDO TAREFAS DE LANÇAMENTO:")
        tarefas_lancamento = [t for t in tarefas_projeto if normalizar(t.get('nome', '')) == 'lancamento']
        
        if not tarefas_lancamento:
            print("❌ Nenhuma tarefa de lançamento encontrada!")
            # Buscar tarefas com nomes similares
            print("\n🔍 Procurando tarefas com nomes similares a 'lançamento':")
            for tarefa in tarefas_projeto:
                nome = tarefa.get('nome', '').lower()
                if 'lanc' in nome or 'launch' in nome:
                    print(f"  - '{tarefa.get('nome', '')}' | Normalizada: '{normalizar(tarefa.get('nome', ''))}'")
        else:
            print(f"✅ Encontradas {len(tarefas_lancamento)} tarefa(s) de lançamento:")
            for tarefa in tarefas_lancamento:
                nome = tarefa.get('nome', '')
                data_inicio = tarefa.get('data_inicio')
                data_inicio_tarefa = tarefa.get('data_inicio_tarefa')
                data_final = data_inicio or data_inicio_tarefa
                print(f"  - '{nome}'")
                print(f"    data_inicio: {data_inicio}")
                print(f"    data_inicio_tarefa: {data_inicio_tarefa}")
                print(f"    Data final: {'✅ ' + str(data_final) if data_final else '❌ None'}")
        
        # Testar a função da aplicação
        print(f"\n🧪 TESTANDO FUNÇÃO data_inicio_lancamento:")
        projeto['tarefas'] = tarefas_projeto
        
        def data_inicio_lancamento(projeto):
            tarefas = projeto.get('tarefas', [])
            tarefas_lancamento = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
            
            if not tarefas_lancamento:
                print(f"  ❌ Nenhuma tarefa de lançamento encontrada")
                return None
            
            datas = [t.get('data_inicio') or t.get('data_inicio_tarefa') for t in tarefas_lancamento if (t.get('data_inicio') or t.get('data_inicio_tarefa'))]
            datas_validas = [d for d in datas if d]
            
            if datas_validas:
                data_final = min(datas_validas)
                print(f"  ✅ Data encontrada: {data_final}")
                return data_final
            else:
                print(f"  ❌ Tarefas de lançamento sem data válida")
                return None
        
        resultado = data_inicio_lancamento(projeto)
        print(f"  Resultado final: {resultado}")

if __name__ == "__main__":
    investigar_projetos_especificos()