#!/usr/bin/env python3
"""
Teste simples para verificar a funcionalidade de exportação por projeto
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import supabase

def testar_exportacao_projeto():
    """Testa a funcionalidade de exportação por projeto"""
    print("🔍 Testando funcionalidade de exportação por projeto...")
    
    try:
        # Buscar projetos existentes
        projetos_resp = supabase.table('projetos').select('id, nome').limit(5).execute()
        
        if hasattr(projetos_resp, 'data') and projetos_resp.data:
            projetos = projetos_resp.data
            print(f"✅ Encontrados {len(projetos)} projetos:")
            
            for projeto in projetos:
                print(f"  - ID: {projeto['id']} | Nome: {projeto['nome']}")
                
                # Buscar tarefas deste projeto
                tarefas_resp = supabase.table('tarefas').select('id, nome, data_inicio, data_fim').eq('projeto_id', projeto['id']).execute()
                
                if hasattr(tarefas_resp, 'data') and tarefas_resp.data:
                    tarefas = tarefas_resp.data
                    print(f"    📋 {len(tarefas)} tarefas encontradas")
                    
                    # Mostrar algumas tarefas
                    for tarefa in tarefas[:3]:
                        print(f"      • {tarefa['nome']} ({tarefa.get('data_inicio', 'Sem data')} - {tarefa.get('data_fim', 'Sem data')})")
                        
                    if len(tarefas) > 3:
                        print(f"      ... e mais {len(tarefas) - 3} tarefas")
                else:
                    print(f"    ℹ️ Nenhuma tarefa encontrada")
                    
                print()  # Linha em branco
        else:
            print("❌ Nenhum projeto encontrado no sistema")
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        
    print("📊 Teste de exportação por projeto concluído!")

if __name__ == '__main__':
    testar_exportacao_projeto()