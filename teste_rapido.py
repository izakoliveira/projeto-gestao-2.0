#!/usr/bin/env python3

# Teste simples da correção
def normalizar(nome):
    if not nome:
        return ''
    return nome.strip().lower().replace('ã', 'a').replace('á', 'a').replace('â', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ç', 'c')

def normaliza_opcional(valor):
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor.strip() if valor.strip() else None
    return valor

# Simular o problema
nome_tarefa = "Lançamento"
print(f"🔧 TESTE DA CORREÇÃO")
print(f"="*30)
print(f"Nome da tarefa: '{nome_tarefa}'")
print()

# ANTES da correção (INCORRETO)
resultado_antes = normaliza_opcional(nome_tarefa) == 'lancamento'
print(f"ANTES (normaliza_opcional): '{normaliza_opcional(nome_tarefa)}' == 'lancamento' -> {resultado_antes}")

# DEPOIS da correção (CORRETO) 
resultado_depois = normalizar(nome_tarefa) == 'lancamento'
print(f"DEPOIS (normalizar): '{normalizar(nome_tarefa)}' == 'lancamento' -> {resultado_depois}")

print()
print(f"🎯 RESULTADO:")
if resultado_depois:
    print(f"✅ CORREÇÃO FUNCIONOU! Agora o filtro encontra tarefas de lançamento")
else:
    print(f"❌ Algo ainda está errado")

print()
print(f"📋 EXPLICAÇÃO:")
print(f"- normaliza_opcional('{nome_tarefa}') = '{normaliza_opcional(nome_tarefa)}'")
print(f"- normalizar('{nome_tarefa}') = '{normalizar(nome_tarefa)}'")
print(f"- Para passar no filtro, precisa ser igual a 'lancamento'")
print(f"- Apenas a função normalizar() faz a conversão correta!")