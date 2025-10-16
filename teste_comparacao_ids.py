#!/usr/bin/env python3

"""
TESTE: Verificar comparação de IDs de projeto
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# ID do projeto problemático
projeto_2509_id = '8b4cd282-203c-4c2f-a13e-1e0d6b0745dc'

print("🔍 TESTE DE COMPARAÇÃO DE IDs")
print("="*35)

# Buscar tarefas
print("1️⃣ Buscar todas as tarefas do projeto 2509:")
tarefas = supabase.table("tarefas").select("*").eq("projeto_id", projeto_2509_id).execute().data
print(f"   Total: {len(tarefas)} tarefas")

if tarefas:
    primeira_tarefa = tarefas[0]
    pid_from_task = primeira_tarefa.get('projeto_id')
    
    print(f"   Projeto ID esperado: '{projeto_2509_id}' (tipo: {type(projeto_2509_id)})")
    print(f"   Projeto ID da tarefa: '{pid_from_task}' (tipo: {type(pid_from_task)})")
    
    # Testar diferentes tipos de comparação
    print(f"\n2️⃣ Testes de comparação:")
    
    # Comparação direta
    comp1 = (pid_from_task == projeto_2509_id)
    print(f"   pid_from_task == projeto_2509_id: {comp1}")
    
    # Comparação com str()
    comp2 = (str(pid_from_task) == str(projeto_2509_id))
    print(f"   str(pid_from_task) == str(projeto_2509_id): {comp2}")
    
    # Comparação com str().strip()  
    comp3 = (str(pid_from_task).strip() == str(projeto_2509_id).strip())
    print(f"   str(pid_from_task).strip() == str(projeto_2509_id).strip(): {comp3}")
    
    # Ver se há espaços ou caracteres especiais
    print(f"\n3️⃣ Análise detalhada:")
    print(f"   len(projeto_2509_id): {len(projeto_2509_id)}")
    print(f"   len(str(pid_from_task)): {len(str(pid_from_task))}")
    print(f"   repr(projeto_2509_id): {repr(projeto_2509_id)}")
    print(f"   repr(pid_from_task): {repr(pid_from_task)}")

# Simular a lógica da aplicação
print(f"\n4️⃣ Simular lógica da aplicação:")
tarefas_filtradas = tarefas  # Simular que todas as tarefas estão em tarefas_filtradas

# Método 1 (linha 129)
metodo1 = [t for t in tarefas_filtradas if t.get('projeto_id') == projeto_2509_id]
print(f"   Método 1 (==): {len(metodo1)} tarefas")

# Método 2 (linhas 266-276) 
metodo2 = []
for tarefa in tarefas_filtradas:
    tid = tarefa.get('projeto_id')
    if str(tid).strip() == str(projeto_2509_id).strip():
        metodo2.append(tarefa)
print(f"   Método 2 (str().strip()): {len(metodo2)} tarefas")

print(f"\n💡 Se os métodos retornam números diferentes,")
print(f"   isso explica por que as tarefas estão sendo perdidas!")