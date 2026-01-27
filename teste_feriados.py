from utils.dias_uteis import obter_feriados_banco
from config.database import supabase

print('Testando função obter_feriados_banco()...')
feriados = obter_feriados_banco()
print(f'Tipo retornado: {type(feriados)}')
print(f'Número de feriados: {len(feriados)}')
print('Primeiros 5 feriados:')
for i, (data, nome) in enumerate(list(feriados.items())[:5]):
    print(f'  {data}: {nome}')

print('\nTestando consulta direta ao Supabase...')
try:
    result = supabase.table('feriados').select('data, nome').execute()
    print(f'Resultado da consulta: {len(result.data) if result.data else 0} registros')
    if result.data:
        for item in result.data[:3]:
            print(f'  {item["data"]}: {item["nome"]}')
except Exception as e:
    print(f'Erro na consulta: {e}')