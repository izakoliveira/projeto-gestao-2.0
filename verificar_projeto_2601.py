#!/usr/bin/env python3
"""
Verificar tarefas específicas do projeto "2601 - WORLD JAN"
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

def verificar_projeto_2601():
    """Verifica tarefas do projeto 2601 - WORLD JAN"""

    print("🔍 Verificando tarefas do projeto '2601 - WORLD JAN'...")

    try:
        # Primeiro, buscar o projeto pelo nome
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

        print(f"📋 Total de tarefas encontradas: {len(tarefas)}")

        if not tarefas:
            print("⚠️  Nenhuma tarefa encontrada para este projeto!")
            return

        hoje = datetime.now()
        print(f"📅 Data de hoje: {hoje.strftime('%Y-%m-%d')}")
        print()

        tarefas_atrasadas = []
        tarefas_pendentes = []
        tarefas_em_progresso = []
        tarefas_concluidas = []

        print("📝 Lista de todas as tarefas do projeto:")
        print("=" * 80)

        for tarefa in tarefas:
            nome = tarefa.get('nome', 'Sem nome')
            status = tarefa.get('status', 'N/A')
            data_inicio = tarefa.get('data_inicio', 'N/A')
            data_fim = tarefa.get('data_fim', 'N/A')

            # Categorizar tarefas
            if status.lower() == 'pendente':
                tarefas_pendentes.append(tarefa)
            elif status.lower() == 'em progresso':
                tarefas_em_progresso.append(tarefa)
            elif status.lower() in ['concluída', 'concluida']:
                tarefas_concluidas.append(tarefa)

            # Verificar se está atrasada
            atrasada = verificar_tarefa_atrasada(tarefa)

            if atrasada:
                tarefas_atrasadas.append(tarefa)
                print(f"⚠️  ATRASADA: {nome}")
            else:
                print(f"✅ Normal: {nome}")

            print(f"   Status: {status}")
            print(f"   Data início: {data_inicio}")
            print(f"   Data fim: {data_fim}")
            print()

        print("=" * 80)
        print("📊 Resumo do projeto:")
        print(f"   Total de tarefas: {len(tarefas)}")
        print(f"   Tarefas concluídas: {len(tarefas_concluidas)}")
        print(f"   Tarefas em progresso: {len(tarefas_em_progresso)}")
        print(f"   Tarefas pendentes: {len(tarefas_pendentes)}")
        print(f"   Tarefas atrasadas: {len(tarefas_atrasadas)}")

        if tarefas_atrasadas:
            print()
            print("🚨 DETALHES DAS TAREFAS ATRASADAS:")
            for tarefa in tarefas_atrasadas:
                nome = tarefa.get('nome', 'Sem nome')
                status = tarefa.get('status', 'N/A')
                data_fim = tarefa.get('data_fim', 'N/A')

                # Calcular quantos dias de atraso
                atraso_dias = 0
                if data_fim and data_fim != 'N/A':
                    try:
                        data_fim_obj = datetime.strptime(data_fim.split('T')[0], '%Y-%m-%d')
                        if data_fim_obj < hoje:
                            atraso_dias = (hoje.date() - data_fim_obj.date()).days
                    except:
                        pass

                print(f"   • {nome} (Status: {status}, Data fim: {data_fim}) - Atraso: {atraso_dias} dias")

        print()
        print("🎯 Conclusão:")
        if tarefas_atrasadas:
            print(f"   O projeto está ATRASADO porque tem {len(tarefas_atrasadas)} tarefa(s) atrasada(s).")
        else:
            print("   O projeto NÃO está atrasado - todas as tarefas estão dentro do prazo.")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_projeto_2601()