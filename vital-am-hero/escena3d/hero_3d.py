# Hero SmartCare VITAL AM desde la escena 3D final del film (film.blend): una camara vertical en la superficie del
# estanque. Se renderiza dos veces (camara apenas arriba del agua / apenas abajo) y se une en la linea del agua,
# igual que los planos de superficie del film. Arriba: amanecer sobre el estanque y las palmeras. Abajo: el camaron del
# cliente subiendo hacia el alimento que cae, otros camarones detras, rayos de sol.
# blender -b film.blend -P hero_3d.py -- SALIDA_DIR ANCHO MUESTRAS [air|under|both]
import bpy, sys, os, math, json
from mathutils import Vector, Matrix, Euler
a = sys.argv[sys.argv.index('--') + 1:]; OUT = a[0]; RW = int(a[1]); SPP = int(a[2]); WHICH = a[3] if len(a) > 3 else 'both'
sys.path.insert(0, os.environ['FILM_SCRIPTS'])
import drive
sc = bpy.context.scene
P = json.load(open(os.environ['HERO_PARAMS'])) if os.environ.get('HERO_PARAMS') else {}
def g(k, d): return P.get(k, d)
# ---- camara vertical
cam = sc.camera; cam.data.lens = g('lens', 22); cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 36
sc.render.resolution_x = RW; sc.render.resolution_y = RW * 3 // 2; sc.render.resolution_percentage = 100
CP = Vector(g('cam_pos', [0.0, -0.6, 0.0])); pitch = math.radians(g('pitch', -8.0)); yaw = math.radians(g('yaw', 0.0))
look = Vector((math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
def place_cam(z):
    q = look.to_track_quat('-Z', 'Y'); cam.matrix_world = Matrix.Translation(Vector((CP.x, CP.y, z))) @ q.to_matrix().to_4x4()
# ---- camarones: protagonista + algunos de fondo; el resto oculto
sh = drive.Shrimp()
for r in sh.rigs:
    r.hide_render = True
    for c in r.children_recursive: c.hide_render = True
for o in bpy.data.objects:
    if o.name.startswith('SHRL_'): o.data.energy = 0.0
SH = g('shrimp', [[0, [0.10, 0.45, -0.16], [0, -28, 15], 1.0, 2.1]])     # [indice, posicion, rotacion XYZ grados, escala, fase de nado]
for i, pos, rot, s, ph in SH:
    r = sh.rigs[i]; r.hide_render = False
    for c in r.children_recursive: c.hide_render = False
    r.matrix_world = Matrix.Translation(Vector(pos)) @ Euler([math.radians(v) for v in rot], 'XYZ').to_matrix().to_4x4() @ Matrix.Scale(0.013 * s, 4)   # el rig del cliente va a escala 0.013 (camaron de ~14 cm)
    sh.pose(r, ph)
    sl = bpy.data.objects.get(r.name.replace('SHR_', 'SHRL_'))
    if sl: sl.data.energy = drive.SHRL_W if hasattr(drive, 'SHRL_W') else 0.0
# ---- alimento: estela de pellets desde la superficie hacia la cabeza del protagonista
pool = [o for o in bpy.data.objects if o.name.startswith('PEL_') and o.name != 'PEL_SRC']
for q in pool: q.hide_render = True
import random
rr = random.Random(5); A = Vector(g('feed_a', [-0.05, 0.75, -0.01])); B = Vector(g('feed_b', [0.16, 0.48, -0.10]))
NPEL = g('npel', 26); PS = g('pel_scale', 0.003)                                   # malla del pellet ~1.9 u -> ~6 mm (el doble del real, para que se lea)
for k in range(min(NPEL, len(pool))):
    t = rr.random() ** 0.8; p = A.lerp(B, t) + Vector((rr.gauss(0, 0.012 + 0.03 * t), rr.gauss(0, 0.02), rr.gauss(0, 0.006 + 0.012 * t)))
    pool[k].matrix_world = Matrix.Translation(p) @ Euler((rr.uniform(0, 6.3), rr.uniform(0, 6.3), rr.uniform(0, 6.3))).to_matrix().to_4x4() @ Matrix.Scale(PS, 4)
    pool[k].hide_render = False
# ---- sin efectos de lanzamiento (salpicaduras, anillos, burbujas del film), sin la bolsa ni el granjero
for o in bpy.data.objects:
    if o.name.startswith(('DROP_', 'RING_', 'CROWN_', 'BUB_', 'BAG', 'JS_BAG', 'FARMER', 'SCOOP', 'FIST', 'BUCKET', 'HAND', 'PHONE', 'ROOM', 'ELBOW')):
        o.hide_render = True
        for c in o.children_recursive: c.hide_render = True
sc.cycles.samples = SPP; sc.cycles.use_denoising = True
pm_ = bpy.data.objects['PEL_000'].active_material                     # pellet marron, como en el film
if pm_ and pm_.use_nodes:
    rp_ = [x for x in pm_.node_tree.nodes if x.type == 'VALTORGB']
    if rp_:
        k_ = g('pel_dark', 0.55); e_ = rp_[0].color_ramp.elements
        e_[0].color = (0.13 * k_, 0.07 * k_, 0.035 * k_, 1); e_[1].color = (0.30 * k_, 0.18 * k_, 0.09 * k_, 1)
os.makedirs(OUT, exist_ok=True)
SUN = g('sun', [0.0, 0.06, -1.0])                                       # direccion del sol (coordenadas del previs): bajo, al frente
for fo in (['air', 'under'] if WHICH == 'both' else [WHICH]):
    under = fo == 'under'
    d = {'sun': SUN, 'under': under, 'room': False, 'shot': 's4', 'F': 300, 'f': 300}
    drive.set_mode(d)
    place_cam(-0.018 if under else 0.008)
    cam.data.clip_start = 0.005; cam.data.clip_end = 2000
    mo = bpy.data.objects.get('MOTES')
    if mo: mo.hide_render = not under
    if not under:                                                      # arriba: sol de amanecer al frente, sobre las palmeras
        so = bpy.data.objects['SUN']; sunv = Vector((SUN[0], -SUN[2], SUN[1])).normalized()
        so.rotation_euler = (-sunv).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(OUT, 'hero_%s.png' % fo); sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True); print('RENDER', fo, flush=True)
# linea del agua en pantalla (para unir las dos mitades)
from bpy_extras.object_utils import world_to_camera_view as w2c
place_cam(0.0); bpy.context.view_layer.update()
far = cam.matrix_world.translation + Vector((look.x, look.y, 0)).normalized() * 500; far.z = 0
json.dump({'wl': 1 - w2c(sc, cam, far).y}, open(os.path.join(OUT, 'waterline.json'), 'w'))
print('HERO_DONE')
