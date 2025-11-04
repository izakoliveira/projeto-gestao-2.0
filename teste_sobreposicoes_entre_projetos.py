#!/usr/bin/env python3
"""
Teste: Detecção de Tarefas Sobrepostas Entre Projetos Diferentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Dados de teste com sobreposições entre projetos
projetos = [
    {
        'id': '1',
        'nome': 'Projeto Website',
        'data_inicio': '2024-01-01',
        'data_fim': '2024-01-31'
    },
    {
        'id': '2', 
        'nome': 'Projeto Mobile App',
        'data_inicio': '2024-01-15',
        'data_fim': '2024-02-15'
    },
    {
        'id': '3',
        'nome': 'Projeto Dashboard',
        'data_inicio': '2024-02-01',
        'data_fim': '2024-02-28'
    }
]

tarefas = [
    # Projeto 1 - Website
    {
        'id': '1',
        'nome': 'Design Interface',
        'projeto_id': '1', 
        'ordem': 1,
        'data_inicio': '2024-01-10',
        'data_fim': '2024-01-20'
    },
    {
        'id': '2',
        'nome': 'Desenvolvimento Frontend',
        'projeto_id': '1',
        'ordem': 2,
        'data_inicio': '2024-01-15',  # Sobrepõe com Design Interface (mesmo projeto - OK)
        'data_fim': '2024-01-25'
    },
    
    # Projeto 2 - Mobile App
    {
        'id': '3', 
        'nome': 'Wireframes Mobile',
        'projeto_id': '2',
        'ordem': 1,
        'data_inicio': '2024-01-18',  # SOBREPÕE com "Design Interface" do Projeto 1
        'data_fim': '2024-01-22'
    },
    {
        'id': '4',
        'nome': 'Desenvolvimento App',
        'projeto_id': '2',
        'ordem': 2,
        'data_inicio': '2024-01-23',  # SOBREPÕE com "Desenvolvimento Frontend" do Projeto 1  
        'data_fim': '2024-02-05'
    },
    
    # Projeto 3 - Dashboard
    {
        'id': '5',
        'nome': 'Análise de Requisitos',
        'projeto_id': '3',
        'ordem': 1,
        'data_inicio': '2024-02-02',  # SOBREPÕE com "Desenvolvimento App" do Projeto 2
        'data_fim': '2024-02-08'
    },
    {
        'id': '6',
        'nome': 'Prototipagem Dashboard',
        'projeto_id': '3',
        'ordem': 2,
        'data_inicio': '2024-02-05',  # Sobrepõe com "Análise de Requisitos" (mesmo projeto - OK)
        'data_fim': '2024-02-12'
    }
]

def testar_sobreposicoes_entre_projetos():
    print("🔍 TESTE: Detecção de Sobreposições Entre Projetos")
    print("=" * 60)
    
    try:
        from routes.relatorio import detectar_conflitos_datas
        
        print("📊 CENÁRIOS DE TESTE:")
        print("   Projeto 1 (Website):")
        print("   - Design Interface: 10/01 - 20/01")
        print("   - Desenvolvimento Frontend: 15/01 - 25/01")
        print()
        print("   Projeto 2 (Mobile App):")
        print("   - Wireframes Mobile: 18/01 - 22/01  ⚠️ SOBREPÕE com Design")
        print("   - Desenvolvimento App: 23/01 - 05/02  ⚠️ SOBREPÕE com Frontend")
        print()
        print("   Projeto 3 (Dashboard):")  
        print("   - Análise de Requisitos: 02/02 - 08/02  ⚠️ SOBREPÕE com Dev App")
        print("   - Prototipagem Dashboard: 05/02 - 12/02")
        print()
        
        # Executar detecção
        conflitos = detectar_conflitos_datas(projetos, tarefas)
        
        print("📋 RESULTADOS DA DETECÇÃO:")
        print(f"   - Sobrepostas no mesmo projeto: {len(conflitos['tarefas_sobrepostas'])}")
        print(f"   - Sobrepostas entre projetos: {len(conflitos['tarefas_sobrepostas_entre_projetos'])}")
        print()
        
        print("🔄 SOBREPOSIÇÕES NO MESMO PROJETO:")
        if conflitos['tarefas_sobrepostas']:
            for conflito in conflitos['tarefas_sobrepostas']:
                print(f"   ✅ {conflito['projeto_nome']}: {conflito['tarefa1_nome']} ↔ {conflito['tarefa2_nome']}")
        else:
            print("   ❌ Nenhuma detectada")
        print()
        
        print("🔀 SOBREPOSIÇÕES ENTRE PROJETOS DIFERENTES:")
        if conflitos['tarefas_sobrepostas_entre_projetos']:
            for i, conflito in enumerate(conflitos['tarefas_sobrepostas_entre_projetos'], 1):
                print(f"   {i}. {conflito['projeto1_nome']} → {conflito['tarefa1_nome']}")
                print(f"      × {conflito['projeto2_nome']} → {conflito['tarefa2_nome']}")
                print(f"      📅 Período: {conflito['tarefa1_inicio']} - {conflito['tarefa1_fim']}")
                print(f"                 vs {conflito['tarefa2_inicio']} - {conflito['tarefa2_fim']}")
                print()
        else:
            print("   ❌ Nenhuma detectada")
            
        # Verificação das expectativas
        sobreposicoes_esperadas = 3  # 3 sobreposições entre projetos diferentes
        sobreposicoes_encontradas = len(conflitos['tarefas_sobrepostas_entre_projetos'])
        
        print("🎯 VALIDAÇÃO:")
        print(f"   Esperadas: {sobreposicoes_esperadas} sobreposições entre projetos")
        print(f"   Encontradas: {sobreposicoes_encontradas} sobreposições entre projetos")
        
        if sobreposicoes_encontradas == sobreposicoes_esperadas:
            print("   ✅ SUCESSO: Todas as sobreposições foram detectadas corretamente!")
        else:
            print("   ❌ PROBLEMA: Número de sobreposições não confere")
            
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

def mostrar_beneficios():
    print(f"\n\n💡 BENEFÍCIOS DA NOVA FUNCIONALIDADE:")
    print("=" * 60)
    
    beneficios = [
        {
            'titulo': 'Gestão de Recursos',
            'descricao': 'Identificar quando equipes trabalham em tarefas simultâneas'
        },
        {
            'titulo': 'Planejamento Estratégico', 
            'descricao': 'Visualizar conflitos de agenda entre diferentes projetos'
        },
        {
            'titulo': 'Otimização de Timeline',
            'descricao': 'Reorganizar cronogramas para evitar sobrecargas'
        },
        {
            'titulo': 'Análise de Capacidade',
            'descricao': 'Entender se a equipe consegue entregar tudo no prazo'
        }
    ]
    
    for i, beneficio in enumerate(beneficios, 1):
        print(f"{i}. {beneficio['titulo']}")
        print(f"   📝 {beneficio['descricao']}")
        print()

if __name__ == "__main__":
    testar_sobreposicoes_entre_projetos()
    mostrar_beneficios()