#!/usr/bin/env python3
"""
Script de verificação para testar se o instalador inclui os arquivos atualizados
"""

import sys
import os
from pathlib import Path

def verificar_arquivos_instalador():
    """Verifica se os arquivos atualizados estão presentes no instalador"""
    print("🔍 Verificando arquivos no instalador...")

    if hasattr(sys, '_MEIPASS'):
        print("✓ Executando como executável PyInstaller")
        base_path = Path(sys._MEIPASS)
        projeto_path = base_path / 'projeto_arquivos'

        if projeto_path.exists():
            print("✓ Pasta projeto_arquivos encontrada!")

            # Verificar arquivos específicos que foram atualizados
            arquivos_para_verificar = [
                ('routes/projetos.py', 'Backend com lógica de filtros'),
                ('templates/projetos_gantt_basico.html', 'Frontend com função limparFiltros'),
                ('app_producao.py', 'Aplicação principal'),
                ('supabase_client.py', 'Cliente Supabase'),
            ]

            todos_ok = True
            for arquivo, descricao in arquivos_para_verificar:
                caminho_completo = projeto_path / arquivo
                if caminho_completo.exists():
                    tamanho = caminho_completo.stat().st_size
                    print(f"✓ {arquivo} ({descricao}): {tamanho} bytes")
                else:
                    print(f"✗ {arquivo} ({descricao}): ARQUIVO NÃO ENCONTRADO!")
                    todos_ok = False

            if todos_ok:
                print("\n🎉 Todos os arquivos atualizados estão presentes no instalador!")
                return True
            else:
                print("\n❌ Alguns arquivos estão faltando!")
                return False
        else:
            print("✗ Pasta projeto_arquivos NÃO encontrada!")
            print("Conteúdo do _MEIPASS:")
            for item in base_path.iterdir():
                print(f"  - {item.name}")
            return False
    else:
        print("Executando como script Python normal (não como executável)")
        print("Para testar corretamente, execute o instalador: dist\\Instalador_Sistema_Gestao.exe")
        return False

if __name__ == "__main__":
    verificar_arquivos_instalador()