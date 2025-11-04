#!/usr/bin/env python3
"""
Script para tentar fazer push automaticamente quando GitHub voltar
"""
import subprocess
import time
import sys

def tentar_push():
    """Tenta fazer git push"""
    try:
        print("🔄 Tentando git push...")
        result = subprocess.run(
            ["git", "push"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Push realizado com sucesso!")
            print("📋 Output:", result.stdout)
            return True
        else:
            print("❌ Push falhou:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - GitHub ainda não respondeu")
        return False
    except Exception as e:
        print(f"🚫 Erro inesperado: {e}")
        return False

def main():
    """Loop principal"""
    print("🚀 AUTO PUSH MONITOR")
    print("=" * 50)
    print("📝 Monitora conexão GitHub e faz push quando possível")
    print("🔄 Tentativas a cada 2 minutos")
    print("⏹️  Pressione Ctrl+C para parar")
    print("=" * 50)
    
    tentativas = 0
    
    try:
        while True:
            tentativas += 1
            print(f"\n🔍 Tentativa #{tentativas} - {time.strftime('%H:%M:%S')}")
            
            if tentar_push():
                print("🎉 SUCESSO! Push enviado para GitHub!")
                print("📡 Render deve iniciar novo deploy em breve...")
                break
            else:
                print(f"⏳ Aguardando 2 minutos antes da próxima tentativa...")
                time.sleep(120)  # 2 minutos
                
    except KeyboardInterrupt:
        print("\n⏹️  Script interrompido pelo usuário")
        print(f"📊 Total de tentativas: {tentativas}")

if __name__ == "__main__":
    main()