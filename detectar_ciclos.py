# Script para detectar ciclos nas dependências das tarefas

from supabase import create_client
import os

# Configure suas variáveis de ambiente ou coloque direto aqui
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://zvdpuxggltqejplybzet.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2ZHB1eGdnbHRxZWpwbHliemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTcyOTAsImV4cCI6MjA2NTMzMzI5MH0.YaDt2gAl_FFolp8Gh5n18ZjwzkLLcQ2EuWzFZTTyEMI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_tarefas(projeto_id):
    resp = supabase.table("tarefas").select("id, nome, predecessoras").eq("projeto_id", projeto_id).execute()
    return resp.data if hasattr(resp, 'data') else []

def extrair_ids_predecessoras(predecessoras_str):
    """
    Extrai apenas os IDs das predecessoras do formato ProjectLibre (ex: '2FS+2d;3SS-1d').
    """
    ids = []
    if not predecessoras_str:
        return ids
    for pred in predecessoras_str.split(';'):
        pred = pred.strip()
        if not pred:
            continue
        # Pega tudo antes de FS, SS, FF, SF
        for tipo in ['FS', 'SS', 'FF', 'SF']:
            if tipo in pred:
                ids.append(pred.split(tipo)[0])
                break
        else:
            ids.append(pred)
    return [id_.strip() for id_ in ids if id_]

def build_graph(tarefas):
    ordem_para_id = {str(t['ordem']): t['id'] for t in tarefas}
    grafo = {}
    for t in tarefas:
        preds = []
        if t.get('predecessoras'):
            for pred in extrair_ids_predecessoras(t['predecessoras']):
                pred_id = ordem_para_id.get(pred, pred)
                preds.append(pred_id)
        grafo[t['id']] = preds
    return grafo

def encontrar_ciclo(grafo):
    caminho = []
    visitados = set()
    def dfs(v, pilha):
        visitados.add(v)
        pilha.append(v)
        for vizinho in grafo.get(v, []):
            if vizinho not in visitados:
                if dfs(vizinho, pilha):
                    return True
            elif vizinho in pilha:
                pilha.append(vizinho)
                return True
        pilha.pop()
        return False
    for v in grafo:
        if v not in visitados:
            pilha = []
            if dfs(v, pilha):
                # Encontrou ciclo, extrair apenas o ciclo
                ciclo = []
                if pilha:
                    ultimo = pilha[-1]
                    for node in reversed(pilha[:-1]):
                        ciclo.append(node)
                        if node == ultimo:
                            break
                    ciclo = list(reversed(ciclo)) + [ultimo]
                return ciclo
    return None

def detect_cycles(tarefas):
    grafo = build_graph(tarefas)
    ciclo = encontrar_ciclo(grafo)
    return ciclo

def remover_auto_dependencias(tarefas, projeto_id):
    alteradas = 0
    for t in tarefas:
        id_tarefa = t['id']
        predecessoras = t.get('predecessoras')
        if not predecessoras:
            continue
        preds = predecessoras.split(';')
        novos_preds = []
        for pred in preds:
            pred_limpo = pred.strip()
            if not pred_limpo:
                continue
            # Extrai apenas o número/id da predecessora
            for tipo in ['FS', 'SS', 'FF', 'SF']:
                if tipo in pred_limpo:
                    pred_id = pred_limpo.split(tipo)[0].strip()
                    break
            else:
                pred_id = pred_limpo
            if pred_id != id_tarefa:
                novos_preds.append(pred_limpo)
        if len(novos_preds) != len(preds):
            nova_str = ';'.join(novos_preds)
            # Atualiza no Supabase
            supabase.table("tarefas").update({"predecessoras": nova_str}).eq("id", id_tarefa).execute()
            print(f"Auto-dependência removida da tarefa {t['nome']} ({id_tarefa})")
            alteradas += 1
    print(f"Total de tarefas corrigidas: {alteradas}")

def mostrar_mapeamento_e_predecessoras(tarefas):
    print("\n--- Mapeamento de tarefas (ordem, nome, ID) ---")
    for t in tarefas:
        print(f"{t['ordem']}: {t['nome']} ({t['id']}) | predecessoras: {t.get('predecessoras','')}")
    print("\n--- Interpretação das predecessoras ---")
    ordem_para_id = {str(t['ordem']): t['id'] for t in tarefas}
    for t in tarefas:
        preds = t.get('predecessoras')
        if not preds:
            continue
        print(f"Tarefa: {t['nome']} ({t['id']})")
        for pred in preds.split(';'):
            pred = pred.strip()
            if not pred:
                continue
            for tipo in ['FS', 'SS', 'FF', 'SF']:
                if tipo in pred:
                    pred_num = pred.split(tipo)[0]
                    break
            else:
                pred_num = pred
            pred_id = ordem_para_id.get(pred_num, pred_num)
            print(f"  predecessora bruta: '{pred}' | ordem: '{pred_num}' | ID interpretado: '{pred_id}'")

# Exemplo de uso:
if __name__ == '__main__':
    projeto_id = "0f101b88-a90c-4020-8cab-81c445310dc9"
    # Buscar também o campo 'ordem'
    def buscar_tarefas_ordem(projeto_id):
        resp = supabase.table("tarefas").select("id, nome, predecessoras, ordem").eq("projeto_id", projeto_id).execute()
        return resp.data if hasattr(resp, 'data') else []
    tarefas = buscar_tarefas_ordem(projeto_id)
    print(f"Total de tarefas encontradas: {len(tarefas)}")
    mostrar_mapeamento_e_predecessoras(tarefas)
    ciclo = detect_cycles(tarefas)
    if ciclo:
        print('Ciclo detectado nas dependências!')
        print('IDs das tarefas no ciclo:', ' -> '.join(ciclo))
        id_para_nome = {t['id']: t['nome'] for t in tarefas}
        print('Nomes das tarefas no ciclo:')
        for id_ in ciclo:
            print(f"- {id_para_nome.get(id_, id_)} ({id_})")
    else:
        print('Nenhum ciclo detectado.')
    print("\nRemovendo auto-dependências...")
    remover_auto_dependencias(tarefas, projeto_id) 