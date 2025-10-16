#!/usr/bin/env python3
"""
Script para simular EXATAMENTE o processo da aplicação
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

def simular_aplicacao_exato():
    """Simular EXATAMENTE o que a aplicação faz"""
    
    print("🔄 Simulando EXATAMENTE o processo da aplicação...")
    
    # ===== PASSO 1: Buscar projetos (simulando código da aplicação) =====
    query = supabase.table("projetos").select("*")
    projetos = query.execute().data
    
    # ===== PASSO 2: Buscar tarefas dos projetos específicos =====
    projeto_ids = [projeto['id'] for projeto in projetos]
    print(f"[DEBUG] IDs dos projetos encontrados: {projeto_ids}")
    
    tarefas_filtradas = []
    if projeto_ids:
        try:
            # Consulta sem filtro de status/exclusão para garantir que todas as tarefas venham
            tarefas_filtradas = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute().data or []
        except Exception as e:
            print(f"Erro ao buscar tarefas dos projetos: {e}")
            tarefas_filtradas = []
    
    print(f"📋 Total de projetos: {len(projetos)}")
    print(f"📋 Total de tarefas filtradas: {len(tarefas_filtradas)}")
    
    # ===== PASSO 3: Associar tarefas aos projetos (EXATO como na aplicação) =====
    # Adicionar tarefas aos projetos
    for projeto in projetos:
        pid = projeto.get('id')
        print(f"[DEBUG] Projeto id: {pid} ({type(pid)})")
        tarefas_associadas = []
        nomes_normalizados = []
        for tarefa in tarefas_filtradas:
            tid = tarefa.get('projeto_id')
            if str(tid).strip() == str(pid).strip():
                tarefas_associadas.append(tarefa)
                nome = tarefa.get('nome', '')
                nomes_normalizados.append(nome)  # Não precisa normalizar aqui
        print(f"[DEBUG] Projeto {pid} recebeu {len(tarefas_associadas)} tarefas")
        projeto['tarefas'] = tarefas_associadas
    
    # ===== PASSO 4: Testar a função de data de lançamento =====
    print("\n" + "="*80)
    print("🔍 TESTANDO FUNÇÃO data_inicio_lancamento PARA PROJETOS ESPECÍFICOS")
    print("="*80)
    
    projetos_problema = ['2509 - WORLD SET', '2606 - WORLD JUN']
    
    def data_inicio_lancamento(projeto):
        tarefas = projeto.get('tarefas', [])
        tarefas_lancamento = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
        
        if not tarefas_lancamento:
            return None
        
        datas = [t.get('data_inicio') or t.get('data_inicio_tarefa') for t in tarefas_lancamento if (t.get('data_inicio') or t.get('data_inicio_tarefa'))]
        datas_validas = [d for d in datas if d]
        
        if datas_validas:
            return min(datas_validas)
        
        return None
    
    # ===== PASSO 5: Imprimir resultados exatamente como na aplicação =====
    print('\n[DEBUG] Ordem dos projetos antes do render:')
    for projeto in projetos:
        data_lanc = None
        for t in projeto.get('tarefas', []):
            if normalizar(t.get('nome', '')) == 'lancamento':
                data_lanc = t.get('data_inicio') or t.get('data_inicio_tarefa')
                break
        
        nome_projeto = projeto.get('nome', 'Sem nome')
        print(f"Projeto: {nome_projeto} | Data lançamento: {data_lanc}")
        
        # Investigação detalhada para projetos problemáticos
        if nome_projeto in projetos_problema:
            print(f"\n🔍 INVESTIGAÇÃO DETALHADA: {nome_projeto}")
            print(f"  ID do projeto: {projeto.get('id')}")
            print(f"  Total de tarefas associadas: {len(projeto.get('tarefas', []))}")
            
            print(f"  📝 Tarefas associadas:")
            for i, tarefa in enumerate(projeto.get('tarefas', []), 1):
                nome = tarefa.get('nome', '')
                nome_norm = normalizar(nome)
                data_inicio = tarefa.get('data_inicio')
                data_inicio_tarefa = tarefa.get('data_inicio_tarefa')
                eh_lancamento = nome_norm == 'lancamento'
                print(f"    {i:2d}. '{nome}' | Normalizada: '{nome_norm}' | É lançamento: {'✅' if eh_lancamento else '❌'}")
                if eh_lancamento:
                    print(f"        data_inicio: {data_inicio}")
                    print(f"        data_inicio_tarefa: {data_inicio_tarefa}")
                    print(f"        Data final: {data_inicio or data_inicio_tarefa}")
            
            # Testar função específica
            resultado_funcao = data_inicio_lancamento(projeto)
            print(f"  🧪 Resultado da função data_inicio_lancamento: {resultado_funcao}")
            
            # Comparar com tarefas_filtradas originais
            print(f"  🔍 Verificando tarefas_filtradas originais para este projeto:")
            projeto_id = projeto.get('id')
            tarefas_do_projeto_original = [t for t in tarefas_filtradas if str(t.get('projeto_id')).strip() == str(projeto_id).strip()]
            print(f"    Total de tarefas encontradas em tarefas_filtradas: {len(tarefas_do_projeto_original)}")
            
            for tarefa in tarefas_do_projeto_original:
                nome = tarefa.get('nome', '')
                if normalizar(nome) == 'lancamento':
                    print(f"    ✅ Tarefa lançamento encontrada em tarefas_filtradas:")
                    print(f"      Nome: '{nome}'")
                    print(f"      projeto_id: {tarefa.get('projeto_id')}")
                    print(f"      data_inicio: {tarefa.get('data_inicio')}")
                    print(f"      data_inicio_tarefa: {tarefa.get('data_inicio_tarefa')}")
            
            print()

if __name__ == "__main__":
    simular_aplicacao_exato()