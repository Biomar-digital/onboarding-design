@echo off
echo Iniciando Agrandar imagen...
title Agrandar imagen - mas resolucion con IA en tu placa de video
cd /d "%~dp0"
rem Sube la resolucion de imagenes PNG o JPG con Real-ESRGAN (IA) y deja la nueva al lado de la original.

rem ---- imagenes de entrada: arrastradas sobre el .bat (una o varias), o todas las de esta carpeta
set "LIST="
:args
if "%~1"=="" goto :argsdone
set LIST=%LIST% "%~f1"
shift
goto :args
:argsdone
setlocal enabledelayedexpansion
if not defined LIST for %%f in (*.png *.jpg *.jpeg) do (
  set "NM=%%~nf"
  if /i not "!NM:~-9!"=="_AGRANDADA" set LIST=!LIST! "%%~ff"
)
if not defined LIST (
  echo.
  echo No encontre imagenes PNG o JPG.
  echo  - Arrastra las imagenes ENCIMA de AGRANDAR_IMAGEN.bat, o
  echo  - copialas en esta carpeta y hace doble clic en AGRANDAR_IMAGEN.bat
  echo IMPORTANTE: primero descomprimi el zip ^(clic derecho - Extraer todo^).
  pause
  goto :eof
)
echo.
echo Imagenes:
for %%v in (%LIST%) do echo   %%~nxv

echo.
echo  Que tipo de imagen es?
echo    1 = Foto real                              ^(mas natural, menos "pintada"^)
echo    2 = Ilustracion, 3D, render o imagen de IA ^(bordes mas limpios^)
echo.
choice /c 12 /n /m "Elegi 1 o 2: "
if errorlevel 2 (set "MODEL=realesrgan-x4plus-anime") else (set "MODEL=realesrgan-x4plus")

echo.
echo  Cuanto la agrando? ^(siempre mantiene la proporcion^)
echo    1 = El doble   ^(x2^)                     ^<- recomendado
echo    2 = Cuatro veces ^(x4^)
echo    3 = 4K : el lado largo queda en 3840 px
echo    4 = 8K : el lado largo queda en 7680 px
echo.
choice /c 1234 /n /m "Elegi 1, 2, 3 o 4: "
if errorlevel 4 (set "MODE=long" & set "VAL=7680" & set "TAG=8K") else if errorlevel 3 (set "MODE=long" & set "VAL=3840" & set "TAG=4K") else if errorlevel 2 (set "MODE=factor" & set "VAL=4" & set "TAG=x4") else (set "MODE=factor" & set "VAL=2" & set "TAG=x2")

rem ---- Real-ESRGAN (se baja una sola vez, 50 MB)
set "ESR=realesrgan\realesrgan-ncnn-vulkan.exe"
if not exist "%ESR%" (
  echo.
  echo Descargando Real-ESRGAN ^(50 MB, una sola vez^)...
  curl -L -o esr.zip https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip || goto :err
  mkdir realesrgan 2>nul
  tar -xf esr.zip -C realesrgan || goto :err
  del esr.zip
)
if not exist "%ESR%" goto :err

set /a OK=0
for %%v in (%LIST%) do (
  call :one "%%~v"
  if errorlevel 1 (echo     ERROR con %%~nxv - sigo con las demas) else (set /a OK+=1)
)
if exist tmp_img rd /s /q tmp_img
echo.
echo LISTO: !OK! imagen^(es^). Las nuevas estan al lado de las originales, terminadas en _%TAG%_AGRANDADA
pause
goto :eof

:one
set "IN=%~1"
set "EXT=%~x1"
set "FMT=png"
if /i "%EXT%"==".jpg" set "FMT=jpg"
if /i "%EXT%"==".jpeg" set "FMT=jpg"
set "OUT=%~dpn1_%TAG%_AGRANDADA.%FMT%"
echo.
echo ==== %~nx1
rem copia con nombre simple: Real-ESRGAN falla con acentos o simbolos en la ruta
if exist tmp_img rd /s /q tmp_img
mkdir tmp_img
copy /y "%IN%" "tmp_img\in%EXT%" >nul || exit /b 1
echo     [1/2] Agrandando x4 con IA ^(%MODEL%^)...
"%ESR%" -i "tmp_img\in%EXT%" -o "tmp_img\up.png" -n %MODEL% -s 4 -m realesrgan\models -f png >nul 2>&1
if not exist "tmp_img\up.png" (
  echo     La placa de video no pudo con la IA. Pruebo en modo seguro ^(mas lento^)...
  "%ESR%" -i "tmp_img\in%EXT%" -o "tmp_img\up.png" -n %MODEL% -s 4 -m realesrgan\models -f png -t 100 -g -1 >nul 2>&1
)
if not exist "tmp_img\up.png" exit /b 1
echo     [2/2] Ajustando al tamano final y guardando...
powershell -NoProfile -ExecutionPolicy Bypass -File "ajustar.ps1" -Original "tmp_img\in%EXT%" -Grande "tmp_img\up.png" -Salida "%OUT%" -Modo %MODE% -Valor %VAL% || exit /b 1
exit /b 0

:err
echo.
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
pause
goto :eof
