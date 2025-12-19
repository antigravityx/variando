@echo off
echo ==========================================
echo      ACTUALIZADOR AUTOMATICO (VERIX)
echo ==========================================
echo.
echo 1. Cerrando El Cerebro para actualizar...
taskkill /IM "El_Cerebro_Final.exe" /F >nul 2>&1

:: Limpieza: Borrar la versión vieja si existe para no confundirse
if exist "El_Cerebro.exe" del "El_Cerebro.exe"

echo.
echo 2. Esperando liberacion de archivos...
timeout /t 3 /nobreak >nul

echo.
echo 3. Descargando la nueva version desde GitHub...
:: REEMPLAZA LA URL DE ABAJO CON LA URL "RAW" DE TU EJECUTABLE EN GITHUB
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/antigravityx/variando/raw/master/dist/El_Cerebro_Final.exe' -OutFile 'El_Cerebro_Final.exe'"

echo.
echo ==========================================
echo ¡ACTUALIZACION COMPLETADA!
echo Reiniciando El Cerebro...
echo ==========================================
start "" "El_Cerebro_Final.exe"
exit