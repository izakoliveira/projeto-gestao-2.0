#!/usr/bin/env python3
"""
Demonstração de Tipos de Dependências com Deslocamentos
"""

def demonstrar_tipos_dependencias():
    print("🔗 TIPOS DE DEPENDÊNCIAS ENTRE TAREFAS")
    print("=" * 50)
    
    exemplos = [
        {
            'caso': 'Caso 1: Sequencial Normal',
            'tarefa_a': 'Desenvolvimento (15 dias)',
            'tarefa_b': 'Testes',
            'dependencia': '1FS',
            'explicacao': 'Testes começam quando Desenvolvimento termina'
        },
        {
            'caso': 'Caso 2: Começar Junto',
            'tarefa_a': 'Design UI (10 dias)', 
            'tarefa_b': 'Design UX',
            'dependencia': '1SS',
            'explicacao': 'Design UX começa junto com Design UI'
        },
        {
            'caso': 'Caso 3: Terminar Junto',
            'tarefa_a': 'Codificação (20 dias)',
            'tarefa_b': 'Documentação',
            'dependencia': '1FF',
            'explicacao': 'Documentação termina quando Codificação termina'
        },
        {
            'caso': 'Caso 4: Preparação Antecipada - SUA PERGUNTA!',
            'tarefa_a': 'Deployment (5 dias)',
            'tarefa_b': 'Preparar Ambiente',
            'dependencia': '1FS-3d',
            'explicacao': 'Preparar Ambiente começa 3 dias ANTES do Deployment terminar'
        },
        {
            'caso': 'Caso 5: Sobreposição Controlada',
            'tarefa_a': 'Desenvolvimento (15 dias)',
            'tarefa_b': 'Testes Unitários', 
            'dependencia': '1SS+5d',
            'explicacao': 'Testes começam 5 dias DEPOIS do Desenvolvimento começar'
        }
    ]
    
    for exemplo in exemplos:
        print(f"\n📋 {exemplo['caso']}")
        print(f"   Tarefa A: {exemplo['tarefa_a']}")
        print(f"   Tarefa B: {exemplo['tarefa_b']}")
        print(f"   Dependência: '{exemplo['dependencia']}'")
        print(f"   📝 {exemplo['explicacao']}")
        
        # Visualização temporal
        if exemplo['dependencia'] == '1FS':
            print("   📅 A: ████████████████")
            print("   📅 B:                 ████████")
        elif exemplo['dependencia'] == '1SS':
            print("   📅 A: ████████████")
            print("   📅 B: ████████")
        elif exemplo['dependencia'] == '1FF':
            print("   📅 A: ████████████████")
            print("   📅 B:      ████████████████")
        elif exemplo['dependencia'] == '1FS-3d':
            print("   📅 A: ████████████████")
            print("   📅 B:          ████████     (começa 3d antes de A terminar)")
        elif exemplo['dependencia'] == '1SS+5d':
            print("   📅 A: ████████████████")
            print("   📅 B:      ████████        (começa 5d depois de A começar)")
    
    print(f"\n🎯 RESPONDENDO SUA PERGUNTA:")
    print(f"   Para uma tarefa começar X dias ANTES de outra terminar:")
    print(f"   Use: '[numero]FS-[X]d'")
    print(f"   Exemplo: '3FS-5d' = começar 5 dias antes da Tarefa 3 terminar")
    
    print(f"\n   Para uma tarefa começar X dias ANTES de outra começar:")
    print(f"   Use: '[numero]SS-[X]d'") 
    print(f"   Exemplo: '2SS-3d' = começar 3 dias antes da Tarefa 2 começar")

def mostrar_casos_reais():
    print(f"\n\n🏗️ EXEMPLOS DO MUNDO REAL:")
    print("=" * 50)
    
    casos_reais = [
        {
            'contexto': 'Projeto de Software',
            'tarefa_principal': 'Deploy em Produção',
            'tarefa_preparatoria': 'Configurar Servidor',
            'dependencia': '10FS-2d',
            'explicacao': 'Servidor deve estar pronto 2 dias antes do deploy'
        },
        {
            'contexto': 'Evento/Lançamento', 
            'tarefa_principal': 'Lançamento do Produto',
            'tarefa_preparatoria': 'Marketing/Divulgação',
            'dependencia': '5FS-7d',
            'explicacao': 'Marketing começa 7 dias antes do lançamento'
        },
        {
            'contexto': 'Construção Civil',
            'tarefa_principal': 'Instalação Elétrica', 
            'tarefa_preparatoria': 'Compra de Material',
            'dependencia': '8FS-3d',
            'explicacao': 'Material deve chegar 3 dias antes da instalação'
        }
    ]
    
    for caso in casos_reais:
        print(f"\n🏢 {caso['contexto']}")
        print(f"   Tarefa Principal: {caso['tarefa_principal']}")
        print(f"   Preparação: {caso['tarefa_preparatoria']}")
        print(f"   Dependência: '{caso['dependencia']}'")
        print(f"   💡 {caso['explicacao']}")

if __name__ == "__main__":
    demonstrar_tipos_dependencias()
    mostrar_casos_reais()