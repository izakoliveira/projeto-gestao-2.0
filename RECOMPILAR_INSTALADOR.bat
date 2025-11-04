@echo off
echo ===============================================
echo   Recompilador do Instalador
echo   Sistema de Gestao de Projetos 2.0
echo ===============================================
echo.

REM Verifica se o ambiente virtual existe
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
    echo.
)

REM Ativa o ambiente virtual
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

REM Instala/atualiza PyInstaller
echo Instalando PyInstaller...
pip install pyinstaller
echo.

REM Remove build anterior se existir
if exist "build" (
    echo Removendo build anterior...
    rmdir /s /q build
)

if exist "dist\Instalador_Sistema_Gestao_v2.exe" (
    echo Removendo executavel anterior...
    del "dist\Instalador_Sistema_Gestao_v2.exe"
)

REM Compila o novo executável
echo Compilando novo executavel...
pyinstaller --onefile --windowed --name "Instalador_Sistema_Gestao_v2" instalador_sistema.py

REM Verifica se a compilação foi bem-sucedida
if exist "dist\Instalador_Sistema_Gestao_v2.exe" (
    echo.
    echo ===============================================
    echo   SUCESSO!
    echo ===============================================
    echo Executavel criado em: dist\Instalador_Sistema_Gestao_v2.exe
    echo Tamanho do arquivo:
    dir dist\Instalador_Sistema_Gestao_v2.exe
    echo.
    echo Para testar o instalador:
    echo 1. Execute: INSTALAR.bat
    echo 2. Ou navegue ate dist\ e execute: Instalador_Sistema_Gestao_v2.exe
    echo.
) else (
    echo.
    echo ===============================================
    echo   ERRO!
    echo ===============================================
    echo Falha ao criar o executavel.
    echo Verifique os logs acima para detalhes.
    echo.
)

pause