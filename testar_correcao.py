#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalizar(nome):
    if not nome:
        return ''
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')

def normaliza_opcional(valor):
    """Função original que estava causando o problema"""
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor.strip() if valor.strip() else None
    return valor

# Buscar projetos problemáticos
projetos = supabase.table("projetos").select("*").execute().data
projetos_problema = {}
for projeto in projetos:
    nome = projeto.get('nome', '')
    if nome in ['2509 - WORLD SET', '2606 - WORLD JUN']:
        projetos_problema[nome] = projeto.get('id')

print("🔧 TESTANDO CORREÇÃO DO FILTRO")
print("="*50)

for nome, id_proj in projetos_problema.items():
    print(f"\n📁 {nome}:")
    
    # Buscar todas as tarefas
    tarefas = supabase.table("tarefas").select("*").eq("projeto_id", id_proj).execute().data
    print(f"  Total tarefas no banco: {len(tarefas)}")
    
    # Simular diferentes filtros de status
    status_para_testar = ['em andamento', 'ativo', 'em progresso']
    
    for status_filtro in status_para_testar:
        print(f"\n  🔍 Testando filtro de status: '{status_filtro}'")
        
        # ANTES da correção (usando normaliza_opcional - INCORRETO)
        tarefas_filtradas_antes = [
            t for t in tarefas
            if t.get('status') == status_filtro or normaliza_opcional(t.get('nome', '')) == 'lancamento'
        ]
        
        # DEPOIS da correção (usando normalizar - CORRETO)
        tarefas_filtradas_depois = [
            t for t in tarefas
            if t.get('status') == status_filtro or normalizar(t.get('nome', '')) == 'lancamento'
        ]
        
        print(f"    ANTES da correção: {len(tarefas_filtradas_antes)} tarefas")
        print(f"    DEPOIS da correção: {len(tarefas_filtradas_depois)} tarefas")
        
        # Verificar se encontrou lançamento
        lancamentos_antes = [t for t in tarefas_filtradas_antes if normalizar(t.get('nome', '')) == 'lancamento']
        lancamentos_depois = [t for t in tarefas_filtradas_depois if normalizar(t.get('nome', '')) == 'lancamento']
        
        print(f"    Lançamentos ANTES: {len(lancamentos_antes)}")
        print(f"    Lançamentos DEPOIS: {len(lancamentos_depois)}")
        
        if len(lancamentos_depois) > 0:
            print(f"    ✅ CORREÇÃO FUNCIONOU! Lançamento encontrado")
            for l in lancamentos_depois:
                print(f"      - {l.get('nome')} | Data: {l.get('data_inicio') or l.get('data_inicio_tarefa')}")
        else:
            print(f"    ❌ Ainda não encontrou lançamento")

print(f"\n🎯 RESUMO:")
print(f"O problema era que 'normaliza_opcional()' não faz normalização de texto.")
print(f"A função correta é 'normalizar()' que converte para minúsculo e remove acentos.")
print(f"Agora as tarefas de 'Lançamento' são sempre incluídas nos filtros!")