#!/usr/bin/env python3
"""
Monitor de Deploy - Render
Sistema de Gestão de Projetos v2.0.0
"""

import requests
import json
import time
from datetime import datetime

class RenderMonitor:
    def __init__(self, base_url=None):
        # URL base do seu app no Render (você vai precisar atualizar)
        self.base_url = base_url or "https://projeto-gestao-2-0.onrender.com"
        self.endpoints = {
            "health": "/health",
            "status": "/status", 
            "home": "/",
            "login": "/login",
            "dashboard": "/dashboard"
        }
    
    def test_endpoint(self, endpoint, expected_status=200):
        """Testar um endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=30)
            status = "✅" if response.status_code == expected_status else "❌"
            return {
                "url": url,
                "status_code": response.status_code,
                "expected": expected_status,
                "success": response.status_code == expected_status,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content),
                "status": status
            }
        except requests.exceptions.Timeout:
            return {"url": url, "error": "Timeout", "status": "⏱️"}
        except requests.exceptions.ConnectionError:
            return {"url": url, "error": "Connection Error", "status": "🔌"}
        except Exception as e:
            return {"url": url, "error": str(e), "status": "❌"}
    
    def check_health(self):
        """Verificar health check"""
        result = self.test_endpoint("/health", 200)
        if result.get("success"):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                data = response.json()
                print(f"✅ Health Check OK - {result['response_time']:.2f}s")
                print(f"   Status: {data.get('status')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Database: {data.get('database')}")
                print(f"   Blueprints: {len(data.get('blueprints', []))}")
                return True
            except Exception as e:
                print(f"❌ Health check falhou: {e}")
                return False
        else:
            print(f"❌ Health Check Failed: {result}")
            return False
    
    def check_status(self):
        """Verificar status detalhado"""
        result = self.test_endpoint("/status", 200)
        if result.get("success"):
            try:
                response = requests.get(f"{self.base_url}/status", timeout=10)
                data = response.json()
                print(f"✅ Status OK - {result['response_time']:.2f}s")
                print(f"   Status: {data.get('status')}")
                print(f"   Environment: {data.get('environment')}")
                print(f"   Platform: {data.get('platform')}")
                blueprints = data.get('blueprints', [])
                print(f"   Blueprints ({len(blueprints)}): {blueprints}")
                return True
            except Exception as e:
                print(f"❌ Status check falhou: {e}")
                return False
        else:
            print(f"❌ Status Failed: {result}")
            return False
    
    def full_check(self):
        """Verificação completa"""
        print(f"🔍 Monitorando aplicação: {self.base_url}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Teste básico de conectividade
        print("1. 🌐 Testando conectividade...")
        home_result = self.test_endpoint("/", 302)  # Deve redirecionar
        print(f"   Home: {home_result.get('status', '❌')} ({home_result.get('status_code', 'N/A')})")
        
        # Health check
        print("\n2. ❤️ Testando Health Check...")
        self.check_health()
        
        # Status check  
        print("\n3. 📊 Testando Status...")
        self.check_status()
        
        # Teste de login
        print("\n4. 🔐 Testando página de login...")
        login_result = self.test_endpoint("/login", 200)
        print(f"   Login: {login_result.get('status', '❌')} ({login_result.get('status_code', 'N/A')})")
        
        print("-" * 60)
        print("✅ Verificação completa!")
    
    def monitor_continuous(self, interval=30):
        """Monitoramento contínuo"""
        print(f"🔄 Iniciando monitoramento contínuo (intervalo: {interval}s)")
        print("   Pressione Ctrl+C para parar")
        
        try:
            while True:
                self.full_check()
                print(f"\n⏳ Aguardando {interval} segundos...\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento interrompido pelo usuário")

def main():
    """Função principal"""
    import sys
    
    # URL padrão - você pode alterar aqui quando souber a URL do Render
    default_url = "https://projeto-gestao-2-0.onrender.com"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input(f"Digite a URL do seu app no Render (ou Enter para usar {default_url}): ").strip()
        if not url:
            url = default_url
    
    monitor = RenderMonitor(url)
    
    print("Escolha uma opção:")
    print("1. Verificação única")
    print("2. Monitoramento contínuo")
    
    choice = input("Opção (1 ou 2): ").strip()
    
    if choice == "2":
        monitor.monitor_continuous()
    else:
        monitor.full_check()

if __name__ == "__main__":
    main()