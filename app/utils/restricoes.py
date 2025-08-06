"""
Gerenciamento de restrições de funcionalidades
==============================================
"""

import json
import os

RESTRICOES_PATH = 'restricoes.json'

def carregar_restricoes():
    """Carrega as restrições do arquivo JSON"""
    try:
        with open(RESTRICOES_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def salvar_restricoes(restricoes):
    """Salva as restrições no arquivo JSON"""
    with open(RESTRICOES_PATH, 'w') as f:
        json.dump(restricoes, f)

def adicionar_restricoes_padrao(usuario_id):
    """Adiciona restrições padrão para um novo usuário"""
    restricoes = carregar_restricoes()
    restricoes_padrao = {
        'restr_criar_projeto': False,
        'restr_editar_projeto': False,
        'restr_excluir_projeto': False,
        'restr_criar_tarefa': False,
        'restr_editar_tarefa': False,
        'restr_excluir_tarefa': False,
        'restr_editar_responsavel': False,
        'restr_editar_duracao': False,
        'restr_editar_datas': False,
        'restr_editar_predecessoras': False,
        'restr_editar_nome_tarefa': False
    }
    restricoes[str(usuario_id)] = restricoes_padrao
    salvar_restricoes(restricoes)

def verificar_restricao(usuario_id, nome_restricao):
    """Verifica se uma funcionalidade está restrita para o usuário"""
    restricoes = carregar_restricoes()
    restricoes_usuario = restricoes.get(str(usuario_id), {})
    return restricoes_usuario.get(f'restr_{nome_restricao}', False) 