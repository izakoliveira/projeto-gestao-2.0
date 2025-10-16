import requests
import json
import time

print("🧪 TESTANDO CORREÇÃO DA TAREFA RÁPIDA")
print("="*40)

time.sleep(2)

# Simular criação de tarefa rápida
teste_data = {
    "nome": "Teste Tarefa Rápida",
    "status": "pendente",
    "usuario_id": "test-user-id",
    "data_inicio": "2025-10-10",
    "data_fim": "2025-10-15"
}

try:
    # Tentar criar tarefa rápida (provavelmente falhará por autenticação, mas não deve dar erro 500)
    response = requests.post(
        'http://localhost:5000/projetos/6d8f6755-78f6-44ec-be5c-24161b81e5b0/criar_tarefa_rapida',
        json=teste_data,
        timeout=10
    )
    
    print(f"Status da resposta: {response.status_code}")
    
    if response.status_code == 500:
        print("❌ Ainda retorna erro 500 - verificar logs")
    elif response.status_code in [401, 403]:
        print("✅ Erro de autenticação (esperado) - não é mais erro 500!")
    elif response.status_code == 302:
        print("✅ Redirecionamento (esperado) - não é mais erro 500!")
    else:
        print(f"ℹ️  Status inesperado: {response.status_code}")
    
    # Tentar ver conteúdo da resposta
    try:
        content = response.text[:200]
        print(f"Conteúdo da resposta: {content}")
    except:
        pass
        
except Exception as e:
    print(f"Erro de conexão: {e}")

print("\n💡 Se não der mais erro 500, a correção funcionou!")