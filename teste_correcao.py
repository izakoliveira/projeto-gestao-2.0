#!/usr/bin/env python3
"""
Teste rápido da correção do status do projeto
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

def teste_correcao_status():
    """Testa se a correção do status funcionou"""

    print("🧪 Testando correção do status do projeto '2601 - WORLD JAN'...")

    try:
        # Buscar o projeto
        projeto_resp = supabase.table("projetos").select("*").eq("nome", "2601 - WORLD JAN").execute()
        projetos = projeto_resp.data if hasattr(projeto_resp, 'data') else []

        if not projetos:
            print("❌ Projeto não encontrado!")
            return

        projeto = projetos[0]
        projeto_id = projeto.get('id')
        print(f"✅ Projeto encontrado: {projeto.get('nome', 'Sem nome')}")
        print(f"   Status no banco: {projeto.get('status', 'Sem status')}")

        # Buscar tarefas
        tarefas_resp = supabase.table("tarefas").select("*").eq("projeto_id", projeto_id).execute()
        tarefas = tarefas_resp.data if hasattr(tarefas_resp, 'data') else []

        print(f"📋 Tarefas encontradas: {len(tarefas)}")

        # Simular a lógica correta (igual à que está no código agora)
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

        # Determinar status correto
        if tarefas_atrasadas > 0:
            status_correto = 'atrasado'
        elif tarefas_em_progresso > 0:
            status_correto = 'em progresso'
        elif len(tarefas) > 0 and tarefas_concluidas == len(tarefas):
            status_correto = 'concluído'
        else:
            status_correto = 'pendente'

        print("\n📊 Cálculo correto:")
        print(f"   Tarefas atrasadas: {tarefas_atrasadas}")
        print(f"   Tarefas em progresso: {tarefas_em_progresso}")
        print(f"   Tarefas pendentes: {tarefas_pendentes}")
        print(f"   Tarefas concluídas: {tarefas_concluidas}")
        print(f"   Status CORRETO: {status_correto}")
        print(f"   Status no BANCO: {projeto.get('status', 'Sem status')}")

        if status_correto == projeto.get('status', ''):
            print("✅ CORREÇÃO CONFIRMADA: Status está correto!")
        else:
            print("❌ AINDA HÁ PROBLEMA: Status não foi corrigido")

        # Verificar se há tarefas que seriam consideradas atrasadas pela lógica antiga
        print("\n🔍 Verificação adicional:")
        tarefas_atrasadas_antiga_logica = 0
        for tarefa in tarefas:
            status = tarefa.get('status', '')
            if status.lower() not in ['concluido', 'concluida', 'concluído', 'concluída']:
                data_fim = tarefa.get('data_fim')
                if data_fim:
                    try:
                        data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
                        if data_fim_dt < datetime.now(data_fim_dt.tzinfo):
                            tarefas_atrasadas_antiga_logica += 1
                            print(f"   ⚠️  Tarefa que seria atrasada pela lógica antiga: {tarefa.get('nome', '')}")
                    except:
                        pass

        print(f"   Tarefas que seriam atrasadas pela lógica antiga: {tarefas_atrasadas_antiga_logica}")

        if tarefas_atrasadas_antiga_logica > 0 and tarefas_atrasadas == 0:
            print("✅ CONFIRMADO: A lógica antiga estava errada - a correção foi necessária!")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    teste_correcao_status()