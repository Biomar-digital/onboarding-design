# Render en la PC con la placa de video. Sigue desde donde quedo si se corta.
#   blender -b escena_agua.blend -P render_btw.py -- DESDE HASTA PORCENTAJE MUESTRAS CARPETA
import bpy, sys, os, time
a = sys.argv[sys.argv.index('--') + 1:]
A, B, PCT, SPP, OUT = int(a[0]), int(a[1]), int(a[2]), int(a[3]), os.path.abspath(a[4])
sc = bpy.context.scene
def use_gpu():
    pr = bpy.context.preferences.addons['cycles'].preferences
    for kind in ('OPTIX', 'CUDA', 'METAL', 'HIP', 'ONEAPI'):
        try: pr.compute_device_type = kind
        except TypeError: continue
        pr.get_devices(); devs = [d for d in pr.devices if d.type == kind]
        if devs:
            for d in pr.devices: d.use = (d.type == kind)
            sc.cycles.device = 'GPU'; print('GPU:', kind, [d.name for d in devs], flush=True); return
    print('No se encontro placa de video: renderiza con el procesador (mucho mas lento)', flush=True)
use_gpu()
sc.render.resolution_percentage = PCT; sc.cycles.samples = SPP; sc.render.use_motion_blur = True
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
def rend():
    try: bpy.ops.render.render(write_still=True)
    except RuntimeError as e:                                                    # placa sin memoria en un cuadro pesado: ese va por procesador
        if sc.cycles.device != 'GPU': raise
        print('GPU sin memoria, este cuadro va por CPU:', str(e).splitlines()[0], flush=True)
        sc.cycles.device = 'CPU'
        try: bpy.ops.render.render(write_still=True)
        finally: sc.cycles.device = 'GPU'
os.makedirs(OUT, exist_ok=True)
for f in range(A, B + 1):                                                       # cuadro por cuadro en orden (las particulas lo necesitan)
    sc.frame_set(f); p = os.path.join(OUT, f'btw_{f:04d}.png')
    if os.path.exists(p): continue
    t = time.time(); sc.render.filepath = p; rend()
    print(f'CUADRO {f} de {B}  ({time.time() - t:.0f} s)', flush=True)
print('RENDER_OK')
