@echo off
title Vital AM - render 1080p
cd /d "%~dp0"
set BL=blender-4.2.23-windows-x64\blender.exe

echo ============================================================
echo  SmartCare Vital AM - render 1080p (24 fps, 589 cuadros)
echo  Deja la compu prendida. Si se corta, volve a hacer doble
echo  clic: sigue desde donde quedo.
echo ============================================================
echo.

if not exist "%BL%" (
  echo [1/3] Descargando Blender 4.2 portable ^(380 MB, una sola vez^)...
  curl -L -o blender42.zip https://download.blender.org/release/Blender4.2/blender-4.2.23-windows-x64.zip || goto :err
  echo Descomprimiendo...
  tar -xf blender42.zip || goto :err
  del blender42.zip
)

echo [2/3] Renderizando cuadros con la placa de video...
"%BL%" -b -P film\render_film.py -- 1 589 1920 16 cuadros_render || goto :err

echo [3/3] Armando el video final...
"%BL%" -b --factory-startup -P film\post_blender.py -- cuadros_render cuadros_final VitalAM_1080p.mp4 || goto :err

echo.
echo LISTO: VitalAM_1080p.mp4
start "" "VitalAM_1080p.mp4"
pause
exit /b

:err
echo.
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
pause
