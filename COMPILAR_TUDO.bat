@echo off
title Compilando Sistema de Gestao de Projetos
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   COMPILANDO SISTEMA DE GESTAO DE PROJETOS v2.0          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Verificar se PyInstaller está instalado
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller nao encontrado!
    echo.
    echo Instale com: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo ✅ PyInstaller encontrado
echo.

REM Criar pasta dist se não existir
if not exist "dist" mkdir dist

echo 📁 Compilando INSTALADOR...
echo.

REM Compilar instalador
pyinstaller --clean --noconfirm Instalador_Sistema_Gestao.spec

if errorlevel 1 (
    echo ❌ Erro ao compilar instalador!
    pause
    exit /b 1
)

echo ✅ Instalador compilado com sucesso
echo.

echo 📁 Compilando LAUNCHER do sistema...
echo.

REM Criar arquivo .spec para o launcher se não existir
if not exist "Launcher_Sistema.spec" (
    echo Criando arquivo .spec para o launcher...

    REM Criar arquivo .spec básico para o app_producao.py
    echo # -*- mode: python ; coding: utf-8 -*- > Launcher_Sistema.spec
    echo. >> Launcher_Sistema.spec
    echo block_cipher = None >> Launcher_Sistema.spec
    echo. >> Launcher_Sistema.spec
    echo a = Analysis( >> Launcher_Sistema.spec
    echo     ['app_producao.py'], >> Launcher_Sistema.spec
    echo     pathex=[], >> Launcher_Sistema.spec
    echo     binaries=[], >> Launcher_Sistema.spec
    echo     datas=[ >> Launcher_Sistema.spec
    echo         ('templates', 'templates'), >> Launcher_Sistema.spec
    echo         ('static', 'static'), >> Launcher_Sistema.spec
    echo         ('routes', 'routes'), >> Launcher_Sistema.spec
    echo         ('utils', 'utils'), >> Launcher_Sistema.spec
    echo         ('config', 'config'), >> Launcher_Sistema.spec
    echo         ('sgp_icon.ico', '.'), >> Launcher_Sistema.spec
    echo     ], >> Launcher_Sistema.spec
    echo     hiddenimports=[ >> Launcher_Sistema.spec
    echo         'flask', >> Launcher_Sistema.spec
    echo         'supabase', >> Launcher_Sistema.spec
    echo         'dotenv', >> Launcher_Sistema.spec
    echo         'werkzeug', >> Launcher_Sistema.spec
    echo         'jinja2', >> Launcher_Sistema.spec
    echo         'datetime', >> Launcher_Sistema.spec
    echo         'os', >> Launcher_Sistema.spec
    echo         'sys', >> Launcher_Sistema.spec
    echo         'json', >> Launcher_Sistema.spec
    echo         'threading', >> Launcher_Sistema.spec
    echo         'subprocess', >> Launcher_Sistema.spec
    echo     ], >> Launcher_Sistema.spec
    echo     hookspath=[], >> Launcher_Sistema.spec
    echo     hooksconfig={}, >> Launcher_Sistema.spec
    echo     runtime_hooks=[], >> Launcher_Sistema.spec
    echo     excludes=[], >> Launcher_Sistema.spec
    echo     win_no_prefer_redirects=False, >> Launcher_Sistema.spec
    echo     win_private_assemblies=False, >> Launcher_Sistema.spec
    echo     cipher=block_cipher, >> Launcher_Sistema.spec
    echo     noarchive=False, >> Launcher_Sistema.spec
    echo ) >> Launcher_Sistema.spec
    echo. >> Launcher_Sistema.spec
    echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> Launcher_Sistema.spec
    echo. >> Launcher_Sistema.spec
    echo exe = EXE( >> Launcher_Sistema.spec
    echo     pyz, >> Launcher_Sistema.spec
    echo     a.scripts, >> Launcher_Sistema.spec
    echo     a.binaries, >> Launcher_Sistema.spec
    echo     a.zipfiles, >> Launcher_Sistema.spec
    echo     a.datas, >> Launcher_Sistema.spec
    echo     [], >> Launcher_Sistema.spec
    echo     name='Sistema_Gestao_Projetos', >> Launcher_Sistema.spec
    echo     debug=False, >> Launcher_Sistema.spec
    echo     bootloader_ignore_signals=False, >> Launcher_Sistema.spec
    echo     strip=False, >> Launcher_Sistema.spec
    echo     upx=True, >> Launcher_Sistema.spec
    echo     upx_exclude=[], >> Launcher_Sistema.spec
    echo     runtime_tmpdir=None, >> Launcher_Sistema.spec
    echo     console=True, >> Launcher_Sistema.spec
    echo     disable_windowed_traceback=False, >> Launcher_Sistema.spec
    echo     argv_emulation=False, >> Launcher_Sistema.spec
    echo     target_arch=None, >> Launcher_Sistema.spec
    echo     codesign_identity=None, >> Launcher_Sistema.spec
    echo     entitlements_file=None, >> Launcher_Sistema.spec
    echo     icon='sgp_icon.ico', >> Launcher_Sistema.spec
    echo ) >> Launcher_Sistema.spec

    echo ✅ Arquivo Launcher_Sistema.spec criado
    echo.
)

REM Compilar launcher
pyinstaller --clean --noconfirm Launcher_Sistema.spec

if errorlevel 1 (
    echo ❌ Erro ao compilar launcher!
    pause
    exit /b 1
)

echo ✅ Launcher compilado com sucesso
echo.

REM Verificar arquivos gerados
echo 📊 Verificando arquivos compilados...
echo.

if exist "dist\Instalador_Sistema_Gestao.exe" (
    for %%A in ("dist\Instalador_Sistema_Gestao.exe") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
    )
    echo ✅ Instalador: dist\Instalador_Sistema_Gestao.exe (%sizeMB% MB)
) else (
    echo ❌ Instalador nao encontrado!
)

if exist "dist\Sistema_Gestao_Projetos.exe" (
    for %%A in ("dist\Sistema_Gestao_Projetos.exe") do (
        set launcherSize=%%~zA
        set /a launcherMB=!launcherSize! / 1048576
    )
    echo ✅ Launcher: dist\Sistema_Gestao_Projetos.exe (%launcherMB% MB)
) else (
    echo ❌ Launcher nao encontrado!
)

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   ✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!                   ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 📁 Arquivos gerados na pasta 'dist':
if exist "dist\Instalador_Sistema_Gestao.exe" echo    - Instalador_Sistema_Gestao.exe
if exist "dist\Sistema_Gestao_Projetos.exe" echo    - Sistema_Gestao_Projetos.exe
echo.
echo 🎯 Próximos passos:
echo    1. Execute TESTAR_INSTALADOR.bat para verificar
echo    2. Teste o instalador em uma máquina limpa
echo    3. Distribua o Instalador_Sistema_Gestao.exe
echo.

pause