@echo off
setlocal
title Patagonic RAS 360 - render en tu placa de video
cd /d "%~dp0"
echo.
echo  ===  Patagonic RAS 360 - render de las 10 pantallas  ===
echo  Carpeta del proyecto: %CD%
if not exist "fuente\hall.py" (
  echo.
  echo  No encuentro fuente\hall.py
  echo  Primero descomprimi el zip: clic derecho sobre el zip - "Extraer todo".
  pause & goto :eof
)

rem ---- Blender 4.2 LTS y ffmpeg se instalan una sola vez en una carpeta local corta
rem      (fuera de OneDrive y de rutas largas, que traban la descompresion)
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
echo.
echo  Renderizando en "%OUT%" ...  (cuadros %RAS_FRAMES%)
echo  Primero prepara la escena (unos minutos), despues va mostrando cada cuadro terminado.
echo  Podes cerrar esta ventana cuando quieras: al volver a abrirla sigue desde el ultimo cuadro.
echo.
"%BL%" -b --factory-startup -P fuente\hall.py -- "%CD%\%OUT%" 0 1440 %SCALE% 2>&1 | powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=[IO.StreamWriter]::new((Join-Path (Get-Location) 'render_log.txt')); foreach($l in $input){ $w.WriteLine($l); if($l -match '^GPU|FRAME_DONE|^FISH|Error|Traceback|^DONE'){ Write-Host ((Get-Date -Format 'HH:mm:ss')+'  '+$l); $w.Flush() } }; $w.Close()"
findstr /c:"DONE" render_log.txt >nul || (echo. & echo  El render no termino bien. Mandame el archivo render_log.txt de esta carpeta. & pause & goto :eof)

echo.
echo  Armando un video MP4 por pantalla (con vinieteo suave y grano fino)...
for /d %%d in ("%OUT%\*") do "%FF%" -y -loglevel error -framerate 24 -start_number %START% -i "%%d\%%~nxd_%%04d.%EXT%" -vf "vignette=angle=PI/7,noise=alls=4:allf=t" -c:v libx264 -crf 14 -pix_fmt yuv420p "%OUT%\%%~nxd.mp4"
echo.
echo  Listo. Los videos estan en la carpeta "%OUT%" (uno por pantalla).
echo  Mandalos al chat y armo el mockup del hall con ellos.
explorer "%OUT%"
pause
goto :eof

:errdl
echo.
echo  Fallo la descarga. Revisa la conexion a internet y volve a hacer doble clic.
pause & goto :eof
:errzip
echo.
echo  No se pudo descomprimir en %TOOLS%.
echo  Suele ser el antivirus revisando los archivos: espera un minuto y volve a hacer doble clic
echo  (el zip ya quedo descargado, no se baja de nuevo).
pause & goto :eof
