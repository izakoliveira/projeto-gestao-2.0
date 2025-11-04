#!/usr/bin/env python3
"""
Teste direto da funcionalidade de exportação Excel
"""

import sys
import os
sys.path.append('.')

def test_excel_generation():
    """Testa diretamente a geração de Excel"""
    print("🧪 TESTE DIRETO: Geração de Excel")
    print("=" * 50)
    
    try:
        import pandas as pd
        import io
        
        # Dados de teste simples
        dados = [
            {
                'Projeto': 'Projeto Teste',
                'Tarefa': 'Tarefa 1',
                'Início': '01/01/2025',
                'Fim': '31/01/2025',
                'Dias Úteis': 20,
                'Duração': 30,
                'Coleção': 'Desenvolvimento',
                'Responsável': 'João Silva',
            },
            {
                'Projeto': 'Projeto Teste',
                'Tarefa': 'Tarefa 2',
                'Início': '01/02/2025',
                'Fim': '28/02/2025',
                'Dias Úteis': 18,
                'Duração': 28,
                'Coleção': 'Testes',
                'Responsável': 'Maria Souza',
            }
        ]
        
        print(f"✅ Dados de teste criados: {len(dados)} registros")
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        print(f"✅ DataFrame criado: {df.shape}")
        
        # Gerar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
            print("✅ Excel gerado na memória")
        
        output.seek(0)
        tamanho = len(output.getvalue())
        print(f"✅ Arquivo Excel: {tamanho} bytes")
        
        if tamanho > 1000:
            print("🎉 SUCESSO! A geração de Excel está funcionando corretamente!")
            return True
        else:
            print("❌ Arquivo muito pequeno, pode ter problema")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_supabase_connection():
    """Testa conexão com Supabase"""
    print("\n🧪 TESTE: Conexão Supabase")
    print("=" * 50)
    
    try:
        from config.database import supabase
        
        # Teste simples de conexão
        result = supabase.table('tarefas').select('id').limit(1).execute()
        
        if hasattr(result, 'data'):
            print(f"✅ Conexão Supabase OK")
            return True
        else:
            print("❌ Resposta inválida do Supabase")
            return False
            
    except Exception as e:
        print(f"❌ ERRO Supabase: {e}")
        return False

def main():
    print("🚀 DIAGNÓSTICO COMPLETO DO SISTEMA")
    print("=" * 60)
    
    testes_passaram = 0
    total_testes = 2
    
    if test_excel_generation():
        testes_passaram += 1
        
    if test_supabase_connection():
        testes_passaram += 1
    
    print(f"\n📊 RESULTADO: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ O sistema deveria estar funcionando corretamente")
        print("   Se ainda há erro, pode ser um problema de indentação ou sintaxe")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("   Verifique os erros acima")

if __name__ == "__main__":
    main()