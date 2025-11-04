#!/usr/bin/env python3
"""
Teste da funcionalidade de datas conflitantes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simular dados para teste
projetos = [
    {
        'id': '1',
        'nome': 'Projeto Teste 1',
        'data_inicio': '2024-01-15',
        'data_fim': '2024-01-10'  # Data fim anterior ao início - CONFLITO
    },
    {
        'id': '2',
        'nome': 'Projeto Teste 2',
        'data_inicio': '2024-01-01',
        'data_fim': '2024-01-31'
    }
]

tarefas = [
    {
        'id': '1',
        'nome': 'Tarefa 1',
        'projeto_id': '2',
        'ordem': 1,
        'data_inicio': '2023-12-15',  # Fora do período do projeto - CONFLITO
        'data_fim': '2024-01-05'
    },
    {
        'id': '2', 
        'nome': 'Tarefa 2',
        'projeto_id': '2',
        'ordem': 2,
        'data_inicio': '2024-01-10',
        'data_fim': '2024-01-05'  # Data fim anterior ao início - CONFLITO
    },
    {
        'id': '3',
        'nome': 'Tarefa 3',
        'projeto_id': '2',
        'ordem': 3,
        'data_inicio': '2024-01-10',
        'data_fim': '2024-01-15'
    },
    {
        'id': '4',
        'nome': 'Tarefa 4',
        'projeto_id': '2', 
        'ordem': 4,
        'data_inicio': '2024-01-12',  # Sobreposta com Tarefa 3 - CONFLITO
        'data_fim': '2024-01-18'
    },
    {
        'id': '5',
        'nome': 'Tarefa 5',
        'projeto_id': '2',
        'ordem': 5,
        'predecessoras': '99FS',  # Predecessora inexistente - CONFLITO
        'data_inicio': '2024-01-20',
        'data_fim': '2024-01-25'
    },
    {
        'id': '6',
        'nome': 'Tarefa 6',
        'projeto_id': '2',
        'ordem': 6,
        'predecessoras': '7FS',  # Predecessora com ordem posterior - CONFLITO
        'data_inicio': '2024-01-22',
        'data_fim': '2024-01-28'
    }
]

# Importar a função de detecção de conflitos
try:
    from routes.relatorio import detectar_conflitos_datas
    
    print("🔍 Testando funcionalidade de datas conflitantes...")
    print("=" * 50)
    
    # Executar detecção
    conflitos = detectar_conflitos_datas(projetos, tarefas)
    
    # Mostrar resultados
    print(f"📊 Resumo dos conflitos encontrados:")
    print(f"   - Projetos inconsistentes: {len(conflitos['projetos_inconsistentes'])}")
    print(f"   - Tarefas fora do projeto: {len(conflitos['tarefas_fora_projeto'])}")
    print(f"   - Tarefas sobrepostas: {len(conflitos['tarefas_sobrepostas'])}")
    print(f"   - Datas inválidas: {len(conflitos['datas_invalidas'])}")
    print(f"   - Problemas com predecessoras: {len(conflitos['predecessoras_conflito'])}")
    
    print("\n📋 Detalhes dos conflitos:")
    
    if conflitos['projetos_inconsistentes']:
        print("\n🔥 Projetos inconsistentes:")
        for conflito in conflitos['projetos_inconsistentes']:
            print(f"   - {conflito['projeto_nome']}: {conflito['descricao']}")
    
    if conflitos['tarefas_fora_projeto']:
        print("\n⚠️ Tarefas fora do projeto:")
        for conflito in conflitos['tarefas_fora_projeto']:
            print(f"   - {conflito['tarefa_nome']} em {conflito['projeto_nome']}: {conflito['descricao']}")
    
    if conflitos['datas_invalidas']:
        print("\n❌ Datas inválidas:")
        for conflito in conflitos['datas_invalidas']:
            print(f"   - {conflito.get('tarefa_nome', conflito.get('projeto_nome', 'N/A'))}: {conflito['descricao']}")
    
    if conflitos['tarefas_sobrepostas']:
        print("\n🔄 Tarefas sobrepostas:")
        for conflito in conflitos['tarefas_sobrepostas']:
            print(f"   - {conflito['tarefa1_nome']} x {conflito['tarefa2_nome']}: {conflito['descricao']}")
    
    if conflitos['predecessoras_conflito']:
        print("\n🔗 Problemas com predecessoras:")
        for conflito in conflitos['predecessoras_conflito']:
            print(f"   - {conflito['tarefa_nome']} (ordem {conflito['tarefa_ordem']}): {conflito['descricao']}")
    
    print("\n✅ Teste concluído com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar módulo: {e}")
except Exception as e:
    print(f"❌ Erro durante o teste: {e}")
    import traceback
    traceback.print_exc()