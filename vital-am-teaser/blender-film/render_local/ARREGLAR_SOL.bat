@echo off
setlocal enabledelayedexpansion
title Vital AM - arreglo del sol (escena final)
cd /d "%~dp0"
set "P=%~dp0parche_sol"
if not exist "%P%\film\drive.py" ( echo No encuentro la carpeta parche_sol junto a este archivo. Descomprimi el zip completo. & pause & exit /b )

rem ---- buscar la carpeta del render (la que tiene RENDER_VitalAM.bat): aca, en subcarpetas o en la carpeta de arriba
set "TGT="
if exist "%~dp0RENDER_VitalAM.bat" set "TGT=%~dp0"
if not defined TGT for /r "%~dp0" %%f in (RENDER_VitalAM.bat) do if not defined TGT if exist "%%f" set "TGT=%%~dpf"
if not defined TGT for /r "%~dp0.." %%f in (RENDER_VitalAM.bat) do if not defined TGT if exist "%%f" set "TGT=%%~dpf"
if not defined TGT ( echo No encuentro RENDER_VitalAM.bat. Pone esta carpeta al lado de la carpeta VitalAM_render. & pause & exit /b )
echo Carpeta del render: %TGT%

rem ---- aplicar el parche y verificarlo
copy /y "%P%\film\drive.py" "%TGT%film\drive.py" >nul || goto :err
copy /y "%P%\film\post_blender.py" "%TGT%film\post_blender.py" >nul || goto :err
copy /y "%P%\EXPORTAR_FINAL_60FPS.bat" "%TGT%EXPORTAR_FINAL_60FPS.bat" >nul
if exist "%TGT%film\__pycache__" rd /s /q "%TGT%film\__pycache__"
findstr /c:"SUN_PEEK=0.007" "%TGT%film\drive.py" >nul || ( echo El parche NO se aplico. Saca una captura y mandasela a Claude. & pause & exit /b )
echo Parche aplicado OK.

rem ---- borrar la escena final vieja (cuadros 458-589), el armado y los videos viejos
cd /d "%TGT%"
for /l %%i in (458,1,589) do (
  set "n=000%%i" & set "n=!n:~-4!"
  del /q "cuadros_render\f!n!.jpg" "cuadros_render\f!n!_a.jpg" "cuadros_render\f!n!_u.jpg" "cuadros_render\f!n!.json" 2>nul
)
if exist cuadros_final rd /s /q cuadros_final
if exist VitalAM_1080p.mp4 del /q VitalAM_1080p.mp4
if exist VitalAM_escena_final_1080p60.mp4 del /q VitalAM_escena_final_1080p60.mp4
echo Renderizando de nuevo la escena final (132 cuadros)...
call RENDER_VitalAM.bat
echo.
echo Ahora exportando la escena final en 1080p 60fps...
call EXPORTAR_FINAL_60FPS.bat
exit /b

:err
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
pause
