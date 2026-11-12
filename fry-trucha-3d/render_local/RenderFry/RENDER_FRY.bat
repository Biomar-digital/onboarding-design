@echo off
setlocal enabledelayedexpansion
title Fry de trucha 3D - render en tu placa de video (v16)
cd /d "%~dp0"
echo.
echo  ===  Fry de trucha 3D - render del video (1920x1080, 11 s)  ===
echo  Carpeta del proyecto: %CD%
echo "%CD%" | find /i "OneDrive" >nul && (echo. & echo  OJO: esta carpeta esta dentro de OneDrive. Mejor moverla a C:\RenderFry para que no trabe el render. & echo.)
if not exist "fuente\fry_escena.py" (
  echo.
  echo  No encuentro fuente\fry_escena.py
  echo  Primero descomprimi el zip: clic derecho sobre el zip - "Extraer todo".
  pause & goto :eof
)

rem ---- Blender 4.2 LTS y ffmpeg: usa los que ya bajo el render de RAS 360; si no estan, los baja una sola vez
set "TOOLS=%LOCALAPPDATA%\RAS360"
if not exist "%TOOLS%" mkdir "%TOOLS%"
echo  Herramientas en: %TOOLS%
set "BL=%TOOLS%\blender\blender.exe"
set "FF=%TOOLS%\ffmpeg\bin\ffmpeg.exe"

if exist "%BL%" goto :haveblender
if not exist "%TOOLS%\blender.zip" (
  echo.
  echo  Descargando Blender 4.2 LTS ^(380 MB, una sola vez^)...
  curl -L -o "%TOOLS%\blender.zip" https://download.blender.org/release/Blender4.2/blender-4.2.23-windows-x64.zip || goto :errdl
)
echo  Descomprimiendo Blender ^(1-3 minutos^)...
if exist "%TOOLS%\blender-4.2.23-windows-x64" rmdir /s /q "%TOOLS%\blender-4.2.23-windows-x64"
tar -xf "%TOOLS%\blender.zip" -C "%TOOLS%"
if errorlevel 1 (
  echo  La descompresion rapida fallo, pruebo con PowerShell ^(mas lento^)...
  if exist "%TOOLS%\blender-4.2.23-windows-x64" rmdir /s /q "%TOOLS%\blender-4.2.23-windows-x64"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Force -LiteralPath '%TOOLS%\blender.zip' -DestinationPath '%TOOLS%'" || goto :errzip
)
if exist "%TOOLS%\blender" rmdir /s /q "%TOOLS%\blender"
move "%TOOLS%\blender-4.2.23-windows-x64" "%TOOLS%\blender" >nul || goto :errzip
if not exist "%BL%" goto :errzip
del "%TOOLS%\blender.zip"
:haveblender

if exist "%FF%" goto :haveffmpeg
if not exist "%TOOLS%\ffmpeg.zip" (
  echo.
  echo  Descargando ffmpeg ^(200 MB, una sola vez^)...
  curl -L -o "%TOOLS%\ffmpeg.zip" https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip || goto :errdl
)
echo  Descomprimiendo ffmpeg...
tar -xf "%TOOLS%\ffmpeg.zip" -C "%TOOLS%"
if errorlevel 1 powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Force -LiteralPath '%TOOLS%\ffmpeg.zip' -DestinationPath '%TOOLS%'" || goto :errzip
if exist "%TOOLS%\ffmpeg" rmdir /s /q "%TOOLS%\ffmpeg"
move "%TOOLS%\ffmpeg-master-latest-win64-gpl" "%TOOLS%\ffmpeg" >nul || goto :errzip
if not exist "%FF%" goto :errzip
del "%TOOLS%\ffmpeg.zip"
:haveffmpeg

echo.
echo  Que queres hacer?
echo    1 = Video completo, calidad final ^(228 cuadros + blanco final^). Si se corto, sigue desde donde quedo.
echo    2 = Prueba rapida: 6 cuadros sueltos para ver que todo funciona
echo    3 = Empezar de cero ^(borra los cuadros ya hechos^)
echo.
choice /c 123 /n /m "Elegi 1, 2 o 3: "
set "M=%errorlevel%"
set "OUT=cuadros_v16"
set "LAST=228"
if "%M%"=="3" (if exist "%OUT%" rmdir /s /q "%OUT%")
if not exist "%OUT%" mkdir "%OUT%"

if "%M%"=="2" (
  if not exist "prueba" mkdir "prueba"
  for %%F in (30 60 95 125 195 205) do (
    echo  Cuadro de prueba %%F...
    "%BL%" -b -P "%CD%\fuente\fry_escena.py" -- "%CD%\fuente\silueta.json" "%CD%\prueba" 1920 32 %%F-%%F > "prueba\log_%%F.txt" 2>&1
  )
  echo.
  echo  Listo: mira las imagenes en la carpeta "prueba".
  start "" "prueba"
  pause & goto :eof
)

rem ---- busca el primer cuadro que falta (para retomar)
set "START=1"
:findstart
set "N=0000!START!"
set "N=!N:~-4!"
if exist "%OUT%\f_!N!.png" (
  set /a START+=1
  if !START! leq %LAST% goto :findstart
)
if !START! gtr %LAST% goto :encode
echo.
echo  Renderizando cuadros !START! a %LAST% ...  ^(se puede cerrar y volver a abrir: sigue desde el ultimo cuadro^)
echo  Hora de inicio: %TIME%
echo  Esta ventana no muestra el avance: para verlo, abri la carpeta %OUT% y mira como aparecen los cuadros.
start "" "%CD%\%OUT%"
"%BL%" -b -P "%CD%\fuente\fry_escena.py" -- "%CD%\fuente\silueta.json" "%CD%\%OUT%" 1920 32 !START!-%LAST% > "log_render.txt" 2>&1
set "N=0000%LAST%"
set "N=!N:~-4!"
if not exist "%OUT%\f_!N!.png" (
  echo.
  echo  El render no llego al final. Mira log_render.txt y volve a abrir este archivo: sigue desde donde quedo.
  pause & goto :eof
)

:encode
echo.
echo  Armando el MP4 ^(el ultimo cuadro, blanco, se sostiene hasta los 11 s^)...
"%FF%" -y -loglevel error -framerate 25 -i "%OUT%\f_%%04d.png" -vf "tpad=stop_mode=clone:stop_duration=1.88" -c:v libx264 -pix_fmt yuv420p -crf 14 -preset slow -movflags +faststart "fry_pregunta_sin_sonido.mp4"
if errorlevel 1 (echo  Fallo al armar el video. & pause & goto :eof)
"%FF%" -y -loglevel error -i "fry_pregunta_sin_sonido.mp4" -i "fuente\fry_sonido.wav" -c:v copy -c:a aac -b:a 192k -movflags +faststart "fry_pregunta.mp4"
if errorlevel 1 (echo  Fallo al armar el video. & pause & goto :eof)
echo.
echo  LISTO: fry_pregunta.mp4 ^(con sonido^) y fry_pregunta_sin_sonido.mp4  ^(hora: %TIME%^)
start "" "%CD%"
pause & goto :eof

:errdl
echo.
echo  No se pudo descargar. Revisa la conexion a internet y volve a abrir este archivo.
pause & goto :eof
:errzip
echo.
echo  No se pudo descomprimir. Borra la carpeta %TOOLS% y volve a abrir este archivo.
pause & goto :eof
