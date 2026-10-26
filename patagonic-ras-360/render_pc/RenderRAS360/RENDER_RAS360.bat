@echo off
title Patagonic RAS 360 - render en tu placa de video
cd /d "%~dp0"
echo.
echo  ===  Patagonic RAS 360 - render de las 10 pantallas  ===
echo  Carpeta: %CD%
echo.
if not exist "fuente\hall.py" (
  echo  No encuentro fuente\hall.py
  echo  Primero descomprimi el zip: clic derecho sobre el zip - "Extraer todo".
  pause & goto :eof
)

rem ---- Blender 4.2 LTS (version con la que se probo todo) y ffmpeg: se bajan una sola vez
set "BL=blender\blender.exe"
if not exist "%BL%" (
  echo  Descargando Blender 4.2 LTS ^(380 MB, una sola vez^)...
  curl -L -o blender.zip https://download.blender.org/release/Blender4.2/blender-4.2.23-windows-x64.zip || goto :err
  echo  Descomprimiendo Blender...
  tar -xf blender.zip || goto :err
  ren blender-4.2.23-windows-x64 blender || goto :err
  del blender.zip
)
set "FF=ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
if not exist "%FF%" (
  echo  Descargando ffmpeg ^(200 MB, una sola vez^)...
  curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip || goto :err
  tar -xf ffmpeg.zip || goto :err
  del ffmpeg.zip
)

echo.
echo  Que queres renderizar?
echo    1 = Prueba rapida: 3 segundos de las 10 pantallas, calidad media   ^<- empeza por aca
echo    2 = Minuto completo, calidad media  (mitad de resolucion, para revisar)
echo    3 = Minuto completo, calidad final  (resolucion nativa de cada pantalla)
echo.
choice /c 123 /n /m "Elegi 1, 2 o 3: "
if errorlevel 3 (set "OUT=render_final" & set "SCALE=1.0" & set "RAS_SAMPLES=64" & set "RAS_FRAMES=1-1440" & set "RAS_JPG=" & set "EXT=png" & set "START=1" & goto :go)
if errorlevel 2 (set "OUT=render_media" & set "SCALE=0.5" & set "RAS_SAMPLES=24" & set "RAS_FRAMES=1-1440" & set "RAS_JPG=1" & set "EXT=jpg" & set "START=1" & goto :go)
set "OUT=render_prueba" & set "SCALE=0.5" & set "RAS_SAMPLES=24" & set "RAS_FRAMES=613-684" & set "RAS_JPG=1" & set "EXT=jpg" & set "START=613"
:go
set "RAS_GPU=AUTO"
set "RAS_FRAMEMAJOR=1"
set "RAS_STATIC_FROM=15"
echo.
echo  Renderizando en "%OUT%" ...  (cuadros %RAS_FRAMES%)
echo  Podes cerrar esta ventana cuando quieras: al volver a abrirla sigue desde el ultimo cuadro.
echo  La primera linea dice que placa de video encontro ("GPU ...").
echo.
"%BL%" -b --factory-startup -P fuente\hall.py -- "%CD%\%OUT%" 0 1440 %SCALE% 2>&1 | findstr /r /c:"^GPU" /c:"FRAME_DONE" /c:"FISH" /c:"Error" /c:"DONE" /c:"GPU no"
if errorlevel 1 echo.

echo.
echo  Armando un video MP4 por pantalla (con vinieteo suave y grano fino)...
for /d %%d in ("%OUT%\*") do (
  "%FF%" -y -loglevel error -framerate 24 -start_number %START% -i "%%d\%%~nxd_%%04d.%EXT%" -vf "vignette=angle=PI/7,noise=alls=4:allf=t" -c:v libx264 -crf 14 -pix_fmt yuv420p "%OUT%\%%~nxd.mp4" 2>nul
)
echo.
echo  Listo. Los videos estan en la carpeta "%OUT%" (uno por pantalla).
echo  Mandalos al chat y armo el mockup del hall con ellos.
explorer "%OUT%"
pause
goto :eof

:err
echo.
echo  Algo fallo descargando o descomprimiendo. Revisa la conexion y volve a intentar.
pause
