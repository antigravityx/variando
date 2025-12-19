@echo off
echo ==========================================
echo      ACTUALIZADOR AUTOMATICO (VERIX)
echo ==========================================
echo.
echo 1. Cerrando El Cerebro para actualizar...
taskkill /IM "El_Cerebro.exe" /F >nul 2>&1

echo.
echo 2. Esperando liberacion de archivos...
timeout /t 3 /nobreak >nul

echo.
echo 3. Descargando la nueva version desde GitHub...
:: REEMPLAZA LA URL DE ABAJO CON LA URL "RAW" DE TU EJECUTABLE EN GITHUB
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/antigravityx/variando/blob/master/dist/El_Cerebro.exe' -OutFile 'El_Cerebro.exe'"

echo.
echo ==========================================
echo ¡ACTUALIZACION COMPLETADA!
echo Reiniciando El Cerebro...
echo ==========================================
start "" "El_Cerebro.exe"
exit