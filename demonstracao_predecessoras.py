#!/usr/bin/env python3
"""
Demonstração Visual da Lógica de Predecessoras
"""

def demonstrar_logica_predecessoras():
    print("🔗 DEMONSTRAÇÃO: Lógica de Predecessoras")
    print("=" * 50)
    
    # Exemplo de projeto com tarefas
    tarefas_exemplo = [
        {'ordem': 1, 'nome': 'Análise', 'predecessoras': None},
        {'ordem': 2, 'nome': 'Design', 'predecessoras': '1FS'},
        {'ordem': 3, 'nome': 'Desenvolvimento', 'predecessoras': '2FS'},
        {'ordem': 4, 'nome': 'Testes', 'predecessoras': '3FS'},
        {'ordem': 5, 'nome': 'Deploy', 'predecessoras': '4FS'},
        
        # PROBLEMAS INTENCIONAIS PARA DEMONSTRAÇÃO
        {'ordem': 6, 'nome': 'Documentação', 'predecessoras': '99FS'},  # Predecessora inexistente
        {'ordem': 7, 'nome': 'Revisão', 'predecessoras': '10FS'},       # Predecessora posterior
    ]
    
    print("📋 TAREFAS DO PROJETO:")
    for tarefa in tarefas_exemplo:
        pred_str = tarefa['predecessoras'] or 'Nenhuma'
        print(f"   {tarefa['ordem']}. {tarefa['nome']} | Predecessoras: {pred_str}")
    
    print("\n🔍 VERIFICANDO PROBLEMAS:")
    
    # Simular a lógica de verificação
    for tarefa in tarefas_exemplo:
        predecessoras = tarefa.get('predecessoras')
        if predecessoras:
            print(f"\n📝 Analisando: {tarefa['nome']} (ordem {tarefa['ordem']})")
            print(f"   Predecessoras definidas: {predecessoras}")
            
            # Extrair números das predecessoras
            import re
            pred_list = [p.strip() for p in predecessoras.split(',') if p.strip()]
            
            for pred in pred_list:
                match = re.match(r'^(\d+)', pred)
                if match:
                    pred_ordem = int(match.group(1))
                    print(f"   → Verificando predecessora: {pred_ordem}")
                    
                    # Verificar se existe
                    pred_existe = any(t['ordem'] == pred_ordem for t in tarefas_exemplo)
                    
                    if not pred_existe:
                        print(f"   ❌ PROBLEMA: Tarefa {pred_ordem} não existe!")
                        print(f"      Solução: Remover '{pred}' ou criar Tarefa {pred_ordem}")
                    
                    elif pred_ordem >= tarefa['ordem']:
                        print(f"   ❌ PROBLEMA: Tarefa {pred_ordem} tem ordem igual/posterior!")
                        print(f"      Solução: Usar predecessora com ordem menor que {tarefa['ordem']}")
                    
                    else:
                        print(f"   ✅ OK: Tarefa {pred_ordem} existe e tem ordem válida")
    
    print("\n📊 RESUMO DOS PROBLEMAS ENCONTRADOS:")
    print("   • Tarefa 6 (Documentação): Referencia Tarefa 99 que não existe")
    print("   • Tarefa 7 (Revisão): Referencia Tarefa 10 que não existe") 
    
    print("\n💡 COMO CORRIGIR:")
    print("   1. Para Tarefa 6: Trocar '99FS' por '5FS' (depender do Deploy)")
    print("   2. Para Tarefa 7: Trocar '10FS' por '6FS' (depender da Documentação)")
    
    print("\n✅ APÓS CORREÇÃO, TODAS AS DEPENDÊNCIAS FICAM LÓGICAS!")

if __name__ == "__main__":
    demonstrar_logica_predecessoras()