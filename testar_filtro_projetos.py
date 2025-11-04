import requests
import pandas as pd
from io import BytesIO
import json

def testar_filtro_projetos_especificos():
    """Testa se o filtro de projetos específicos está funcionando"""
    
    print("🧪 Testando filtro de projetos específicos...")
    
    # Primeiro, vamos ver todos os projetos disponíveis
    print("\n📋 TESTE 1: Exportar TODOS os projetos (sem filtro)")
    response_todos = requests.post(
        "http://localhost:5000/relatorio/gantt_excel",
        json={
            "gantt_base64": "",
            "projeto_ids": [],  # Vazio = todos
            "status": [],
            "colecao": [],
            "data_inicio": "",
            "data_fim": ""
        },
        timeout=30
    )
    
    if response_todos.status_code == 200:
        xl_todos = pd.ExcelFile(BytesIO(response_todos.content))
        df_todos = pd.read_excel(BytesIO(response_todos.content), sheet_name='Dados')
        projetos_todos = df_todos['Projeto'].unique()
        
        print(f"✅ Todos os projetos ({len(projetos_todos)}):")
        for i, projeto in enumerate(projetos_todos[:10]):  # Mostrar até 10
            print(f"   {i+1}. {projeto}")
        
        # Agora vamos testar com projetos específicos
        print(f"\n📋 TESTE 2: Exportar apenas os 3 primeiros projetos")
        
        # Vamos simular IDs de projetos (assumindo que são strings UUID)
        # Como não temos os IDs reais, vamos usar os nomes e tentar encontrar os IDs
        
        # Fazer uma requisição para obter dados dos projetos
        try:
            # Tentar usar a API diretamente se houver
            print("🔍 Tentando obter IDs dos projetos...")
            
            # Para este teste, vamos usar nomes de projetos como se fossem IDs
            primeiros_3_projetos = projetos_todos[:3].tolist()
            print(f"📝 Testando com projetos: {primeiros_3_projetos}")
            
            # Simular requisição com projeto_ids específicos
            response_filtrado = requests.post(
                "http://localhost:5000/relatorio/gantt_excel",
                json={
                    "gantt_base64": "",
                    "projeto_ids": primeiros_3_projetos,  # Tentar com nomes
                    "status": [],
                    "colecao": [],
                    "data_inicio": "",
                    "data_fim": ""
                },
                timeout=30
            )
            
            print(f"📊 Status resposta filtrada: {response_filtrado.status_code}")
            
            if response_filtrado.status_code == 200:
                xl_filtrado = pd.ExcelFile(BytesIO(response_filtrado.content))
                df_filtrado = pd.read_excel(BytesIO(response_filtrado.content), sheet_name='Dados')
                projetos_filtrados = df_filtrado['Projeto'].unique()
                
                print(f"\n🎯 RESULTADO DO FILTRO:")
                print(f"   Projetos solicitados: {len(primeiros_3_projetos)}")
                print(f"   Projetos obtidos: {len(projetos_filtrados)}")
                print(f"   Abas criadas: {len(xl_filtrado.sheet_names)}")
                
                print(f"\n📋 Projetos no resultado filtrado:")
                for projeto in projetos_filtrados:
                    print(f"   - {projeto}")
                
                if len(projetos_filtrados) == len(primeiros_3_projetos):
                    print("✅ FILTRO FUNCIONANDO CORRETAMENTE!")
                elif len(projetos_filtrados) == 1:
                    print("❌ PROBLEMA: Apenas 1 projeto retornado")
                elif len(projetos_filtrados) == len(projetos_todos):
                    print("❌ PROBLEMA: Todos os projetos retornados (filtro ignorado)")
                else:
                    print("⚠️ PROBLEMA: Número inesperado de projetos")
                    
            else:
                print(f"❌ Erro na requisição filtrada: {response_filtrado.status_code}")
                print(f"📄 Resposta: {response_filtrado.text[:300]}")
                
        except Exception as e:
            print(f"❌ Erro no teste de filtro: {e}")
    
    else:
        print(f"❌ Erro ao obter todos os projetos: {response_todos.status_code}")

if __name__ == "__main__":
    testar_filtro_projetos_especificos()