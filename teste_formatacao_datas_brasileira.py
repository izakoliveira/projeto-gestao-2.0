#!/usr/bin/env python3
"""
Teste: Formatação de Datas no Formato Brasileiro (DD/MM/AAAA)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Dados de teste com datas em formato ISO
projetos = [
    {
        'id': '1',
        'nome': 'Projeto Teste',
        'data_inicio': '2024-01-15',  # ISO: 2024-01-15 -> Brasileiro: 15/01/2024
        'data_fim': '2024-02-28'     # ISO: 2024-02-28 -> Brasileiro: 28/02/2024
    }
]

tarefas = [
    {
        'id': '1',
        'nome': 'Tarefa de Desenvolvimento',
        'projeto_id': '1',
        'ordem': 1,
        'data_inicio': '2024-01-20T09:00:00',  # Com horário
        'data_fim': '2024-02-10T18:00:00'
    },
    {
        'id': '2',
        'nome': 'Tarefa de Testes',
        'projeto_id': '1',
        'ordem': 2,
        'data_inicio': '2024-02-05',  # Sem horário
        'data_fim': '2024-02-25'
    }
]

def testar_formatacao_datas():
    print("📅 TESTE: Formatação de Datas no Formato Brasileiro")
    print("=" * 60)
    
    try:
        from routes.relatorio import detectar_conflitos_datas
        
        print("📊 DADOS DE ENTRADA (Formato ISO):")
        print(f"   Projeto: {projetos[0]['data_inicio']} até {projetos[0]['data_fim']}")
        print(f"   Tarefa 1: {tarefas[0]['data_inicio']} até {tarefas[0]['data_fim']}")
        print(f"   Tarefa 2: {tarefas[1]['data_inicio']} até {tarefas[1]['data_fim']}")
        print()
        
        # Executar detecção
        conflitos = detectar_conflitos_datas(projetos, tarefas)
        
        print("📋 RESULTADOS COM FORMATAÇÃO BRASILEIRA:")
        
        # Verificar tarefas sobrepostas (deve ter pelo menos uma)
        if conflitos['tarefas_sobrepostas']:
            conflito = conflitos['tarefas_sobrepostas'][0]
            print("🔄 Tarefas Sobrepostas no Mesmo Projeto:")
            print(f"   Tarefa 1: {conflito['tarefa1_inicio']} até {conflito['tarefa1_fim']}")
            print(f"   Tarefa 2: {conflito['tarefa2_inicio']} até {conflito['tarefa2_fim']}")
            print(f"   Descrição: {conflito['descricao']}")
            print()
            
            # Validar formato brasileiro
            import re
            padrao_brasileiro = r'\d{2}/\d{2}/\d{4}'
            
            print("✅ VALIDAÇÃO DO FORMATO:")
            formatos_corretos = []
            
            datas_para_validar = [
                ('Tarefa 1 Início', conflito['tarefa1_inicio']),
                ('Tarefa 1 Fim', conflito['tarefa1_fim']),
                ('Tarefa 2 Início', conflito['tarefa2_inicio']),
                ('Tarefa 2 Fim', conflito['tarefa2_fim'])
            ]
            
            for nome, data in datas_para_validar:
                if re.match(padrao_brasileiro, data):
                    print(f"   ✅ {nome}: {data} (formato correto)")
                    formatos_corretos.append(True)
                else:
                    print(f"   ❌ {nome}: {data} (formato incorreto)")
                    formatos_corretos.append(False)
            
            if all(formatos_corretos):
                print("\n🎉 SUCESSO: Todas as datas estão no formato brasileiro DD/MM/AAAA!")
            else:
                print("\n❌ PROBLEMA: Algumas datas não estão no formato correto")
        
        else:
            print("⚠️ Nenhuma sobreposição detectada para testar formato")
            
        # Testar outros tipos de conflito se existirem
        print(f"\n📊 RESUMO DOS CONFLITOS:")
        print(f"   - Projetos inconsistentes: {len(conflitos['projetos_inconsistentes'])}")
        print(f"   - Tarefas fora do projeto: {len(conflitos['tarefas_fora_projeto'])}")
        print(f"   - Tarefas sobrepostas: {len(conflitos['tarefas_sobrepostas'])}")
        print(f"   - Sobrepostas entre projetos: {len(conflitos['tarefas_sobrepostas_entre_projetos'])}")
        
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

def mostrar_exemplos_conversao():
    print(f"\n\n💡 EXEMPLOS DE CONVERSÃO:")
    print("=" * 60)
    
    exemplos = [
        ('2024-01-15', '15/01/2024'),
        ('2024-02-28T14:30:00', '28/02/2024'), 
        ('2024-12-01', '01/12/2024'),
        ('2025-03-10T09:00:00Z', '10/03/2025')
    ]
    
    for iso, brasileiro in exemplos:
        print(f"   {iso:<25} → {brasileiro}")

if __name__ == "__main__":
    testar_formatacao_datas()
    mostrar_exemplos_conversao()