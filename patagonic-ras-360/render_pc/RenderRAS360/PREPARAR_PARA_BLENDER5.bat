@echo off
setlocal enabledelayedexpansion
title Banners para blender.farm - version liviana para Blender 5
cd /d "%~dp0"
rem Pasa los .blend de la carpeta "granja" a tu Blender 5 y los deja livianos para abrir (los salmones se ocultan
rem solo en la vista 3D; el render de la granja sale igual). Crea *_LIVIANO.blend al lado.
set "B5="
for /d %%d in ("C:\Program Files\Blender Foundation\Blender 5*") do if exist "%%d\blender.exe" set "B5=%%d\blender.exe"
if not defined B5 (
  echo No encontre Blender 5 en "C:\Program Files\Blender Foundation".
  echo Arrastra aca el archivo blender.exe de tu Blender 5.2 y apreta Enter:
  set /p "B5="
  set "B5=!B5:"=!"
)
if not exist "%B5%" (echo No existe "%B5%". & pause & goto :eof)
echo Usando: %B5%
for %%b in (frontal lateral) do (
  if exist "granja\RAS360_banner_%%b.blend" (
    echo.
    echo Preparando banner %%b ^(1-3 minutos^)...
    "%B5%" -b "%CD%\granja\RAS360_banner_%%b.blend" -P "%CD%\fuente\liviano.py" -- "%CD%\granja\RAS360_banner_%%b_LIVIANO.blend" > "granja\liviano_%%b_log.txt" 2>&1
    findstr /c:"LIVIANO" "granja\liviano_%%b_log.txt" || echo   Fallo: mandame granja\liviano_%%b_log.txt
  )
)
echo.
echo Listo. Abri en Blender 5 los archivos *_LIVIANO.blend de la carpeta "granja" y mandalos con el complemento.
explorer "%CD%\granja"
pause
