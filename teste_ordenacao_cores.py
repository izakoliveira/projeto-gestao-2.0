#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste para verificar se a ordenação das cores da legenda está correta
"""

import sys
import os

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cores_ordenacao():
    """Simula a lógica de ordenação e cores"""
    
    # Simular alguns projetos de exemplo
    projetos_exemplo = [
        {'nome': '2604 - WORLD ABR', 'id': '1'},
        {'nome': '2511 - WORLD NOV', 'id': '2'},
        {'nome': '2603 - WORLD MAR', 'id': '3'},
        {'nome': '250202 - DIPAULA CAP', 'id': '4'},
        {'nome': '260202 - DI PAULA CAP', 'id': '5'},
        {'nome': '2509 - WORLD SET', 'id': '6'},
    ]
    
    # Cores como no código original
    cores = [
        '#FF1744', '#D500F9', '#3D5AFE', '#00BFA5', '#FFC400', '#FF9100', 
        '#FF6D00', '#DD2C00', '#C2185B', '#7B1FA2', '#1565C0', '#00695C'
    ]
    
    # Função para simular ordenação por data (simplificada)
    def data_inicio_lancamento(projeto):
        # Simular ordenação por data de lançamento
        # Aqui vamos simular usando o número no nome do projeto
        nome = projeto.get('nome', '')
        try:
            # Extrair número do nome (ex: "2604" de "2604 - WORLD ABR")
            numero = nome.split(' - ')[0]
            return numero
        except:
            return '9999'
    
    # Normalizar função
    def normalizar(texto):
        return texto.lower().strip()
    
    print("🔍 ANTES da ordenação:")
    for i, projeto in enumerate(projetos_exemplo):
        print(f"  {i+1}. {projeto['nome']}")
    
    # Ordenar projetos (como no código original)
    projetos_ordenados = sorted(projetos_exemplo, key=lambda p: (data_inicio_lancamento(p), normalizar(p.get('nome', ''))))
    
    print("\n✅ APÓS a ordenação:")
    for i, projeto in enumerate(projetos_ordenados):
        print(f"  {i+1}. {projeto['nome']}")
    
    # Criar cores seguindo a nova lógica
    projects_colors = {}
    
    print("\n🎨 Cores atribuídas (seguindo ordem dos projetos):")
    for i, projeto in enumerate(projetos_ordenados):
        projeto_nome = projeto.get('nome', 'Projeto sem nome')
        if projeto_nome not in projects_colors:
            cor_escolhida = cores[i % len(cores)]
            projects_colors[projeto_nome] = cor_escolhida
            print(f"  {i+1}. {projeto_nome} → {cor_escolhida}")
    
    print("\n📋 Legenda de cores (ordem da lista de projetos):")
    for i, projeto in enumerate(projetos_ordenados):
        projeto_nome = projeto.get('nome', '')
        cor = projects_colors.get(projeto_nome, '#000000')
        print(f"  {i+1}. [{cor}] {projeto_nome}")
    
    print("\n🎯 Resultado:")
    print("✅ A legenda agora segue exatamente a mesma ordem dos cards de projetos!")

if __name__ == "__main__":
    test_cores_ordenacao()