#!/usr/bin/env python3
"""
Script de teste para verificar se o background do painel de filtros está correto no modo escuro
"""

import requests
from bs4 import BeautifulSoup

def testar_background_filtros():
    """Testa se o background do painel de filtros está correto no modo escuro"""

    try:
        # Fazer requisição para a página de projetos
        response = requests.get('http://localhost:5000/projetos')
        response.raise_for_status()

        # Parsear o HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Procurar pelo painel de filtros
        offcanvas = soup.find(id='offcanvas-filtros-desktop')

        if not offcanvas:
            print("❌ Painel de filtros não encontrado")
            return False

        # Verificar se há estilos CSS para tema escuro
        style_tag = soup.find('style')
        if not style_tag:
            print("❌ Tag de estilo não encontrada")
            return False

        css_content = style_tag.get_text()

        # Verificar se há regras CSS para body.dark #offcanvas-filtros-desktop
        if 'body.dark #offcanvas-filtros-desktop' not in css_content:
            print("❌ Regra CSS para tema escuro do painel de filtros não encontrada")
            return False

        # Verificar se a regra contém background com gradiente escuro
        if 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)' not in css_content:
            print("❌ Gradiente escuro não encontrado na regra CSS")
            return False

        print("✅ Background do painel de filtros corrigido para modo escuro!")
        print("✅ Regra CSS body.dark #offcanvas-filtros-desktop encontrada")
        print("✅ Gradiente escuro aplicado corretamente")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao fazer requisição: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testando correção do background dos filtros no modo escuro...")
    sucesso = testar_background_filtros()

    if sucesso:
        print("\n🎉 Teste passou! O background do painel de filtros deve estar funcionando corretamente no modo escuro.")
    else:
        print("\n❌ Teste falhou! Verifique a implementação da correção.")