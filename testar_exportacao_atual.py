import requests
import pandas as pd
from io import BytesIO

def testar_exportacao_comparar_com_exemplo():
    """Teste para comparar com o relatorio_gantt.xlsx de exemplo"""
    
    print("🧪 Testando exportação atual e comparando com exemplo...")
    
    # Fazer requisição igual ao exemplo
    response = requests.post(
        "http://localhost:5000/relatorio/gantt_excel",
        json={
            "gantt_base64": "",
            "projeto_ids": [],  # Vazio = todos os projetos
            "status": [],
            "colecao": [],
            "data_inicio": "",
            "data_fim": ""
        },
        timeout=30
    )
    
    print(f"📊 Status da resposta: {response.status_code}")
    
    if response.status_code == 200:
        # Analisar o Excel atual
        xl_file = pd.ExcelFile(BytesIO(response.content))
        abas_atual = xl_file.sheet_names
        
        print(f"\n📑 EXPORTAÇÃO ATUAL:")
        print(f"   Total de abas: {len(abas_atual)}")
        print(f"   Abas: {abas_atual}")
        
        # Verificar aba Dados
        if 'Dados' in abas_atual:
            df_dados = pd.read_excel(BytesIO(response.content), sheet_name='Dados')
            projetos_unicos = df_dados['Projeto'].nunique() if 'Projeto' in df_dados.columns else 0
            print(f"   📊 Aba 'Dados': {len(df_dados)} linhas, {projetos_unicos} projetos únicos")
            
            if projetos_unicos > 1:
                print("   ✅ MÚLTIPLOS PROJETOS detectados!")
                print("   🏢 Projetos encontrados:")
                for projeto in df_dados['Projeto'].unique()[:10]:  # Mostrar até 10
                    count = len(df_dados[df_dados['Projeto'] == projeto])
                    print(f"      - {projeto}: {count} tarefas")
            else:
                print("   ❌ Apenas 1 projeto encontrado")
        
        # Contar abas individuais
        abas_projetos = [aba for aba in abas_atual if aba != 'Dados']
        print(f"   📁 Abas de projetos individuais: {len(abas_projetos)}")
        
        print(f"\n📑 COMPARAÇÃO COM EXEMPLO (relatorio_gantt.xlsx):")
        print(f"   Exemplo tinha: 16 abas (1 'Dados' + 15 projetos)")
        print(f"   Exemplo tinha: 354 linhas na aba 'Dados'")
        print(f"   Exemplo tinha: 15 projetos únicos")
        
        print(f"\n🎯 RESULTADO:")
        if len(abas_atual) >= 16 and projetos_unicos >= 15:
            print("   ✅ EXPORTAÇÃO FUNCIONANDO PERFEITAMENTE!")
            print("   ✅ Múltiplos projetos estão sendo exportados!")
        elif len(abas_atual) == 1:
            print("   ❌ PROBLEMA: Apenas 1 aba sendo criada")
        elif projetos_unicos <= 1:
            print("   ❌ PROBLEMA: Apenas 1 projeto na aba Dados")
        else:
            print("   ⚠️  Funcionando parcialmente")
            
        # Salvar para análise
        with open('teste_exportacao_atual.xlsx', 'wb') as f:
            f.write(response.content)
        print("💾 Arquivo atual salvo como 'teste_exportacao_atual.xlsx'")
        
    else:
        print(f"❌ Erro na requisição: {response.status_code}")
        print(f"📄 Resposta: {response.text[:300]}")

if __name__ == "__main__":
    testar_exportacao_comparar_com_exemplo()