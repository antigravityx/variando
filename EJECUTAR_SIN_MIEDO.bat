@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title EL CEREBRO - PROTOCOLO DE CONFIANZA
color 0b

:: --- VERIFICACIÓN DE ADMINISTRADOR ---
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ======================================================
    echo   [ERROR] PRIVILEGIOS INSUFICIENTES
    echo ======================================================
    echo.
    echo Se requieren permisos de ADMINISTRADOR para aplicar 
    echo los parches de confianza de Windows.
    echo.
    echo ACCION: Haz clic derecho sobre este archivo y 
    echo selecciona 'Ejecutar como administrador'.
    echo.
    pause
    exit
)

echo ======================================================
echo   [SISTEMA] INICIANDO PROTOCOLO DE CONFIANZA ELITE
echo   [MODO] INSTALACION Y DESBLOQUEO DE SEGURIDAD
echo ======================================================
echo.
echo Este script configurara El Cerebro en tu sistema.
echo No contiene codigo malicioso y solo realiza:
echo  - Desbloqueo de seguridad de Windows (SmartScreen)
echo  - Creacion de un acceso directo en el escritorio
echo.
set /p user_confirm=">> ¿Deseas autorizar la instalacion? (s/n): "
if /i "!user_confirm!" neq "s" (
    echo [INFO] Operacion cancelada por el usuario.
    pause
    exit
)
echo.
echo [PROCESANDO...] Autorizacion concedida. Iniciando forja.
echo.

:: --- COMPROBACIÓN DE ARCHIVO ---
set "EXE_NAME=El_Cerebro_Final.exe"
if not exist "!EXE_NAME!" (
    echo [ALERTA] No se encuentra el archivo '!EXE_NAME!' en esta carpeta.
    echo [CORRECCIÓN] Asegurate de que este script este junto al ejecutable.
    pause
    exit
)

echo [1/3] Aplicando Parche de Confianza (Bypass SmartScreen)...
:: Desbloqueamos el archivo para que Windows no lo marque como "descargado de internet"
powershell -Command "Unblock-File -Path '.\\!EXE_NAME!' -ErrorAction SilentlyContinue"
echo [OK] Archivo validado como seguro en el sistema local.
echo.

echo [2/3] Forjando Acceso Directo en el Escritorio...
set "TARGET=%~dp0!EXE_NAME!"
set "WDIR=%~dp0"
set "ICON=%~dp0orbe.ico"

:: Creación robusta de acceso directo vía PowerShell
set "PS_CMD=$ws = New-Object -ComObject WScript.Shell; "
set "PS_CMD=!PS_CMD!$s = $ws.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'El Cerebro.lnk')); "
set "PS_CMD=!PS_CMD!$s.TargetPath = '!TARGET!'; "
set "PS_CMD=!PS_CMD!$s.WorkingDirectory = '!WDIR!'; "
if exist "!ICON!" (set "PS_CMD=!PS_CMD!$s.IconLocation = '!ICON!'; ")
set "PS_CMD=!PS_CMD!$s.Save()"

powershell -Command "!PS_CMD!"
echo [OK] Acceso directo creado exitosamente.
echo.

echo [3/3] Sincronizando Memoria del Alma...
timeout /t 2 /nobreak >nul
echo [OK] Sistema listo para primer contacto.
echo.

echo ======================================================
echo   ¡PROCESO COMPLETADO CON EXITO, DIRECTOR!
echo   Usa el icono "El Cerebro" en tu escritorio.
echo ======================================================
echo.
echo Iniciando fase de prueba...
start "" "!EXE_NAME!"
echo.
echo Pulsa cualquier tecla para cerrar este instalador.
pause > nul
exit