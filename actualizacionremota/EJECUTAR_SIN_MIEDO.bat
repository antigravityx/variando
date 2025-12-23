@echo off
:: Este script ayuda a que Windows confie en el ejecutable y crea acceso directo
echo ======================================================
echo   INSTALADOR RAPIDO - EL CEREBRO
echo ======================================================
echo.
echo 1. Aplicando parche de confianza (para que Windows no moleste)...
powershell -Command "Unblock-File -Path '.\El_Cerebro_Final.exe' -ErrorAction SilentlyContinue"

echo 2. Creando acceso directo en el Escritorio...
set "TARGET=%~dp0El_Cerebro_Final.exe"
set "WDIR=%~dp0"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'El Cerebro.lnk')); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%WDIR%'; $s.Save()"

echo.
echo ======================================================
echo ¡LISTO! Ya esta "instalado".
echo Se ha creado un icono llamado "El Cerebro" en tu Escritorio.
echo A partir de ahora, usalo desde ahi.
echo ======================================================
echo.
echo Iniciando para probar...
start "" ".\El_Cerebro_Final.exe"
pause