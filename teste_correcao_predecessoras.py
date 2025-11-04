#!/usr/bin/env python3
"""
Teste da Correção: Predecessoras com Ordem "Posterior" são Válidas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Dados de teste com casos VÁLIDOS que antes eram marcados como erro
projetos = [
    {
        'id': '1',
        'nome': 'Projeto de Deploy',
        'data_inicio': '2024-01-01',
        'data_fim': '2024-01-31'
    }
]

tarefas = [
    # Caso 1: Preparação antecipada (FS com deslocamento negativo)
    {
        'id': '1',
        'nome': 'Preparar Servidor',
        'projeto_id': '1',
        'ordem': 3,
        'predecessoras': '8FS-2d',  # Começar 2 dias ANTES da Tarefa 8 terminar
        'data_inicio': '2024-01-10',
        'data_fim': '2024-01-12'
    },
    {
        'id': '2', 
        'nome': 'Deploy em Produção',
        'projeto_id': '1',
        'ordem': 8,
        'data_inicio': '2024-01-14',
        'data_fim': '2024-01-16'
    },
    
    # Caso 2: Start-to-Finish (SF) - tarefa termina quando outra começa
    {
        'id': '3',
        'nome': 'Monitoramento Temporário',
        'projeto_id': '1',
        'ordem': 2,
        'predecessoras': '7SF',  # Terminar quando Tarefa 7 começar
        'data_inicio': '2024-01-05',
        'data_fim': '2024-01-15'
    },
    {
        'id': '4',
        'nome': 'Sistema Principal',
        'projeto_id': '1',
        'ordem': 7,
        'data_inicio': '2024-01-15',
        'data_fim': '2024-01-20'
    },
    
    # Caso 3: Overlap controlado (SS com deslocamento negativo)
    {
        'id': '5',
        'nome': 'Testes de Integração',
        'projeto_id': '1',
        'ordem': 4,
        'predecessoras': '9SS-3d',  # Começar 3 dias ANTES da Tarefa 9 começar
        'data_inicio': '2024-01-17',
        'data_fim': '2024-01-22'
    },
    {
        'id': '6',
        'nome': 'Testes de Performance',
        'projeto_id': '1',
        'ordem': 9,
        'data_inicio': '2024-01-20',
        'data_fim': '2024-01-25'
    }
]

def testar_correcao():
    print("🔧 TESTE: Correção da Lógica de Predecessoras")
    print("=" * 50)
    
    try:
        from routes.relatorio import detectar_conflitos_datas
        
        print("📋 CENÁRIOS DE TESTE:")
        print("1. Tarefa 3 com predecessoras '8FS-2d' (preparação antecipada)")
        print("2. Tarefa 2 com predecessoras '7SF' (start-to-finish)")  
        print("3. Tarefa 4 com predecessoras '9SS-3d' (overlap controlado)")
        print()
        
        # Executar detecção
        conflitos = detectar_conflitos_datas(projetos, tarefas)
        
        print("📊 RESULTADOS APÓS CORREÇÃO:")
        print(f"   - Projetos inconsistentes: {len(conflitos['projetos_inconsistentes'])}")
        print(f"   - Tarefas fora do projeto: {len(conflitos['tarefas_fora_projeto'])}")
        print(f"   - Tarefas sobrepostas: {len(conflitos['tarefas_sobrepostas'])}")
        print(f"   - Datas inválidas: {len(conflitos['datas_invalidas'])}")
        print(f"   - Problemas com predecessoras: {len(conflitos['predecessoras_conflito'])}")
        
        # Verificar se ainda há problemas de "ordem inválida"
        problemas_ordem = [
            c for c in conflitos['predecessoras_conflito'] 
            if c.get('tipo') == 'Predecessora com ordem inválida'
        ]
        
        print(f"\n🎯 VERIFICAÇÃO ESPECÍFICA:")
        print(f"   Problemas de 'ordem inválida' encontrados: {len(problemas_ordem)}")
        
        if len(problemas_ordem) == 0:
            print("   ✅ SUCESSO: Nenhum falso positivo de ordem inválida!")
            print("   ✅ Sistema agora aceita corretamente:")
            print("      • Preparação antecipada (XFS-Nd)")
            print("      • Start-to-Finish (XSF)")
            print("      • Overlaps controlados (XSS-Nd)")
        else:
            print("   ❌ AINDA HÁ PROBLEMAS:")
            for problema in problemas_ordem:
                print(f"      - {problema['descricao']}")
        
        # Mostrar apenas problemas REAIS (predecessoras inexistentes)
        problemas_reais = [
            c for c in conflitos['predecessoras_conflito'] 
            if c.get('tipo') == 'Predecessora inexistente'
        ]
        
        print(f"\n🔍 PROBLEMAS REAIS DETECTADOS:")
        if problemas_reais:
            for problema in problemas_reais:
                print(f"   ❌ {problema['descricao']}")
        else:
            print("   ✅ Nenhum problema real encontrado nos dados de teste")
            
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

def explicar_casos_validos():
    print(f"\n\n💡 EXPLICAÇÃO DOS CASOS VÁLIDOS:")
    print("=" * 50)
    
    casos = [
        {
            'predecessora': '8FS-2d',
            'explicacao': 'Tarefa começa 2 dias ANTES da Tarefa 8 terminar',
            'uso': 'Preparação antecipada (servidor, ambiente, etc.)'
        },
        {
            'predecessora': '7SF',
            'explicacao': 'Tarefa termina quando Tarefa 7 começa',
            'uso': 'Monitoramento temporário, sistema de transição'
        },
        {
            'predecessora': '9SS-3d',
            'explicacao': 'Tarefa começa 3 dias ANTES da Tarefa 9 começar',
            'uso': 'Testes paralelos, preparação simultânea'
        }
    ]
    
    for i, caso in enumerate(casos, 1):
        print(f"{i}. Predecessora: '{caso['predecessora']}'")
        print(f"   📝 {caso['explicacao']}")
        print(f"   🎯 Uso típico: {caso['uso']}")
        print()

if __name__ == "__main__":
    testar_correcao()
    explicar_casos_validos()