import pandas as pd

def analisar_relatorio_excel():
    print("📊 Analisando relatorio_gantt.xlsx...")
    
    try:
        xl_file = pd.ExcelFile('relatorio_gantt.xlsx')
        abas = xl_file.sheet_names
        print(f"📑 Abas encontradas: {abas}")
        print(f"📈 Total de abas: {len(abas)}")
        
        for i, aba in enumerate(abas):
            print(f"\n📋 Aba {i+1}: \"{aba}\"")
            df = pd.read_excel('relatorio_gantt.xlsx', sheet_name=aba)
            print(f"   📏 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            
            if len(df.columns) > 0:
                print(f"   📝 Colunas: {list(df.columns)}")
                
            if len(df) > 0:
                print("   📄 Primeiras 3 linhas:")
                for idx, row in df.head(3).iterrows():
                    print(f"      Linha {idx}: {dict(row)}")
            else:
                print("   📄 Aba vazia")
                
        # Análise especial da aba 'Dados' se existir
        if 'Dados' in abas:
            print(f"\n🎯 ANÁLISE ESPECIAL - Aba 'Dados':")
            df_dados = pd.read_excel('relatorio_gantt.xlsx', sheet_name='Dados')
            
            if 'Projeto' in df_dados.columns:
                projetos_unicos = df_dados['Projeto'].unique()
                print(f"   🏢 Projetos únicos: {len(projetos_unicos)}")
                for projeto in projetos_unicos:
                    count = len(df_dados[df_dados['Projeto'] == projeto])
                    print(f"      - {projeto}: {count} tarefas")
            
        # Análise das abas de projetos individuais
        abas_projetos = [aba for aba in abas if aba != 'Dados']
        if abas_projetos:
            print(f"\n🏗️ ABAS DE PROJETOS INDIVIDUAIS ({len(abas_projetos)}):")
            for aba in abas_projetos:
                df_projeto = pd.read_excel('relatorio_gantt.xlsx', sheet_name=aba)
                print(f"   📁 {aba}: {len(df_projeto)} tarefas")
                
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    analisar_relatorio_excel()