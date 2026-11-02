@echo off
echo Iniciando Mejorar video...
title Mejorar video - mas resolucion y mas cuadros por segundo (IA en tu placa de video)
cd /d "%~dp0"
echo Carpeta de la herramienta: %CD%
rem Sube la resolucion (Real-ESRGAN) y los cuadros por segundo (RIFE, interpolacion de movimiento)
rem de cualquier video, manteniendo SIEMPRE su proporcion (horizontal, vertical, cuadrado...).

rem ---- videos de entrada: arrastrados sobre el .bat (uno o varios), o todos los videos de esta carpeta
set "LIST="
:args
if "%~1"=="" goto :argsdone
set LIST=%LIST% "%~f1"
shift
goto :args
:argsdone
setlocal enabledelayedexpansion
if not defined LIST for %%f in (*.mp4 *.mov *.mkv *.webm *.avi *.m4v) do (
  set "NM=%%~nf"
  if /i not "!NM:~-9!"=="_MEJORADO" set LIST=!LIST! "%%~ff"
)
if not defined LIST (
  echo.
  echo No encontre videos.
  echo  - Arrastra los videos ENCIMA de MEJORAR_VIDEO.bat, o
  echo  - copialos en esta carpeta y hace doble clic en MEJORAR_VIDEO.bat
  echo IMPORTANTE: primero descomprimi el zip ^(clic derecho - Extraer todo^).
  pause
  goto :eof
)
echo Videos:
for %%v in (%LIST%) do echo   %%~nxv

echo.
echo  Que tipo de video es?
echo    1 = Video de IA, 3D o animacion  (rapido)            ^<- recomendado
echo    2 = Filmacion / foto real         (maxima calidad, varias veces mas lento)
echo.
choice /c 12 /n /m "Elegi 1 o 2: "
if errorlevel 2 (set "MODEL=realesrgan-x4plus" & set "FIX=4") else (set "MODEL=realesr-animevideov3" & set "FIX=0")

echo.
echo  Resolucion de salida (se mantiene la proporcion del video):
echo    1 = Full HD : el lado corto queda en 1080   ^<- recomendado
echo    2 = 4K      : el lado corto queda en 2160
echo    3 = El doble de la original
echo.
choice /c 123 /n /m "Elegi 1, 2 o 3: "
if errorlevel 3 (set "SHORT=0" & set "RTAG=x2") else if errorlevel 2 (set "SHORT=2160" & set "RTAG=4K") else (set "SHORT=1080" & set "RTAG=HD")

echo.
echo  Cuadros por segundo de salida:
echo    1 = 60 fps   (movimiento muy fluido)   ^<- recomendado
echo    2 = 50 fps
echo    3 = 30 fps
echo    4 = Dejar los del original
echo.
choice /c 1234 /n /m "Elegi 1, 2, 3 o 4: "
if errorlevel 4 (set "TFPS=0") else if errorlevel 3 (set "TFPS=30") else if errorlevel 2 (set "TFPS=50") else (set "TFPS=60")

rem ---- herramientas (se bajan una sola vez)
set "ESR=realesrgan\realesrgan-ncnn-vulkan.exe"
set "RIFE=rife\rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe"
set "FF=ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
set "FP=ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe"
if not exist "%ESR%" (
  echo Descargando Real-ESRGAN ^(50 MB, una sola vez^)...
  curl -L -o esr.zip https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip || goto :err
  mkdir realesrgan 2>nul
  tar -xf esr.zip -C realesrgan || goto :err
  del esr.zip
)
if not exist "%RIFE%" (
  echo Descargando RIFE ^(430 MB, una sola vez^)...
  curl -L -o rife.zip https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-windows.zip || goto :err
  mkdir rife 2>nul
  tar -xf rife.zip -C rife || goto :err
  del rife.zip
)
if not exist "%FF%" (
  echo Descargando ffmpeg ^(200 MB, una sola vez^)...
  curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip || goto :err
  tar -xf ffmpeg.zip || goto :err
  del ffmpeg.zip
)

for %%v in (%LIST%) do call :one "%%~v" || goto :err
echo.
echo LISTO. Los videos nuevos estan al lado de los originales, terminados en _MEJORADO.mp4
pause
goto :eof

