# Arma el MP4 (H.264, 25 fps) con el propio Blender, sin instalar nada.
#   blender -b --factory-startup -P video_mp4.py -- CARPETA_CUADROS salida.mp4
import bpy, sys, os
a = sys.argv[sys.argv.index('--') + 1:]; SRC, MP4 = os.path.abspath(a[0]), os.path.abspath(a[1])
fr = sorted(f for f in os.listdir(SRC) if f.lower().endswith('.png'))
sc = bpy.context.scene; sc.sequence_editor_create()
st = sc.sequence_editor.sequences.new_image('cuadros', os.path.join(SRC, fr[0]), 1, 1)
for f in fr[1:]: st.elements.append(f)
im = bpy.data.images.load(os.path.join(SRC, fr[0])); W, H = im.size
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.fps = 25; sc.frame_start = 1; sc.frame_end = len(fr)
sc.render.image_settings.file_format = 'FFMPEG'; ff = sc.render.ffmpeg
ff.format = 'MPEG4'; ff.codec = 'H264'; ff.constant_rate_factor = 'HIGH'; ff.ffmpeg_preset = 'GOOD'
sc.render.filepath = MP4; sc.render.use_file_extension = False
bpy.ops.render.render(animation=True)
print('MP4_OK', MP4)
