@echo off
setlocal enabledelayedexpansion
title GENERADOR DE EL CEREBRO - PROTOCOLO VERIX
color 0b

echo ============================================================
echo   [SISTEMA] INICIANDO PROTOCOLO DE FORJA DE EJECUTABLE
echo   [SISTEMA] PROYECTO: EL CEREBRO (VERIX SOUL)
echo ============================================================
echo.

:: Ruta del icono
set "ICON_PATH=%~dp0orbe.ico"

if not exist "%ICON_PATH%" (
    echo [ALERTA] No se encuentra el icono orbe.ico. 
    echo [INFO] Se procedera sin icono personalizado.
    set "ICON_CMD="
) else (
    echo [OK] Icono detectado: %ICON_PATH%
    set "ICON_CMD=--icon="%ICON_PATH%""
)

echo.
echo [1/4] Sincronizando dependencias del manifiesto...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install pyinstaller
echo.

echo [2/4] Limpiando residuos de forjas anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist El_Cerebro_Final.spec del El_Cerebro_Final.spec
echo [OK] Area de trabajo purificada.
echo.

echo [3/4] Iniciando PyInstaller (Compilacion en proceso)...
echo [INFO] Agrupando modulos de 'componentes' y dependencias...

:: Comando PyInstaller robusto
:: --add-data: Incluimos la carpeta componentes para asegurar su presencia
:: --collect-all: Aseguramos num2words y otras librerias problematicas
py -m PyInstaller --clean --onefile ^
    --name "El_Cerebro_Final" ^
    %ICON_CMD% ^
    --add-data "componentes;componentes" ^
    --collect-all num2words ^
    --noconfirm ^
    variando.py

echo.
echo [4/4] Verificando integridad del producto final...
if exist "dist\El_Cerebro_Final.exe" (
    echo.
    echo ============================================================
    echo   [EXITO] EL CEREBRO HA SIDO COMPILADO CORRECTAMENTE.
    echo   [UBICACION] dist\El_Cerebro_Final.exe
    echo   [ESTADO] Listo para distribucion.
    echo ============================================================
) else (
    echo.
    echo [ERROR] La forja ha fallado. Revisa los logs de PyInstaller.
)

echo.
echo Presiona cualquier tecla para cerrar la terminal...
pause > nul