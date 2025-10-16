#!/usr/bin/env python3

"""
TESTE FINAL: Validação da correção do problema de lançamentos
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Função normalizar corrigida (que agora está sendo usada)
def normalizar(nome):
    if not nome:
        return ''
    nome = str(nome).strip().lower()
    nome = nome.replace('ã', 'a').replace('á', 'a').replace('â', 'a')
    nome = nome.replace('é', 'e').replace('ê', 'e').replace('í', 'i')
    nome = nome.replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')
    return nome

# Função antiga problemática (que estava sendo usada antes)
def normaliza_opcional(nome):
    if not nome:
        return ''
    return str(nome).strip()  # SÓ REMOVE ESPAÇOS, NÃO NORMALIZA!

# IDs dos projetos problema
projetos_teste = {
    '2509 - WORLD SET': '8b4cd282-203c-4c2f-a13e-1e0d6b0745dc',
    '2606 - WORLD JUN': 'c658bec1-0196-4ad0-b1d9-19b418419223'
}

print("🔍 VALIDAÇÃO FINAL DA CORREÇÃO")
print("="*50)
print("Testando a diferença entre as funções normalizar vs normaliza_opcional")
print()

for nome_projeto, projeto_id in projetos_teste.items():
    print(f"📁 {nome_projeto}")
    
    # Buscar todas as tarefas
    tarefas = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute().data
    print(f"   Total de tarefas: {len(tarefas)}")
    
    # Encontrar lançamentos
    lancamentos = []
    for tarefa in tarefas:
        nome_tarefa = tarefa.get('nome', '')
        print(f"   Tarefa: '{nome_tarefa}' -> normalizar(): '{normalizar(nome_tarefa)}' | normaliza_opcional(): '{normaliza_opcional(nome_tarefa)}'")
        
        if normalizar(nome_tarefa) == 'lancamento':
            lancamentos.append(tarefa)
    
    print(f"   ✅ Lançamentos encontrados com normalizar(): {len(lancamentos)}")
    
    for lanc in lancamentos:
        data_inicio = lanc.get('data_inicio')
        status = lanc.get('status')
        print(f"   📅 Data de lançamento: {data_inicio} (Status: {status})")
    
    # Simular cenários de filtro
    print(f"   🧪 Simulação de filtros:")
    
    # Cenário 1: Sem filtros (deveria mostrar a data)
    data_lancamento_sem_filtro = None
    for tarefa in tarefas:
        if normalizar(tarefa.get('nome', '')) == 'lancamento':
            data_lancamento_sem_filtro = tarefa.get('data_inicio')
            break
    print(f"      Sem filtros: {data_lancamento_sem_filtro}")
    
    # Cenário 2: Com filtro de status (problemático antes da correção)
    status_comuns = ['pendente', 'em progresso', 'ativo', 'concluída']
    
    for status_filtro in status_comuns:
        # LÓGICA ANTES DA CORREÇÃO (problemática)
        tarefas_filtradas_ANTES = [
            t for t in tarefas 
            if t.get('status') == status_filtro or normaliza_opcional(t.get('nome', '')) == 'lancamento'  # PROBLEMA: normaliza_opcional não normaliza!
        ]
        
        # LÓGICA APÓS A CORREÇÃO (corrigida)
        tarefas_filtradas_DEPOIS = [
            t for t in tarefas 
            if t.get('status') == status_filtro or normalizar(t.get('nome', '')) == 'lancamento'  # CORREÇÃO: normalizar funciona!
        ]
        
        data_ANTES = None
        data_DEPOIS = None
        
        for t in tarefas_filtradas_ANTES:
            if normaliza_opcional(t.get('nome', '')) == 'lancamento':
                data_ANTES = t.get('data_inicio')
                break
                
        for t in tarefas_filtradas_DEPOIS:
            if normalizar(t.get('nome', '')) == 'lancamento':
                data_DEPOIS = t.get('data_inicio')
                break
        
        print(f"      Filtro '{status_filtro}':")
        print(f"         ANTES (normaliza_opcional): {len(tarefas_filtradas_ANTES)} tarefas -> Data: {data_ANTES}")
        print(f"         DEPOIS (normalizar):        {len(tarefas_filtradas_DEPOIS)} tarefas -> Data: {data_DEPOIS}")
        
        if data_ANTES != data_DEPOIS:
            if data_DEPOIS and not data_ANTES:
                print(f"         ✅ CORREÇÃO FUNCIONOU! Agora encontra a data de lançamento")
            elif data_ANTES and not data_DEPOIS:
                print(f"         ❌ PIORA! Perdeu a data de lançamento")
            else:
                print(f"         🔄 MUDANÇA: Resultado diferente")
    
    print()

print("🏁 RESUMO DA VALIDAÇÃO:")
print("="*30)
print("✅ CORREÇÃO APLICADA: Mudamos normaliza_opcional() para normalizar() na linha de filtro")
print("✅ FUNÇÃO normalizar(): Remove acentos E converte para minúsculo")  
print("❌ FUNÇÃO normaliza_opcional(): Só remove espaços (era o problema)")
print()
print("💡 RESULTADO ESPERADO:")
print("   Agora a comparação 'Lançamento' == 'lancamento' funciona corretamente")
print("   Os projetos devem mostrar suas datas de lançamento mesmo com filtros de status!")
print()
print("🧪 PARA TESTAR NA PRÁTICA:")
print("   1. Faça login na aplicação")
print("   2. Acesse /projetos (sem filtros) -> Deve mostrar as datas")  
print("   3. Acesse /projetos?status=pendente -> Projeto 2606 deve mostrar data")
print("   4. Acesse /projetos?status=concluída -> Projeto 2509 deve mostrar data")