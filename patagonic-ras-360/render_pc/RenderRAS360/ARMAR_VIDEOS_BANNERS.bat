@echo off
setlocal enabledelayedexpansion
title Armar los videos de los banners (cuadros de blender.farm -> MP4)
rem Arrastra encima de este .bat las carpetas con los cuadros PNG (una por banner, por ejemplo "frontal" y "lateral").
rem Arma un MP4 por carpeta, al lado de la carpeta: 24 fps, 90 s, loop perfecto, calidad alta.
set "FF=%LOCALAPPDATA%\RAS360\ffmpeg\bin\ffmpeg.exe"
if not exist "%FF%" (echo No encuentro ffmpeg en "%FF%". Abri una vez RENDER_RAS360.bat para que lo baje. & pause & goto :eof)
if "%~1"=="" (
  echo Arrastra ENCIMA de este archivo las carpetas con los cuadros ^(una por banner^).
  pause & goto :eof
)
:next
if "%~1"=="" goto :done
set "DIR=%~f1"
set "NAME=%~n1"
set "LST=%TEMP%\ras_%RANDOM%.txt"
if exist "!LST!" del "!LST!"
set /a N=0
for /f "delims=" %%f in ('dir /b /s /on "!DIR!\*.png" 2^>nul ^| sort') do (
  echo file '%%f'>>"!LST!"
  set /a N+=1
)
echo.
echo ==== !NAME!: !N! cuadros
if !N! LSS 1 (echo    No hay PNG en esa carpeta. & shift & goto :next)
if not !N!==2160 echo    OJO: se esperaban 2160 cuadros. Revisa que hayas bajado todos.
rem sin vineteo: los dos banners estan pegados en la esquina y el vineteo oscureceria la union
"%FF%" -y -loglevel error -r 24 -f concat -safe 0 -i "!LST!" -vf "unsharp=5:5:0.4,noise=alls=3:allf=t,format=yuv420p" -r 24 -c:v libx264 -preset slow -crf 14 -movflags +faststart "%~dp1!NAME!.mp4"
if errorlevel 1 (echo    Fallo al armar el video.) else (echo    OK: "%~dp1!NAME!.mp4")
del "!LST!"
shift
goto :next
:done
echo.
echo Listo.
pause
