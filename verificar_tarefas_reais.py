#!/usr/bin/env python3
"""
Verificar tarefas reais no banco que deveriam estar atrasadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.database import supabase
    from utils.validators import verificar_tarefa_atrasada
    from datetime import datetime
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

def verificar_tarefas_reais():
    """Verifica tarefas reais no banco"""
    
    print("🔍 Verificando tarefas reais no banco...")
    
    try:
        # Buscar todas as tarefas
        tarefas_resp = supabase.table("tarefas").select("*").execute()
        tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []
        
        print(f"✅ Total de tarefas encontradas: {len(tarefas)}")
        
        if not tarefas:
            print("⚠️  Nenhuma tarefa encontrada!")
            return
        
        hoje = datetime.now()
        print(f"📅 Data de hoje: {hoje.strftime('%Y-%m-%d')}")
        print()
        
        tarefas_atrasadas = []
        
        for tarefa in tarefas:
            nome = tarefa.get('nome', 'Sem nome')
            status = tarefa.get('status', 'N/A')
            data_inicio = tarefa.get('data_inicio', 'N/A')
            data_fim = tarefa.get('data_fim', 'N/A')
            
            # Verificar se está atrasada
            atrasada = verificar_tarefa_atrasada(tarefa)
            
            if atrasada:
                tarefas_atrasadas.append(tarefa)
                print(f"⚠️  TAREFA ATRASADA: {nome}")
                print(f"   Status: {status}")
                print(f"   Data início: {data_inicio}")
                print(f"   Data fim: {data_fim}")
                print()
        
        print(f"📊 Resumo: {len(tarefas_atrasadas)} tarefas atrasadas encontradas")
        
        if len(tarefas_atrasadas) == 0:
            print("\n🔍 Analisando por que não há tarefas atrasadas...")
            
            # Verificar tarefas com datas passadas
            for tarefa in tarefas:
                nome = tarefa.get('nome', 'Sem nome')
                status = tarefa.get('status', 'N/A')
                data_inicio = tarefa.get('data_inicio', 'N/A')
                data_fim = tarefa.get('data_fim', 'N/A')
                
                # Verificar se tem data passada
                if data_fim and data_fim != 'N/A':
                    try:
                        data_fim_obj = datetime.strptime(data_fim.split('T')[0], '%Y-%m-%d')
                        if data_fim_obj < hoje:
                            print(f"📅 Tarefa com data passada: {nome}")
                            print(f"   Status: {status}")
                            print(f"   Data fim: {data_fim} (passada em {(hoje - data_fim_obj).days} dias)")
                            print(f"   Por que não está atrasada? Status: {status}")
                            print()
                    except:
                        pass
                        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_tarefas_reais() 