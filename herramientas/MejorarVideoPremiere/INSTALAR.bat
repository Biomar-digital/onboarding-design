@echo off
title Instalar panel Mejorar Video (IA) para Premiere Pro
cd /d "%~dp0"
set "DEST=%APPDATA%\Adobe\CEP\extensions\com.biomar.mejorarvideo"
echo.
echo  Instalando el panel en:
echo    %DEST%
if exist "%DEST%" rd /s /q "%DEST%"
xcopy /e /i /q /y "com.biomar.mejorarvideo" "%DEST%" >nul || goto :err
rem paneles propios (sin firma): Premiere los acepta con PlayerDebugMode=1
for %%v in (8 9 10 11 12 13 14 15 16) do reg add "HKCU\Software\Adobe\CSXS.%%v" /v PlayerDebugMode /t REG_SZ /d 1 /f >nul
if not exist "%DEST%\CSXS\manifest.xml" goto :err
echo.
echo  Comprobacion:
if exist "%DEST%\CSXS\manifest.xml" echo    [OK] panel copiado
reg query "HKCU\Software\Adobe\CSXS.12" /v PlayerDebugMode >nul 2>&1 && echo    [OK] permiso para paneles propios
echo.
echo  LISTO. Cerra y volve a abrir Premiere Pro.
echo  Despues: menu Ventana ^> Extensiones ^> Mejorar Video (IA)
echo  (en Premiere 2025 o mas nuevo: Ventana ^> Extensiones (heredadas) ^> Mejorar Video (IA))
echo.
pause
goto :eof
:err
echo  No se pudo copiar el panel. Saca una captura y mandasela a Claude.
pause
