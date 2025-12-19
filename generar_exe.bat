@echo off
echo ==========================================
echo      GENERADOR DE EJECUTABLE (VERIX)
echo ==========================================
echo.

:: Aseguramos la ruta absoluta del icono para evitar errores
set "ICON_PATH=%~dp0orbe.ico"

if not exist "%ICON_PATH%" (
    echo [ERROR] No se encuentra el icono en: "%ICON_PATH%"
    pause
    exit
)

echo 1. Instalando librerias necesarias...
py -m pip install -r requirements.txt
echo.
echo 2. Instalando PyInstaller...
py -m pip install pyinstaller
echo.
echo 3. Limpiando archivos antiguos para asegurar el icono...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist El_Cerebro.spec del El_Cerebro.spec
echo.
echo 4. Creando el ejecutable (esto puede tardar unos minutos)...
py -m PyInstaller --clean --onefile --name "El_Cerebro_Final" --icon="%ICON_PATH%" --collect-all num2words variando.py
echo.
echo ==========================================
echo ¡LISTO! El archivo 'El_Cerebro_Final.exe' esta en la carpeta 'dist'.
echo ==========================================
pause