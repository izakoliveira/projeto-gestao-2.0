#!/usr/bin/env python3
"""
Script para testar o processamento de dados exatamente como na aplicação
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

def testar_processamento_aplicacao():
    """Testar o mesmo processamento que a aplicação faz"""
    
    print("🔄 Simulando o processamento exato da aplicação...")
    
    # Buscar projetos (simulando código da aplicação)
    query = supabase.table("projetos").select("*")
    projetos = query.execute().data
    
    # Buscar tarefas 
    projeto_ids = [projeto['id'] for projeto in projetos]
    print(f"[DEBUG] IDs dos projetos encontrados: {projeto_ids}")
    
    # Buscar tarefas dos projetos específicos (simulando código da aplicação)
    tarefas_filtradas = []
    if projeto_ids:
        try:
            # Consulta sem filtro de status/exclusão para garantir que todas as tarefas venham
            tarefas_filtradas = supabase.table("tarefas").select("*").in_("projeto_id", projeto_ids).execute().data or []
        except Exception as e:
            print(f"Erro ao buscar tarefas dos projetos: {e}")
            tarefas_filtradas = []
    
    # Associar tarefas a cada projeto (simulando código da aplicação)
    for projeto in projetos:
        projeto['tarefas'] = [t for t in tarefas_filtradas if t.get('projeto_id') == projeto['id']]
    
    print(f"\n📋 Total de projetos: {len(projetos)}")
    print(f"📋 Total de tarefas filtradas: {len(tarefas_filtradas)}")
    
    # Aplicar a função data_inicio_lancamento exatamente como na aplicação
    def data_inicio_lancamento(projeto):
        tarefas = projeto.get('tarefas', [])
        print(f"\n[ORDENAÇÃO] Projeto: {projeto.get('nome', 'Sem nome')}")
        print(f"[ORDENAÇÃO] Total de tarefas no projeto: {len(tarefas)}")
        
        for t in tarefas:
            print(f"[ORDENAÇÃO] Tarefa: '{t.get('nome', '')}' | Normalizada: '{normalizar(t.get('nome', ''))}'")
        
        tarefas_lancamento = [t for t in tarefas if normalizar(t.get('nome', '')) == 'lancamento']
        print(f"[ORDENAÇÃO] Tarefas consideradas para lançamento: {[t.get('nome') for t in tarefas_lancamento]}")
        
        datas = [t.get('data_inicio') or t.get('data_inicio_tarefa') for t in tarefas_lancamento if (t.get('data_inicio') or t.get('data_inicio_tarefa'))]
        datas_validas = [d for d in datas if d]
        print(f"[ORDENAÇÃO] Datas consideradas: {datas_validas}")
        
        if datas_validas:
            print(f"[ORDENAÇÃO] ✅ Data usada para ordenação: {min(datas_validas)}")
            return min(datas_validas)
        
        # Só executa as mensagens de "sem data" quando realmente não há data
        if not tarefas_lancamento:
            print(f"[ORDENAÇÃO] ❌ Projeto SEM tarefa de lançamento: {projeto.get('nome', 'Sem nome')}")
            print(f"[ORDENAÇÃO] Nomes normalizados das tarefas:")
            for t in tarefas:
                print(f"  - '{t.get('nome', '')}' | Normalizada: '{normalizar(t.get('nome', ''))}'")
        else:
            # Tem tarefas de lançamento, mas sem data válida
            print(f"[ORDENAÇÃO] ❌ Projeto com tarefa de lançamento MAS sem data válida: {projeto.get('nome', 'Sem nome')}")
            for t in tarefas_lancamento:
                print(f"  - Tarefa lançamento: '{t.get('nome', '')}' | data_inicio: {t.get('data_inicio')} | data_inicio_tarefa: {t.get('data_inicio_tarefa')}")
        
        print(f"[ORDENAÇÃO] ⚠️  Sem data de lançamento válida, usando padrão '9999-12-31'")
        return '9999-12-31'
    
    print("\n" + "="*80)
    print("🔍 TESTANDO FUNÇÃO data_inicio_lancamento PARA CADA PROJETO")
    print("="*80)
    
    projetos_com_problema = []
    for projeto in projetos:
        resultado = data_inicio_lancamento(projeto)
        if resultado == '9999-12-31':
            projetos_com_problema.append(projeto.get('nome', 'Sem nome'))
    
    print("\n" + "="*80)
    print("📊 RESUMO DO TESTE")
    print("="*80)
    
    if projetos_com_problema:
        print(f"❌ Projetos que retornaram '9999-12-31': {len(projetos_com_problema)}")
        for i, nome in enumerate(projetos_com_problema, 1):
            print(f"{i}. {nome}")
    else:
        print("✅ Todos os projetos têm data de lançamento válida!")

if __name__ == "__main__":
    testar_processamento_aplicacao()