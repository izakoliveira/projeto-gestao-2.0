#!/usr/bin/env python3
"""
Teste do statusMap para verificar se 'pendente' está sendo mapeado corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.database import supabase
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

def teste_status_map():
    """Testa se o statusMap está funcionando corretamente"""

    print("🧪 Testando mapeamento de status para carimbo...")

    # Simular o statusMap do JavaScript
    statusMap = {
        'atrasado': { 'projeto': 'atrasado', 'texto': 'ATRASADO', 'cor': '#dc3545', 'borda': 'border-left: 4px solid #dc3545;' },
        'emprogresso': { 'projeto': 'emprogresso', 'texto': 'EM PROGRESSO', 'cor': '#17a2b8', 'borda': 'border-left: 4px solid #17a2b8;' },
        'concluido': { 'projeto': 'concluido', 'texto': 'CONCLUÍDO', 'cor': '#28a745', 'borda': 'border-left: 4px solid #28a745;' },
        'concluida': { 'projeto': 'concluido', 'texto': 'CONCLUÍDO', 'cor': '#28a745', 'borda': 'border-left: 4px solid #28a745;' },
        'pendente': { 'projeto': 'pendente', 'texto': 'PENDENTE', 'cor': '#ffc107', 'borda': 'border-left: 4px solid #ffc107;' },
        'normal': { 'projeto': 'normal', 'texto': 'NORMAL', 'cor': '#6c757d', 'borda': 'border-left: 4px solid #6c757d;' }
    }

    # Buscar projetos com diferentes status
    response = supabase.table('projetos').select('id, nome, status').execute()
    projetos = response.data

    print(f"📊 Testando mapeamento para {len(projetos)} projetos:")

    for projeto in projetos[:10]:  # Testa apenas os primeiros 10
        status_banco = projeto.get('status', '').lower()
        status_norm = status_banco.replace(' ', '')

        status_info = statusMap.get(status_norm, { 'projeto': 'normal', 'texto': 'NORMAL', 'cor': '#6c757d', 'borda': 'border-left: 4px solid #6c757d;' })

        classe_css = f"status-{status_info['projeto']}"
        texto_carimbo = status_info['texto']

        print(f"  📌 {projeto['nome'][:30]:<30} | Banco: {status_banco:<12} | Classe CSS: {classe_css:<15} | Carimbo: {texto_carimbo}")

    # Verificar especificamente projetos pendentes
    print("\n🎯 Projetos com status 'pendente':")
    projetos_pendentes = [p for p in projetos if p.get('status', '').lower() == 'pendente']

    for projeto in projetos_pendentes[:3]:
        status_norm = 'pendente'
        status_info = statusMap.get(status_norm)
        if status_info:
            classe_css = f"status-{status_info['projeto']}"
            print(f"  ✅ {projeto['nome']} -> Classe CSS: {classe_css} (deve mostrar carimbo amarelo)")
        else:
            print(f"  ❌ {projeto['nome']} -> Status 'pendente' não encontrado no statusMap!")

if __name__ == "__main__":
    teste_status_map()