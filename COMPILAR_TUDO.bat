@echo off
echo ================================================================
echo   COMPILADOR AUTOMATICO - Sistema de Gestao de Projetos 2.0
echo ================================================================
echo.
echo Este script vai:
echo   1. Instalar PyInstaller (se necessario)
echo   2. Preparar arquivos do projeto
echo   3. Compilar o launcher do sistema
echo   4. Compilar o instalador
echo   5. Criar todos os arquivos necessarios
echo.
echo ⏳ Isso pode levar alguns minutos...
echo.
pause
echo.

REM Executar o script de criação de executável
python criar_executavel.py

echo.
echo ================================================================
if %ERRORLEVEL% EQU 0 (
    echo   ✅ COMPILACAO CONCLUIDA COM SUCESSO!
    echo.
    echo   Arquivos criados em: dist\
    echo   - Instalador_Sistema_Gestao.exe
    echo   - Sistema_Gestao_Projetos.exe
    echo.
    echo   Teste executando: dist\Instalador_Sistema_Gestao.exe
) else (
    echo   ❌ ERRO NA COMPILACAO
    echo.
    echo   Verifique as mensagens acima para detalhes
)
echo ================================================================
echo.
pause