:one
set "IN=%~1"
echo.
echo ==== %~nx1
rem ---- datos del original: tamano y cuadros por segundo
for /f "tokens=1,2,3 delims=," %%a in ('call "%FP%" -v error -select_streams v:0 -show_entries stream^=width^,height^,r_frame_rate -of csv^=p^=0 "%IN%"') do (set "W=%%a" & set "H=%%b" & set "SFPS=%%c")
for /f %%s in ('powershell -NoProfile -Command "[math]::Round(%SFPS%,3)"') do set "SFPSN=%%s"
if "%TFPS%"=="0" (set "OFPS=%SFPS%") else (set "OFPS=%TFPS%")
for /f %%s in ('powershell -NoProfile -Command "if(%OFPS% -le %SFPS%+0.01){0}else{1}"') do set "INTERP=%%s"
rem ---- cuanto agrandar con IA: lo necesario para llegar al lado corto pedido (x2..x4), despues se ajusta exacto
for /f %%s in ('powershell -NoProfile -Command "$s=[math]::Min(%W%,%H%); if(%SHORT% -eq 0){2}else{[math]::Max(2,[math]::Min(4,[math]::Ceiling(%SHORT%/$s)))}"') do set "SC=%%s"
if not "%FIX%"=="0" set "SC=%FIX%"
if "%SHORT%"=="0" (set "VF=scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=lanczos") else (set "VF=scale='if(lte(iw,ih),%SHORT%,-2)':'if(lte(iw,ih),-2,%SHORT%)':flags=lanczos")
if "%TFPS%"=="0" (set "FTAG=%SFPSN%") else (set "FTAG=%TFPS%")
set "UHD="
if "%SHORT%"=="2160" set "UHD=-u"
set "OUT=%~dpn1_%RTAG%_%FTAG%fps_MEJORADO.mp4"
echo     original: %W%x%H% a %SFPSN% fps   -^>  IA x%SC%  -^>  %RTAG%, %FTAG% fps

if exist tmp_in rd /s /q tmp_in
if exist tmp_up rd /s /q tmp_up
if exist tmp_fps rd /s /q tmp_fps
mkdir tmp_in tmp_up
echo [1/4] Separando cuadros...
"%FF%" -v error -i "%IN%" -fps_mode passthrough tmp_in\%%08d.png || exit /b 1
for /f %%c in ('dir /b tmp_in\*.png ^| find /c /v ""') do set "N=%%c"
echo [2/4] Subiendo resolucion con IA (%MODEL%, x%SC%) - %N% cuadros...
"%ESR%" -i tmp_in -o tmp_up -n %MODEL% -s %SC% -m realesrgan\models -f png || exit /b 1
set "FRAMES=tmp_up"
if "%INTERP%"=="1" (
  for /f %%t in ('powershell -NoProfile -Command "[math]::Round(%N%*%OFPS%/(%SFPS%))"') do set "NT=%%t"
  mkdir tmp_fps
  echo [3/4] Creando cuadros intermedios con IA ^(RIFE^): %N% -^> !NT! cuadros...
  "%RIFE%" -i tmp_up -o tmp_fps -n !NT! -m rife\rife-ncnn-vulkan-20221029-windows\rife-v4.6 %UHD% -f %%08d.png || exit /b 1
  set "FRAMES=tmp_fps"
) else (
  echo [3/4] Cuadros por segundo: se dejan como el original.
)
echo [4/4] Armando el video final...
"%FF%" -v error -y -framerate %OFPS% -i %FRAMES%\%%08d.png -i "%IN%" -map 0:v -map 1:a? -vf "%VF%" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "%OUT%" || exit /b 1
rd /s /q tmp_in tmp_up
if exist tmp_fps rd /s /q tmp_fps
for /f "tokens=1,2 delims=," %%a in ('call "%FP%" -v error -select_streams v:0 -show_entries stream^=width^,height -of csv^=p^=0 "%OUT%"') do echo     OK: %%ax%%b a %FTAG% fps  -^>  %OUT%
exit /b 0

:err
echo.
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
pause
goto :eof
