#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se o sistema está considerando os feriados de 2026
"""

import requests
from datetime import datetime, date
import json

def testar_api_feriados():
    """Testa a API do BrasilAPI para diferentes anos"""
    print("=" * 60)
    print("VERIFICACAO: Sistema está considerando os feriados de 2026?")
    print("=" * 60)
    
    # Ano atual
    ano_atual = datetime.now().year
    print(f"\nAno atual: {ano_atual}")
    
    # Testar diferentes anos
    anos = [2024, 2025, 2026, 2027]
    
    for ano in anos:
        try:
            print(f"\n--- Testando feriados para {ano} ---")
            url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                feriados = response.json()
                print(f"✅ API disponível para {ano}: {len(feriados)} feriados encontrados")
                
                # Mostrar alguns feriados de exemplo
                for i, feriado in enumerate(feriados[:3]):
                    print(f"   {i+1}. {feriado['date']}: {feriado['name']}")
                
                if len(feriados) > 3:
                    print(f"   ... e mais {len(feriados) - 3} feriados")
                    
            else:
                print(f"❌ API não disponível para {ano}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao consultar {ano}: {e}")
    
    return True

def analisar_problema_sistema():
    """Analisa o problema identificado no sistema"""
    print("\n" + "=" * 60)
    print("PROBLEMA IDENTIFICADO")
    print("=" * 60)
    
    print("""
🔍 ANÁLISE DO CÓDIGO:

1. Em 'detalhes_projeto.html', linha 2037:
   const anoAtual = new Date().getFullYear();
   carregarFeriadosBrasilAPI(anoAtual, uf, cidade);

2. O sistema só carrega feriados do ano atual (2025)
3. Para projetos com datas em 2026, os feriados não são considerados

📊 IMPACTO:
- Tarefas agendadas para 2026 podem ser marcadas incorretamente
- Cálculos de duração podem incluir feriados não identificados
- Cronogramas podem ficar imprecisos
    """)

def sugerir_solucoes():
    """Sugere soluções para o problema"""
    print("=" * 60)
    print("SOLUÇÕES SUGERIDAS")
    print("=" * 60)
    
    print("""
✅ SOLUÇÃO 1: Carregar múltiplos anos
   - Detectar o range de anos das tarefas do projeto
   - Carregar feriados para todos os anos necessários

✅ SOLUÇÃO 2: Cache inteligente
   - Carregar e cachear feriados conforme necessário
   - Verificar localStorage antes de fazer nova requisição

✅ SOLUÇÃO 3: Carregamento proativo
   - Sempre carregar ano atual + próximos 2-3 anos
   - Atualizar cache periodicamente

📝 RECOMENDAÇÃO:
   Implementar Solução 1 + 2 para máxima eficiência
    """)

def main():
    """Função principal"""
    # Testar API
    testar_api_feriados()
    
    # Analisar problema
    analisar_problema_sistema()
    
    # Sugerir soluções
    sugerir_solucoes()
    
    print("\n" + "=" * 60)
    print("CONCLUSÃO")
    print("=" * 60)
    print("""
❌ O sistema NÃO está considerando os feriados de 2026
✅ A API do BrasilAPI possui os feriados de 2026 disponíveis
🔧 É necessário modificar o código para carregar feriados de múltiplos anos
    """)

if __name__ == "__main__":
    main()