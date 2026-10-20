@echo off
setlocal enabledelayedexpansion
title Vital AM - arreglo del sol (escena final)
cd /d "%~dp0"
echo Borrando los cuadros de la escena final (458-589) para volver a renderizarlos...
for /l %%i in (458,1,589) do (
  set "n=000%%i" & set "n=!n:~-4!"
  del /q "cuadros_render\f!n!.jpg" "cuadros_render\f!n!_a.jpg" "cuadros_render\f!n!_u.jpg" "cuadros_render\f!n!.json" 2>nul
)
if exist cuadros_final rd /s /q cuadros_final
if exist VitalAM_1080p.mp4 del /q VitalAM_1080p.mp4
echo Listo. Renderizando de nuevo solo esa parte...
call RENDER_VitalAM.bat
