@echo off
echo ===============================================
echo   Sistema de Gestao de Projetos 2.0
echo   Instalador Automatico
echo ===============================================
echo.
echo Iniciando instalacao...
echo.

REM Verifica se o executável existe (prioriza a versão mais recente)
if exist "dist\Instalador_Sistema_Gestao_FINAL.exe" (
    set INSTALADOR="dist\Instalador_Sistema_Gestao_FINAL.exe"
    echo ========================================================
    echo   USANDO VERSAO FINAL - PROBLEMA RESOLVIDO!
    echo   - Execucao de Python corrigida
    echo   - Sem loops ou execucoes duplicadas  
    echo   - Logs detalhados para diagnostico
    echo ========================================================
) else if exist "dist\Instalador_Sistema_Gestao_v5.exe" (
    set INSTALADOR="dist\Instalador_Sistema_Gestao_v5.exe"
    echo Usando versao v5.0 - VERSAO FINAL com logs completos
) else if exist "dist\Instalador_Sistema_Gestao_v4.exe" (
    set INSTALADOR="dist\Instalador_Sistema_Gestao_v4.exe"
    echo Usando versao v4.0 com logs detalhados e correcoes
) else if exist "dist\Instalador_Sistema_Gestao_v3.exe" (
    set INSTALADOR="dist\Instalador_Sistema_Gestao_v3.exe"
    echo Usando versao v3.0 com arquivos embarcados
) else (
    echo ERRO: Instalador nao encontrado!
    echo Certifique-se de que existe o arquivo na pasta dist\
    pause
    exit /b 1
)

REM Executa o instalador
echo Executando instalador...
start "" %INSTALADOR%

echo.
echo Instalador iniciado com sucesso!
echo Uma janela de instalacao deve ter aberto.
echo.
echo Se a janela nao abriu:
echo 1. Navegue ate a pasta 'dist\'
echo 2. Execute manualmente: Instalador_Sistema_Gestao.exe
echo.
pause