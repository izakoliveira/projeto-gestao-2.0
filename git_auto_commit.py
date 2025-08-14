import subprocess
import sys

# Mensagem padrão de commit
default_message = "Commit automático via script Python"

try:
    # Adiciona todas as alterações
    subprocess.run(["git", "add", "."], check=True)
    # Faz o commit com mensagem padrão
    subprocess.run(["git", "commit", "-m", default_message], check=True)
    # Envia para o branch main
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Alterações salvas e enviadas para o GitHub com sucesso!")
except subprocess.CalledProcessError as e:
    print(f"Erro ao executar comando: {e}")
    sys.exit(1) 