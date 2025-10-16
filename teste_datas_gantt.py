#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste para verificar como as datas estão sendo interpretadas no Gantt
"""

import supabase_client
import requests
from datetime import datetime, timedelta

def test_gantt_dates():
    """Verifica uma tarefa específica para entender o problema das datas"""
    
    SUPABASE_URL = supabase_client.SUPABASE_URL
    headers = supabase_client.headers
    
    print("🔍 Verificando datas de tarefas no Gantt...")
    
    # Buscar uma tarefa com datas definidas
    url_tarefas = f"{SUPABASE_URL}/rest/v1/tarefas?select=id,nome,data_inicio,data_fim&limit=5"
    resp = requests.get(url_tarefas, headers=headers)
    
    if resp.status_code == 200:
        tarefas = resp.json()
        
        for tarefa in tarefas:
            if tarefa.get('data_inicio') and tarefa.get('data_fim'):
                print(f"\n📋 Tarefa: {tarefa['nome']}")
                print(f"   Data início: {tarefa['data_inicio']}")
                print(f"   Data fim: {tarefa['data_fim']}")
                
                # Calcular duração como no JavaScript
                try:
                    inicio = datetime.strptime(tarefa['data_inicio'], '%Y-%m-%d')
                    fim = datetime.strptime(tarefa['data_fim'], '%Y-%m-%d')
                    
                    # Simular cálculo JavaScript
                    dias_entre = (fim - inicio).days
                    dias_com_adicao = dias_entre + 1
                    
                    print(f"   🧮 Cálculo JavaScript:")
                    print(f"     diasEntre(inicio, fim) = {dias_entre}")
                    print(f"     largura = diasEntre + 1 = {dias_com_adicao}")
                    
                    # Cálculo correto (inclusivo)
                    dias_corretos = (fim - inicio).days + 1
                    print(f"   ✅ Duração correta (inclusiva): {dias_corretos} dias")
                    
                    if dias_com_adicao != dias_corretos:
                        print(f"   ⚠️  PROBLEMA: Barra fica {dias_com_adicao - dias_corretos} dia(s) maior!")
                    else:
                        print(f"   ✅ Cálculo correto!")
                        
                    # Mostrar as datas que deveriam ser ocupadas
                    datas_ocupadas = []
                    current = inicio
                    while current <= fim:
                        datas_ocupadas.append(current.strftime('%d/%m'))
                        current += timedelta(days=1)
                    
                    print(f"   📅 Datas que devem ser ocupadas: {', '.join(datas_ocupadas)}")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao processar: {e}")
                
                break  # Mostrar apenas a primeira tarefa válida
    else:
        print(f"❌ Erro ao buscar tarefas: {resp.status_code}")

if __name__ == "__main__":
    test_gantt_dates()