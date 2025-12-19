@echo off
echo ==========================================
echo      GENERADOR DE EJECUTABLE (VERIX)
echo ==========================================
echo.
echo 1. Instalando librerias necesarias...
pip install -r requirements.txt
echo.
echo 2. Instalando PyInstaller...
pip install pyinstaller
echo.
echo 3. Creando el ejecutable (esto puede tardar unos minutos)...
pyinstaller --onefile --name "El_Cerebro" --collect-all num2words variando.py
echo.
echo ==========================================
echo ¡LISTO! El archivo 'El_Cerebro.exe' esta en la carpeta 'dist'.
echo ==========================================
pause