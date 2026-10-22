@echo off
rem ---- reabrirse dentro de una ventana que NO se cierra sola (para ver siempre que paso)
if "%MC_RUN%"=="1" goto :main
set MC_RUN=1
start "Mejorar calidad" cmd /k call "%~f0" %*
exit /b

:main
title Mejorar calidad - escalado con IA (Real-ESRGAN, placa de video)
cd /d "%~dp0"
echo Carpeta de la herramienta: %CD%

rem ---- videos de entrada: arrastrados sobre el .bat (uno o varios), o todos los .mp4/.mov de esta carpeta
set "LIST="
:args
if "%~1"=="" goto :argsdone
set LIST=%LIST% "%~f1"
shift
goto :args
:argsdone
setlocal enabledelayedexpansion
if not defined LIST for %%f in (*.mp4 *.mov) do (
  set "NM=%%~nf"
  if /i not "!NM:~-3!"=="_HD" if /i not "!NM:~-3!"=="_4K" set LIST=!LIST! "%%~ff"
)
if not defined LIST (
  echo.
  echo No encontre videos.
  echo  - Arrastra los videos ENCIMA de MEJORAR_CALIDAD.bat, o
  echo  - copialos en esta carpeta y hace doble clic en MEJORAR_CALIDAD.bat
  echo IMPORTANTE: primero descomprimi el zip ^(clic derecho - Extraer todo^).
  goto :eof
)
echo Videos:
for %%v in (%LIST%) do echo   %%~nxv

echo.
echo  Que tipo de video es?
echo    1 = Animacion / ilustracion  (los clips de Kling, motion graphics)   ^<- recomendado
echo    2 = Imagen real / foto       (mas lento)
echo.
echo  OJO: no lo uses en las grabaciones de pantalla de Workday:
echo       con letra chica la IA inventa letras.
echo.
choice /c 12 /n /m "Elegi 1 o 2: "
if errorlevel 2 (set "MODEL=realesrgan-x4plus" & set SC=4) else (set "MODEL=realesr-animevideov3" & set SC=2)

echo.
echo  Resolucion de salida:
echo    1 = 1080p  (1920x1080, para el video final)   ^<- recomendado
echo    2 = 4K     (3840x2160)
echo.
choice /c 12 /n /m "Elegi 1 o 2: "
if errorlevel 2 (set "RES=3840:2160" & set "TAG=_4K") else (set "RES=1920:1080" & set "TAG=_HD")

rem ---- herramientas (se bajan una sola vez)
set "ESR=realesrgan\realesrgan-ncnn-vulkan.exe"
set "FF=ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
set "FP=ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe"
if not exist "%ESR%" (
  echo Descargando Real-ESRGAN ^(50 MB, una sola vez^)...
  curl -L -o esr.zip https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip || goto :err
  mkdir realesrgan 2>nul
  tar -xf esr.zip -C realesrgan || goto :err
  del esr.zip
)
if not exist "%FF%" (
  echo Descargando ffmpeg ^(200 MB, una sola vez^)...
  curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip || goto :err
  tar -xf ffmpeg.zip || goto :err
  del ffmpeg.zip
)

for %%v in (%LIST%) do call :one "%%~v" || goto :err
echo.
echo LISTO. Los videos nuevos estan al lado de los originales, terminados en %TAG%.mp4
goto :eof

:one
set "IN=%~1"
set "OUT=%~dpn1%TAG%.mp4"
echo.
echo ==== %~nx1
for /f "delims=" %%r in ('call "%FP%" -v error -select_streams v:0 -show_entries stream^=r_frame_rate -of csv^=p^=0 "%IN%"') do set "FPS=%%r"
if exist tmp_in rd /s /q tmp_in
if exist tmp_out rd /s /q tmp_out
mkdir tmp_in tmp_out
echo [1/3] Separando cuadros...
"%FF%" -v error -i "%IN%" -fps_mode passthrough tmp_in\%%08d.png || exit /b 1
echo [2/3] Escalando con IA en la placa de video (%MODEL%, x%SC%)...
"%ESR%" -i tmp_in -o tmp_out -n %MODEL% -s %SC% -m realesrgan\models -f png || exit /b 1
echo [3/3] Armando el video (%RES%, %FPS% fps)...
"%FF%" -v error -y -framerate %FPS% -i tmp_out\%%08d.png -i "%IN%" -map 0:v -map 1:a? -vf "scale=%RES%:force_original_aspect_ratio=increase:flags=lanczos,crop=%RES%" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -c:a copy -shortest -movflags +faststart "%OUT%" || exit /b 1
rd /s /q tmp_in tmp_out
echo     OK: %OUT%
exit /b 0

:err
echo.
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
goto :eof
