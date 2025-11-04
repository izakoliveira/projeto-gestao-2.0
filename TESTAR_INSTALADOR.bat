@echo off
title Teste do Instalador
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   TESTE DO INSTALADOR - Sistema de Gestao de Projetos    ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Verificar se o instalador existe
if not exist "dist\Instalador_Sistema_Gestao.exe" (
    echo ❌ ERRO: Instalador não encontrado!
    echo.
    echo O arquivo dist\Instalador_Sistema_Gestao.exe nao existe.
    echo.
    echo Execute primeiro: COMPILAR_TUDO.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Instalador encontrado: dist\Instalador_Sistema_Gestao.exe
echo.

REM Verificar tamanho
for %%A in ("dist\Instalador_Sistema_Gestao.exe") do (
    set size=%%~zA
    set /a sizeMB=!size! / 1048576
)

echo 📊 Informacoes do instalador:
echo    Tamanho: %sizeMB% MB aproximadamente
echo.

REM Verificar se o launcher existe
if exist "dist\Sistema_Gestao_Projetos.exe" (
    echo ✅ Launcher encontrado: dist\Sistema_Gestao_Projetos.exe
    
    for %%A in ("dist\Sistema_Gestao_Projetos.exe") do (
        set launcherSize=%%~zA
        set /a launcherMB=!launcherSize! / 1048576
    )
    echo    Tamanho: %launcherMB% MB aproximadamente
) else (
    echo ⚠️  Launcher nao encontrado (sera incluido no instalador)
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo Deseja executar o instalador para teste? (S/N)
set /p choice="Sua escolha: "

if /i "%choice%"=="S" (
    echo.
    echo 🚀 Iniciando instalador...
    echo.
    echo DICA: Durante o teste, escolha uma pasta temporaria
    echo       para facilitar a remocao depois.
    echo.
    timeout /t 3
    start "" "dist\Instalador_Sistema_Gestao.exe"
    echo.
    echo ✅ Instalador iniciado!
    echo.
    echo Aguarde a janela do instalador abrir...
    echo.
) else (
    echo.
    echo ℹ️  Teste cancelado.
    echo.
    echo Para testar manualmente:
    echo    1. Va ate a pasta 'dist\'
    echo    2. Execute: Instalador_Sistema_Gestao.exe
    echo.
)

echo ════════════════════════════════════════════════════════════
echo.
echo 📋 Checklist de Teste:
echo.
echo [ ] Instalador abre sem erros
echo [ ] Interface grafica e exibida
echo [ ] Consegue escolher pasta de instalacao
echo [ ] Consegue configurar Supabase
echo [ ] Instalacao completa sem erros
echo [ ] Ambiente virtual e criado
echo [ ] Dependencias sao instaladas
echo [ ] Arquivo .env e criado
echo [ ] Scripts .bat sao criados
echo [ ] Atalho e criado (se marcado)
echo [ ] Sistema inicia corretamente
echo [ ] Navegador abre automaticamente
echo [ ] Consegue fazer login
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
