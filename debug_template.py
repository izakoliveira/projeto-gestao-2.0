#!/usr/bin/env python3
"""
Debug dos templates de email
Testa isoladamente a geração dos templates HTML
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.append('.')

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variáveis de ambiente carregadas")
except ImportError:
    print("❌ dotenv não disponível")

def test_template_generation():
    """Testa a geração de templates isoladamente"""
    
    print("\n🔍 TESTANDO GERAÇÃO DE TEMPLATES")
    print("=" * 50)
    
    try:
        # Importar o módulo de notificações
        from utils.email_notifications import email_notifier
        print("✅ Módulo importado com sucesso")
        
        # Testar template base
        print("\n📝 Testando template base...")
        base_html = email_notifier._get_email_template('tarefa_designada',
            usuario_nome='Usuário Teste',
            tarefa_nome='Tarefa de Teste',
            projeto_nome='Projeto Teste',
            data_inicio='01/01/2025',
            data_fim='31/01/2025',
            duracao='30 dias',
            colecao='Coleção Teste',
            projeto_url='http://localhost:5000/projetos/123'
        )
        
        print(f"✅ Template gerado com sucesso!")
        print(f"📏 Tamanho: {len(base_html)} caracteres")
        print(f"🔍 Primeiros 200 caracteres:")
        print("-" * 50)
        print(base_html[:200])
        print("-" * 50)
        
        # Verificar se contém elementos esperados
        if 'font-family' in base_html:
            print("✅ CSS font-family encontrado no template")
        else:
            print("❌ CSS font-family NÃO encontrado no template")
            
        if 'Arial, Helvetica, sans-serif' in base_html:
            print("✅ Fonte Arial encontrada no template")
        else:
            print("❌ Fonte Arial NÃO encontrada no template")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar template: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_template():
    """Testa um template HTML simples sem formatação complexa"""
    
    print("\n🧪 TESTANDO TEMPLATE SIMPLES")
    print("=" * 50)
    
    try:
        # Template HTML simples
        simple_template = """<!DOCTYPE html>
<html>
<head>
    <title>Teste</title>
    <style>
        body { font-family: Arial, sans-serif; }
    </style>
</head>
<body>
    <h1>Teste</h1>
    <p>Olá {nome}</p>
</body>
</html>"""
        
        # Testar formatação
        formatted = simple_template.format(nome="Mundo")
        print("✅ Template simples formatado com sucesso")
        print(f"📏 Tamanho: {len(formatted)} caracteres")
        
        if 'font-family' in formatted:
            print("✅ CSS font-family encontrado no template simples")
        else:
            print("❌ CSS font-family NÃO encontrado no template simples")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no template simples: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_encoding():
    """Testa a codificação do arquivo de notificações"""
    
    print("\n🔤 TESTANDO CODIFICAÇÃO DO ARQUIVO")
    print("=" * 50)
    
    try:
        with open('utils/email_notifications.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"✅ Arquivo lido com sucesso")
        print(f"📏 Tamanho: {len(content)} caracteres")
        
        # Verificar caracteres especiais
        special_chars = []
        for i, char in enumerate(content):
            if ord(char) > 127:
                special_chars.append((i, char, ord(char)))
                
        if special_chars:
            print(f"⚠️  Caracteres especiais encontrados: {len(special_chars)}")
            for pos, char, code in special_chars[:5]:  # Mostrar apenas os primeiros 5
                print(f"   Posição {pos}: '{char}' (código {code})")
        else:
            print("✅ Nenhum caractere especial encontrado")
            
        # Verificar se contém o CSS problemático
        if 'font-family' in content:
            print("✅ CSS font-family encontrado no arquivo")
            # Encontrar a linha exata
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'font-family' in line:
                    print(f"   Linha {i+1}: {line.strip()}")
        else:
            print("❌ CSS font-family NÃO encontrado no arquivo")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DEBUG DOS TEMPLATES DE EMAIL")
    print("=" * 50)
    
    # Testar codificação do arquivo
    test_file_encoding()
    
    # Testar template simples
    test_simple_template()
    
    # Testar geração de templates
    test_template_generation()
    
    print("\n🏁 Debug concluído!")
