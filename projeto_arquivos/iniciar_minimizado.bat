@echo off
REM Inicia o sistema com a janela minimizada
cd /d "%~dp0"
if exist venv\Scripts\python.exe (
    start /MIN "" venv\Scripts\python.exe app_producao.py
    timeout /t 3 /nobreak >nul
    start "" http://localhost:5000
) else (
    echo Erro: Ambiente virtual nao encontrado!
    pause
)
