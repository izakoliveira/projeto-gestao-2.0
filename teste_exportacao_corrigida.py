import requests
import json
import pandas as pd
from io import BytesIO

def testar_exportacao_corrigida():
    print("🧪 Testando exportação Excel corrigida...")
    
    # URL do endpoint
    url = "http://localhost:5000/relatorio/gantt_excel"
    
    # Dados para teste - simular múltiplos projetos
    data = {
        "gantt_base64": "",
        "projeto_ids": [],  # Vazio = todos os projetos
        "status": [],
        "colecao": [],
        "data_inicio": "",
        "data_fim": ""
    }
    
    print(f"📤 Enviando requisição POST para: {url}")
    print(f"📝 Dados: {data}")
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Requisição bem-sucedida!")
            
            # Salvar arquivo para análise
            with open('teste_export_corrigido.xlsx', 'wb') as f:
                f.write(response.content)
            
            print("💾 Arquivo salvo como 'teste_export_corrigido.xlsx'")
            
            # Analisar o arquivo Excel
            try:
                xl_file = pd.ExcelFile(BytesIO(response.content))
                abas = xl_file.sheet_names
                
                print(f"📑 Abas encontradas: {abas}")
                
                for aba in abas:
                    df = pd.read_excel(BytesIO(response.content), sheet_name=aba)
                    print(f"   📋 Aba '{aba}': {len(df)} linhas, {len(df.columns)} colunas")
                    if len(df) > 0:
                        print(f"      Colunas: {list(df.columns)}")
                
                # Verificar se tem múltiplas abas
                if len(abas) > 1:
                    print("✅ SUCESSO: Múltiplas abas foram criadas!")
                else:
                    print("❌ PROBLEMA: Apenas uma aba foi criada")
                
                # Verificar aba de projetos
                if 'Projetos' in abas:
                    df_projetos = pd.read_excel(BytesIO(response.content), sheet_name='Projetos')
                    print(f"✅ Aba 'Projetos' encontrada com {len(df_projetos)} projetos")
                else:
                    print("❌ Aba 'Projetos' não encontrada")
                
                # Verificar aba de tarefas
                if 'Tarefas' in abas:
                    df_tarefas = pd.read_excel(BytesIO(response.content), sheet_name='Tarefas')
                    projetos_unicos = df_tarefas['Projeto'].nunique() if 'Projeto' in df_tarefas.columns else 0
                    print(f"✅ Aba 'Tarefas' encontrada com {len(df_tarefas)} tarefas de {projetos_unicos} projetos diferentes")
                else:
                    print("❌ Aba 'Tarefas' não encontrada")
                    
            except Exception as e:
                print(f"❌ Erro ao analisar arquivo Excel: {e}")
                
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    testar_exportacao_corrigida()