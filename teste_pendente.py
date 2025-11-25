import sys
sys.path.append('.')
from config.database import supabase

# Buscar projetos com status pendente
response = supabase.table('projetos').select('id, nome, status').eq('status', 'pendente').execute()
projetos_pendentes = response.data

print(f'Encontrados {len(projetos_pendentes)} projetos com status pendente:')
for projeto in projetos_pendentes[:5]:  # Mostra apenas os primeiros 5
    print(f'  - {projeto["id"]}: {projeto["nome"]} (status: {projeto["status"]})')