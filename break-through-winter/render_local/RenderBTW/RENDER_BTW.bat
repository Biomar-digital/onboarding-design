@echo off
title Break Through Winter - render en tu compu
cd /d "%~dp0"
set BL=blender-4.2.23-windows-x64\blender.exe
set CURL=curl -L -f --ssl-no-revoke --retry 3
set PH=https://dl.polyhaven.org/file/ph-assets
echo ============================================================
echo  BREAK THROUGH WINTER - video 1080x1350 (12 s) + foto 2160x2700
echo  Deja la compu prendida. Si se corta, volve a hacer doble clic:
echo  sigue desde donde quedo.
echo ============================================================
echo.
if not exist "%BL%" (
  echo [1/7] Descargando Blender 4.2 portable ^(380 MB, una sola vez^)...
  %CURL% -o blender42.zip https://download.blender.org/release/Blender4.2/blender-4.2.23-windows-x64.zip || goto :err
  echo Descomprimiendo...
  tar -xf blender42.zip || goto :err
  del blender42.zip
)
if not exist recursos\listo.txt (
  echo [2/7] Descargando cielo, nieve, hielo y abetos ^(Poly Haven y ambientCG, libres^)...
  if not exist recursos\textures mkdir recursos\textures
  %CURL% -o recursos\winter_lake_01_4k.hdr %PH%/HDRIs/hdr/4k/winter_lake_01_4k.hdr || goto :err
  %CURL% -o recursos\snow_02_diff_2k.jpg %PH%/Textures/jpg/2k/snow_02/snow_02_diff_2k.jpg || goto :err
  %CURL% -o recursos\snow_02_nor_gl_2k.jpg %PH%/Textures/jpg/2k/snow_02/snow_02_nor_gl_2k.jpg || goto :err
  %CURL% -o recursos\snow_02_rough_2k.jpg %PH%/Textures/jpg/2k/snow_02/snow_02_rough_2k.jpg || goto :err
  %CURL% -o recursos\snow_02_disp_2k.jpg %PH%/Textures/jpg/2k/snow_02/snow_02_disp_2k.jpg || goto :err
  %CURL% -o recursos\fir_tree_01_1k.blend %PH%/Models/blend/1k/fir_tree_01/fir_tree_01_1k.blend || goto :err
  %CURL% -o recursos\textures\fir_tree_01_bark_diff_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_bark_diff_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_bark_disp_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_bark_disp_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_bark_nor_gl_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_bark_nor_gl_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_bark_rough_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_bark_rough_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_a_diff_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_a_diff_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_a_nor_gl_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_a_nor_gl_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_a_rough_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_a_rough_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_b_diff_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_b_diff_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_b_nor_gl_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_b_nor_gl_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_b_rough_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_b_rough_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_c_diff_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_c_diff_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_c_nor_gl_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_c_nor_gl_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_trunk_c_rough_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_trunk_c_rough_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_twig_alpha_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_twig_alpha_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_twig_diff_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_twig_diff_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_twig_mask_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_twig_mask_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_twig_nor_gl_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_twig_nor_gl_1k.png || goto :err
  %CURL% -o recursos\textures\fir_tree_01_twig_rough_1k.png %PH%/Models/png/1k/fir_tree_01/fir_tree_01_twig_rough_1k.png || goto :err
  %CURL% -o recursos\Ice003.zip "https://ambientcg.com/get?file=Ice003_2K-JPG.zip" || goto :err
  tar -xf recursos\Ice003.zip -C recursos || goto :err
  del recursos\Ice003.zip
  echo ok> recursos\listo.txt
)
if not exist trabajo mkdir trabajo
if not exist trabajo\trucha_rig.blend (
  echo [3/7] Armando la trucha con su rig...
  "%BL%" -b -P fuente\trucha_rig.py -- "%CD%\fuente\trucha_sin_aletas.glb" "%CD%\trabajo\trucha_rig.blend" || goto :err
)
if not exist trabajo\escena.blend (
  echo [4/7] Armando el estanque congelado...
  "%BL%" -b -P fuente\escena_hielo.py -- "%CD%\trabajo\trucha_rig.blend" "%CD%\trabajo\escena.blend" "%CD%\recursos" || goto :err
)
if not exist trabajo\escena_agua.blend (
  echo [5/7] Simulando el agua ^(usa el procesador, 20 a 60 min^)...
  "%BL%" -b "%CD%\trabajo\escena.blend" -P fuente\agua_flip.py -- 160 "%CD%\trabajo\escena_agua.blend" || goto :err
)
echo [6/7] Renderizando los 300 cuadros con la placa de video...
"%BL%" -b "%CD%\trabajo\escena_agua.blend" -P fuente\render_btw.py -- 1 300 100 256 cuadros || goto :err
if not exist BreakThroughWinter_1080x1350.mp4 (
  "%BL%" -b --factory-startup -P fuente\video_mp4.py -- cuadros BreakThroughWinter_1080x1350.mp4 || goto :err
)
echo [7/7] Foto del apice en alta ^(2160x2700^)...
"%BL%" -b "%CD%\trabajo\escena_agua.blend" -P fuente\render_btw.py -- 245 245 200 512 foto || goto :err
echo.
echo LISTO: BreakThroughWinter_1080x1350.mp4 y la foto en la carpeta "foto"
start "" "BreakThroughWinter_1080x1350.mp4"
pause
exit /b

:err
echo.
echo Hubo un error. Saca una captura de esta ventana y mandasela a Claude.
pause
