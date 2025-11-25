#!/usr/bin/env python3
"""
Corrigir status do projeto 2601 - WORLD JAN
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

def corrigir_status_projeto_2601():
    """Corrige o status do projeto 2601 - WORLD JAN baseado nas tarefas atuais"""

    print("🔧 Corrigindo status do projeto '2601 - WORLD JAN'...")

    try:
        # Buscar o projeto
        projeto_resp = supabase.table("projetos").select("*").eq("nome", "2601 - WORLD JAN").execute()
        projetos = projeto_resp.data if hasattr(projeto_resp, 'data') else []

        if not projetos:
            print("❌ Projeto '2601 - WORLD JAN' não encontrado!")
            return

        projeto = projetos[0]
        projeto_id = projeto.get('id')
        print(f"✅ Projeto encontrado: {projeto.get('nome', 'Sem nome')} (ID: {projeto_id})")
        print(f"   Status atual: {projeto.get('status', 'Sem status')}")
        print()

        # Buscar todas as tarefas do projeto
        tarefas_resp = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute()
        tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []

        print(f"📋 Analisando {len(tarefas)} tarefas...")

        # Contar tarefas por status
        tarefas_atrasadas = 0
        tarefas_em_progresso = 0
        tarefas_pendentes = 0
        tarefas_concluidas = 0

        for tarefa in tarefas:
            status = tarefa.get('status', '').lower()
            if verificar_tarefa_atrasada(tarefa):
                tarefas_atrasadas += 1
            if status == 'em progresso':
                tarefas_em_progresso += 1
            if status == 'pendente':
                tarefas_pendentes += 1
            if status in ['concluída', 'concluida']:
                tarefas_concluidas += 1

        # Determinar novo status baseado na lógica do sistema
        if tarefas_atrasadas > 0:
            novo_status = 'atrasado'
        elif tarefas_em_progresso > 0:
            novo_status = 'em progresso'
        elif len(tarefas) > 0 and tarefas_concluidas == len(tarefas):
            novo_status = 'concluído'
        else:
            novo_status = 'pendente'

        print("📊 Análise das tarefas:")
        print(f"   Tarefas concluídas: {tarefas_concluidas}")
        print(f"   Tarefas em progresso: {tarefas_em_progresso}")
        print(f"   Tarefas pendentes: {tarefas_pendentes}")
        print(f"   Tarefas atrasadas: {tarefas_atrasadas}")
        print()
        print(f"🎯 Status calculado: {novo_status}")
        print(f"📝 Status atual no banco: {projeto.get('status', 'Sem status')}")

        # Atualizar status se necessário
        if novo_status != projeto.get('status', ''):
            print(f"🔄 Atualizando status de '{projeto.get('status', '')}' para '{novo_status}'...")

            update_resp = supabase.table("projetos").update({"status": novo_status}).eq("id", projeto_id).execute()

            if hasattr(update_resp, 'data') and update_resp.data:
                print("✅ Status atualizado com sucesso!")
            else:
                print("❌ Erro ao atualizar status no banco")
        else:
            print("✅ Status já está correto - nenhuma atualização necessária")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_status_projeto_2601()