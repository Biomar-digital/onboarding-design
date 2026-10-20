@echo off
setlocal enabledelayedexpansion
title Vital AM - escena final 1080p 60fps
cd /d "%~dp0"
set A=458
set B=589
set /a N=B-A+1
set /a T=N*5/2
set "OUT=VitalAM_escena_final_1080p60.mp4"

if not exist "cuadros_final\f0589.jpg" (
  echo Faltan los cuadros terminados de la escena final.
  echo Primero hace doble clic en ARREGLAR_SOL.bat y espera a que termine.
  pause & exit /b
)

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

if exist tmp60_in rd /s /q tmp60_in
if exist tmp60_out rd /s /q tmp60_out
mkdir tmp60_in tmp60_out
echo [1/3] Tomando los cuadros %A% a %B% (%N% cuadros)...
"%FF%" -v error -start_number %A% -i cuadros_final\f%%04d.jpg -frames:v %N% tmp60_in\%%08d.png || goto :err

echo [2/3] Interpolando a 60 fps con IA (%N% -^> %T% cuadros)...
"%RIFE%" -i tmp60_in -o tmp60_out -m rife-ncnn-vulkan-20221029-windows\rife-v4.6 -n %T% -f %%08d.png || goto :err

echo [3/3] Armando el video...
"%FF%" -v error -y -framerate 60 -i tmp60_out\%%08d.png -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart "%OUT%" || goto :err

rd /s /q tmp60_in tmp60_out
echo.
echo LISTO: %OUT%
start "" "%OUT%"
pause
exit /b

:err
echo.
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
pause
