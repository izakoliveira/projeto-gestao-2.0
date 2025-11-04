import requests
import pandas as pd
from io import BytesIO

def testar_exportacao_multiplos_projetos():
    """Teste para verificar se múltiplos projetos estão sendo exportados"""
    
    print("🧪 Testando exportação de múltiplos projetos...")
    
    # Teste 1: Exportar TODOS os projetos (sem filtro)
    print("\n📋 TESTE 1: Exportar todos os projetos")
    response = requests.post(
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
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Analisar o Excel
        xl_file = pd.ExcelFile(BytesIO(response.content))
        abas = xl_file.sheet_names
        
        print(f"📑 Abas encontradas: {abas}")
        
        # Verificar aba Dados
        if 'Dados' in abas:
            df_dados = pd.read_excel(BytesIO(response.content), sheet_name='Dados')
            projetos_unicos = df_dados['Projeto'].nunique() if 'Projeto' in df_dados.columns else 0
            print(f"   📊 Aba 'Dados': {len(df_dados)} linhas, {projetos_unicos} projetos únicos")
            
            if projetos_unicos > 1:
                print("   ✅ MÚLTIPLOS PROJETOS na aba Dados!")
            else:
                print("   ❌ Apenas 1 projeto na aba Dados")
        
        # Contar abas de projetos individuais (excluindo 'Dados')
        abas_projetos = [aba for aba in abas if aba != 'Dados']
        print(f"   📁 Abas de projetos individuais: {len(abas_projetos)}")
        
        if len(abas_projetos) > 1:
            print("   ✅ MÚLTIPLAS ABAS de projetos individuais!")
            for aba in abas_projetos[:5]:  # Mostrar até 5
                print(f"      - {aba}")
        else:
            print("   ❌ Apenas 1 aba de projeto individual")
            
        # Salvar arquivo para análise
        with open('teste_multiplos_projetos.xlsx', 'wb') as f:
            f.write(response.content)
        print("💾 Arquivo salvo como 'teste_multiplos_projetos.xlsx'")
        
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text[:300])

if __name__ == "__main__":
    testar_exportacao_multiplos_projetos()