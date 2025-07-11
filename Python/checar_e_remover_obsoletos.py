import os
import re
import sys

"""
Uso:
    python checar_e_remover_obsoletos.py           # Checa e, se desejar, remove arquivos obsoletos
    python checar_e_remover_obsoletos.py --detalhado  # Busca também por referências parciais (nome sem extensão)
    python checar_e_remover_obsoletos.py --rapido     # Força modo rápido
"""

DETALHADO = '--detalhado' in sys.argv
RAPIDO = '--rapido' in sys.argv or not DETALHADO
IGNORAR_DIRS = {'venv', 'env', '.venv', '__pycache__'}
IGNORAR_ARQUIVOS = {
    'app.py',
    'requirements.txt',
    'env_example.txt',
    'git_auto_commit.py',
    'verificar_colecoes.py',
    'limpar_colecoes.py',
    'checar_e_remover_obsoletos.py',
    'supabase_client.py',
}

# Função utilitária para buscar arquivos recursivamente, ignorando ambientes virtuais
def listar_arquivos(caminho, extensoes):
    arquivos = []
    for root, dirs, files in os.walk(caminho):
        # Remove dirs a ignorar in-place
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS]
        for f in files:
            if any(f.endswith(ext) for ext in extensoes):
                arquivos.append(os.path.relpath(os.path.join(root, f)))
    return arquivos

# Função para buscar referência (exata ou parcial) e mostrar onde encontrou
def buscar_referencias(arquivo, arquivos_busca, detalhado=False):
    referencias = []
    nome = os.path.basename(arquivo)
    nome_sem_ext = os.path.splitext(nome)[0]
    for f in arquivos_busca:
        with open(f, encoding='utf-8') as fh:
            content = fh.read()
            if nome in content:
                referencias.append(f)
            elif detalhado and nome_sem_ext in content:
                referencias.append(f + ' (parcial)')
    return referencias

# 1. Checar arquivos Python não importados (considerando subpastas)
py_files = [f for f in listar_arquivos('.', ['.py']) if os.path.basename(f) not in IGNORAR_ARQUIVOS]
imports = set()

for fname in listar_arquivos('.', ['.py']):
    if os.path.basename(fname) not in IGNORAR_ARQUIVOS:
        with open(fname, encoding='utf-8') as f:
            content = f.read()
            found = re.findall(r'import ([\w_]+)|from ([\w_]+) import', content)
            for imp1, imp2 in found:
                if imp1:
                    imports.add(imp1 + '.py')
                if imp2:
                    imports.add(imp2 + '.py')

obsoletos = []
print('=== Arquivos Python potencialmente obsoletos ===')
for py in py_files:
    if os.path.basename(py) not in imports:
        refs = buscar_referencias(py, listar_arquivos('.', ['.py']), detalhado=DETALHADO and not RAPIDO)
        if not refs:
            print(f'- {py} (NENHUMA referência encontrada)')
            obsoletos.append(py)
        elif DETALHADO and not RAPIDO:
            print(f'- {py} (referências encontradas em: {refs})')
if not py_files:
    print('Nenhum arquivo Python extra encontrado.')

# 2. Checar HTML em static/ não referenciados em nenhum HTML do projeto (static/ ou templates/)
static_htmls = listar_arquivos('static', ['.html'])
all_htmls = static_htmls + listar_arquivos('templates', ['.html'])
print('\n=== Arquivos HTML em static/ potencialmente obsoletos ===')
for shtml in static_htmls:
    refs = buscar_referencias(shtml, all_htmls, detalhado=DETALHADO and not RAPIDO)
    if not refs:
        print(f'- {shtml} (NENHUMA referência encontrada)')
        obsoletos.append(shtml)
    elif DETALHADO and not RAPIDO:
        print(f'- {shtml} (referências encontradas em: {refs})')
if not static_htmls:
    print('Nenhum HTML extra em static/.')

# 3. Checar templates HTML não utilizados (nem por Python nem por outros templates)
template_htmls = listar_arquivos('templates', ['.html'])
print('\n=== Templates HTML potencialmente obsoletos ===')
for tfile in template_htmls:
    refs_py = buscar_referencias(tfile, listar_arquivos('.', ['.py']), detalhado=DETALHADO and not RAPIDO)
    refs_html = buscar_referencias(tfile, template_htmls, detalhado=DETALHADO and not RAPIDO)
    if not refs_py and not refs_html:
        print(f'- {tfile} (NENHUMA referência encontrada)')
        obsoletos.append(tfile)
    elif DETALHADO and not RAPIDO and (refs_py or refs_html):
        print(f'- {tfile} (referências encontradas em: {refs_py + refs_html})')
if not template_htmls:
    print('Nenhum template HTML extra.')

# 4. Checar arquivos CSS/JS em static/ não referenciados em nenhum HTML do projeto
static_css = listar_arquivos('static', ['.css'])
static_js = listar_arquivos('static', ['.js'])
print('\n=== Arquivos CSS em static/ potencialmente obsoletos ===')
for css in static_css:
    refs = buscar_referencias(css, all_htmls, detalhado=DETALHADO and not RAPIDO)
    if not refs:
        print(f'- {css} (NENHUMA referência encontrada)')
        obsoletos.append(css)
    elif DETALHADO and not RAPIDO:
        print(f'- {css} (referências encontradas em: {refs})')
if not static_css:
    print('Nenhum CSS extra em static/.')

print('\n=== Arquivos JS em static/ potencialmente obsoletos ===')
for js in static_js:
    refs = buscar_referencias(js, all_htmls, detalhado=DETALHADO and not RAPIDO)
    if not refs:
        print(f'- {js} (NENHUMA referência encontrada)')
        obsoletos.append(js)
    elif DETALHADO and not RAPIDO:
        print(f'- {js} (referências encontradas em: {refs})')
if not static_js:
    print('Nenhum JS extra em static/.')

# 5. Checar arquivos JSON/TXT não utilizados
json_txt_files = [f for f in os.listdir('.') if f.endswith('.json') or f.endswith('.txt')]
print('\n=== Arquivos JSON/TXT potencialmente obsoletos ===')
for jfile in json_txt_files:
    refs = buscar_referencias(jfile, listar_arquivos('.', ['.py']), detalhado=DETALHADO and not RAPIDO)
    if not refs:
        print(f'- {jfile} (NENHUMA referência encontrada)')
        obsoletos.append(jfile)
    elif DETALHADO and not RAPIDO:
        print(f'- {jfile} (referências encontradas em: {refs})')
if not json_txt_files:
    print('Nenhum JSON/TXT extra.')

# Pergunta se deseja remover arquivos obsoletos encontrados
if obsoletos:
    print('\nArquivos sem referência encontrados:')
    for arq in obsoletos:
        print(f'  - {arq}')
    resp = input('\nDeseja remover TODOS esses arquivos? (s/n): ').strip().lower()
    if resp == 's':
        for arq in obsoletos:
            if os.path.exists(arq):
                os.remove(arq)
                print(f'Removido: {arq}')
            else:
                print(f'Não encontrado (já removido?): {arq}')
        print('\nRemoção concluída.')
    else:
        print('Nenhum arquivo foi removido.')
else:
    print('\nNenhum arquivo obsoleto para remover!') 