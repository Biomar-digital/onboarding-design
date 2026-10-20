@echo off
setlocal enabledelayedexpansion
title Mas FPS - interpolacion con IA (RIFE)
cd /d "%~dp0"

rem ---- video de entrada: arrastrado sobre el .bat, o el primer .mp4 de esta carpeta
set "IN=%~1"
if "%IN%"=="" for %%f in (*.mp4) do (
  set "NM=%%~nf"
  if /i not "!NM:~-3!"=="fps" if "!IN!"=="" set "IN=%%~ff"
)
if "%IN%"=="" (
  echo No encontre ningun video. Copia el .mp4 en esta carpeta o arrastralo sobre MAS_FPS.bat
  pause & exit /b
)
echo Video: %IN%
echo.
echo   1 = 48 fps  (doble de cuadros, el mas fiel)
echo   2 = 60 fps
echo.
choice /c 12 /n /m "Elegi 1 o 2: "
if errorlevel 2 (set FPS=60) else (set FPS=48)

rem ---- herramientas (se bajan una sola vez)
set "RIFE=rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe"
set "FF=ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not exist "%RIFE%" (
  echo Descargando RIFE ^(430 MB, una sola vez^)...
  curl -L -o rife.zip https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-windows.zip || goto :err
  tar -xf rife.zip || goto :err
  del rife.zip
)
if not exist "%FF%" (
  echo Descargando ffmpeg ^(200 MB, una sola vez^)...
  curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip || goto :err
  tar -xf ffmpeg.zip || goto :err
  del ffmpeg.zip
)

rem ---- 1) separar el video en cuadros
if exist tmp_in rd /s /q tmp_in
if exist tmp_out rd /s /q tmp_out
mkdir tmp_in tmp_out
echo [1/3] Separando cuadros...
"%FF%" -v error -i "%IN%" -fps_mode passthrough tmp_in\%%08d.png || goto :err
for /f %%n in ('dir /b tmp_in\*.png ^| find /c /v ""') do set N=%%n
if "%FPS%"=="60" (set /a T=N*5/2) else (set /a T=N*2)
echo     %N% cuadros -^> %T% cuadros

rem ---- 2) inventar los cuadros intermedios con la placa de video
echo [2/3] Interpolando con IA (RIFE v4.6, placa de video)...
"%RIFE%" -i tmp_in -o tmp_out -m rife-ncnn-vulkan-20221029-windows\rife-v4.6 -n %T% -f %%08d.png || goto :err

rem ---- 3) armar el video nuevo
for %%f in ("%IN%") do set "OUT=%%~dpnf_%FPS%fps.mp4"
echo [3/3] Armando el video...
"%FF%" -v error -y -framerate %FPS% -i tmp_out\%%08d.png -i "%IN%" -map 0:v -map 1:a? -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a copy -shortest -movflags +faststart "%OUT%" || goto :err

rd /s /q tmp_in tmp_out
echo.
echo LISTO: %OUT%
start "" "%OUT%"
pause
exit /b

:err
echo.
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
pause
