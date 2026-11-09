# Video 3D del fry de trucha (personaje): nada, frena, mira hacia arriba con duda y aparece una burbuja de pensamiento vacia.
# El cuerpo y las aletas salen de la silueta exacta del icono (.ai -> svg -> extraer_silueta.py -> silueta.json).
# Look estilizado (Eevee), 1920x1080, 25 fps, 5 s.
#   blender -b -P fry_escena.py -- silueta.json SALIDA_DIR [W] [SAMPLES] [FRAMES ej 1-125] [--save escena.blend]
# En un contenedor sin GPU, Eevee necesita Mesa EGL:  apt-get install -y libegl1 libgl1-mesa-dri libegl-mesa0
import bpy, bmesh, json, math, sys
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:]
SIL, OUT = argv[0], argv[1]
RW = int(argv[2]) if len(argv) > 2 else 1920
SPP = int(argv[3]) if len(argv) > 3 else 32
FR = argv[4] if len(argv) > 4 and not argv[4].startswith('--') else '1-125'
SAVE = argv[argv.index('--save') + 1] if '--save' in argv else None
FPS, NF = 25, 125
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def lin(c): return tuple(((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in c)
BRAND = lin((186, 229, 242))                                                     # celeste del icono
NAVY = lin((18, 52, 96))
# ------------------------------------------------------------------ silueta del icono -> 3D (1 unidad = largo del fry)
shapes = json.load(open(SIL))
X0, X1 = shapes[4]['bbox'][0], shapes[4]['bbox'][2]; S = 1 / (X1 - X0); XC = (X0 + X1) / 2; YC = 566.0
def P(x, y): return ((x - XC) * S, -(y - YC) * S)                               # artboard -> (X, Z)
outer = max(shapes[4]['subpaths'], key=len)
def section(x):                                                                  # arriba / abajo del contorno en esa x
    ys = []
    n = len(outer)
    for i in range(n):
        (xa, ya), (xb, yb) = outer[i], outer[(i + 1) % n]
        if (xa - x) * (xb - x) <= 0 and xa != xb: ys.append(ya + (yb - ya) * (x - xa) / (xb - xa))
    return (min(ys), max(ys)) if len(ys) >= 2 else None
def thick(u):                                                                    # medio espesor / media altura, de cola (0) a nariz (1)
    if u < 0.10: return 0.07
    if u < 0.22: return 0.07 + (u - 0.10) / 0.12 * 0.33
    if u < 0.72: return 0.40 + (u - 0.22) / 0.50 * 0.18
    return 0.58
NS, M = 90, 40
rings = []
for k in range(NS + 1):
    u = k / NS; x = X0 + 1.2 + u * (X1 - X0 - 2.4)
    sct = section(x)
    if sct is None: continue
    top, bot = sct; X, Zt = P(x, top); _, Zb = P(x, bot)
    zc, h = (Zt + Zb) / 2, (Zt - Zb) / 2; w = h * thick(u)
    if u > 0.94: w *= max(0.25, 1 - (u - 0.94) / 0.06 * 0.6)
    rings.append([(X, w * math.sin(2 * math.pi * j / M), zc + h * math.cos(2 * math.pi * j / M)) for j in range(M)])
me = bpy.data.meshes.new('fry'); bm = bmesh.new()
vv = [[bm.verts.new(p) for p in r] for r in rings]
for a, b in zip(vv[:-1], vv[1:]):
    for j in range(M): bm.faces.new((a[j], a[(j + 1) % M], b[(j + 1) % M], b[j]))
bm.faces.new(vv[0][::-1]); bm.faces.new(vv[-1])
bm.to_mesh(me); body = bpy.data.objects.new('FRY_cuerpo', me); sc.collection.objects.link(body)
for p in me.polygons: p.use_smooth = True
sub = body.modifiers.new('sub', 'SUBSURF'); sub.levels = sub.render_levels = 1
def half_w(X):                                                                   # medio espesor del cuerpo en X (para apoyar ojos/aletas)
    best = min(rings, key=lambda r: abs(r[0][0] - X)); return max(abs(p[1]) for p in best)
def z_mid(X):
    best = min(rings, key=lambda r: abs(r[0][0] - X)); zs = [p[2] for p in best]; return (max(zs) + min(zs)) / 2, (max(zs) - min(zs)) / 2
def flat_poly(name, shp, y, rot_x=0.0, th=0.004):
    pts = [P(*q) for q in max(shp['subpaths'], key=len)]
    m = bpy.data.meshes.new(name); b = bmesh.new()
    vs = [b.verts.new((X, 0, Z)) for X, Z in pts[:-1]]; b.faces.new(vs); b.to_mesh(m)
    o = bpy.data.objects.new(name, m); sc.collection.objects.link(o)
    o.location.y = y; o.rotation_euler.x = rot_x
    sol = o.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = th; sol.offset = 0
    sb = o.modifiers.new('sub', 'SUBSURF'); sb.levels = sb.render_levels = 1
    return o
dorsal = flat_poly('FRY_aleta_dorsal', shapes[2], 0.0)
fins = [dorsal]
for k in (0, 1):
    for sgn in (-1, 1):
        cx = sum(P(*q)[0] for q in shapes[k]['subpaths'][0]) / len(shapes[k]['subpaths'][0])
        fins.append(flat_poly(f'FRY_aleta_{k}_{sgn}', shapes[k], sgn * half_w(cx) * 0.55, sgn * math.radians(-18)))
# ------------------------------------------------------------------ materiales
def mat(name, col, rough=0.4, alpha=1.0, emit=0.0, sss=0.0, rim=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (*col, 1); bs.inputs['Roughness'].default_value = rough
    bs.inputs['Alpha'].default_value = alpha
    if emit: bs.inputs['Emission Color'].default_value = (*col, 1); bs.inputs['Emission Strength'].default_value = emit
    if sss: bs.inputs['Subsurface Weight'].default_value = sss; bs.inputs['Subsurface Radius'].default_value = (0.05, 0.08, 0.1)
    if alpha < 1: m.surface_render_method = 'BLENDED'
    if rim:                                                                       # brillo de borde (estilo animacion)
        lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
        mx = nt.nodes.new('ShaderNodeMixRGB'); mx.inputs['Color1'].default_value = (*col, 1); mx.inputs['Color2'].default_value = (*rim, 1)
        nt.links.new(lw.outputs['Facing'], mx.inputs['Fac']); nt.links.new(mx.outputs['Color'], bs.inputs['Base Color'])
    return m
m_body = mat('cuerpo', BRAND, 0.35, sss=0.15, rim=lin((235, 250, 255)))
# contra-sombreado: lomo un poco mas oscuro, panza mas clara (gradiente en Z del objeto)
nt = m_body.node_tree; tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.09; mr.inputs['From Max'].default_value = 0.11
cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*lin((222, 244, 250)), 1); cr.color_ramp.elements[1].color = (*lin((120, 190, 220)), 1)
mx2 = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeMixRGB'][0]
nt.links.new(tc.outputs['Object'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], cr.inputs['Fac'])
nt.links.new(cr.outputs['Color'], mx2.inputs['Color1'])
body.data.materials.append(m_body)
m_fin = mat('aletas', lin((215, 242, 250)), 0.3, alpha=0.85)
for f in fins: f.data.materials.append(m_fin)
m_white = mat('ojo_blanco', (0.95, 0.97, 1.0), 0.15); m_navy = mat('pupila', NAVY, 0.1); m_hl = mat('brillo', (1, 1, 1), 0.1, emit=4)
# ------------------------------------------------------------------ cara: ojos, ceja, boca (sobre el ojo y la boca del icono)
EX, EZ = P(1298, 555); ER = 0.044
eyes = []
for sgn in (-1, 1):
    yb = sgn * half_w(EX) * 0.86
    piv = bpy.data.objects.new(f'FRY_ojo_piv_{sgn}', None); sc.collection.objects.link(piv); piv.location = (EX, yb, EZ)
    ctl = bpy.data.objects.new(f'FRY_ojo_ctl_{sgn}', None); sc.collection.objects.link(ctl); ctl.parent = piv   # mirada + parpadeo
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER, location=(0, 0, 0), segments=32, ring_count=16); ball = bpy.context.object
    ball.name = f'FRY_ojo_{sgn}'; ball.data.materials.append(m_white); ball.parent = ctl
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.6, location=(0.004, sgn * ER * 0.8, 0.006), segments=24, ring_count=12); pup = bpy.context.object
    pup.scale.y = 0.55; pup.data.materials.append(m_navy); pup.parent = ctl; pup.name = f'FRY_pupila_{sgn}'
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.17, location=(0.012, sgn * ER * 0.98, 0.018)); hl = bpy.context.object
    hl.data.materials.append(m_hl); hl.parent = ctl; hl.name = f'FRY_brillo_{sgn}'
    for o in (ball, pup, hl):
        for p in o.data.polygons: p.use_smooth = True
    # ceja: arco fino sobre el ojo, apoyado en la superficie del cuerpo
    cu = bpy.data.curves.new(f'ceja_{sgn}', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0042; cu.bevel_resolution = 3
    spl = cu.splines.new('BEZIER'); spl.bezier_points.add(2)
    for i, (dx, dz) in enumerate(((-0.034, 0.040), (0.0, 0.052), (0.030, 0.046))):
        bp = spl.bezier_points[i]; bp.co = (dx, sgn * 0.004, dz); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    brow = bpy.data.objects.new(f'FRY_ceja_{sgn}', cu); sc.collection.objects.link(brow); brow.parent = piv
    brow.data.materials.append(m_navy)
    eyes.append((piv, brow, ctl))
MX, MZ = P(1371, 604)
cu = bpy.data.curves.new('boca', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0032; cu.bevel_resolution = 3
for sgn in (-1, 1):
    spl = cu.splines.new('BEZIER'); spl.bezier_points.add(2); yb = sgn * half_w(MX - 0.012) * 0.92
    for i, (dx, dz) in enumerate(((-0.028, -0.006), (-0.012, 0.0), (0.004, -0.002))):
        bp = spl.bezier_points[i]; bp.co = (MX + dx, yb * (1 - 0.3 * (i == 2)), MZ + dz); bp.handle_left_type = bp.handle_right_type = 'AUTO'
mouth = bpy.data.objects.new('FRY_boca', cu); sc.collection.objects.link(mouth); mouth.data.materials.append(m_navy)
# ------------------------------------------------------------------ rig: cadena de huesos de la cabeza a la cola, pesos por posicion en X
arm_d = bpy.data.armatures.new('rig'); rig = bpy.data.objects.new('FRY_rig', arm_d); sc.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
JX = [0.52, 0.22, 0.06, -0.09, -0.23, -0.36, -0.52]
bones = []
for i in range(len(JX) - 1):
    b = arm_d.edit_bones.new(f'b{i}'); b.head = (JX[i], 0, 0); b.tail = (JX[i + 1], 0, 0); b.roll = 0
    if bones: b.parent = bones[-1]; b.use_connect = True
    bones.append(b)
bpy.ops.object.mode_set(mode='OBJECT')
def bone_tail_inv():                                                             # hijo de hueso: Blender lo ubica en la COLA del hueso, con su orientacion
    bl = rig.data.bones['b0']; M = bl.matrix_local.copy(); M.translation = bl.tail_local
    return (rig.matrix_world @ M).inverted()
def weigh(o):
    vg = {i: o.vertex_groups.new(name=f'b{i}') for i in range(len(JX) - 1)}
    mw = o.matrix_world
    for v in o.data.vertices:
        X = (mw @ v.co).x
        c = [(JX[i] + JX[i + 1]) / 2 for i in range(len(JX) - 1)]
        if X >= c[0]: vg[0].add([v.index], 1.0, 'REPLACE'); continue
        if X <= c[-1]: vg[len(c) - 1].add([v.index], 1.0, 'REPLACE'); continue
        for i in range(len(c) - 1):
            if c[i + 1] <= X <= c[i]:
                t = (c[i] - X) / (c[i] - c[i + 1]); vg[i].add([v.index], 1 - t, 'REPLACE'); vg[i + 1].add([v.index], t, 'REPLACE'); break
for o in [body, mouth] + fins:
    if o.type == 'CURVE':
        o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'b0'; o.matrix_parent_inverse = bone_tail_inv(); continue
    weigh(o); am = o.modifiers.new('arm', 'ARMATURE'); am.object = rig; o.parent = rig
    o.modifiers.move(len(o.modifiers) - 1, 0)
for piv, brow, ctl in eyes:
    piv.parent = rig; piv.parent_type = 'BONE'; piv.parent_bone = 'b0'
    piv.matrix_parent_inverse = bone_tail_inv()
# ------------------------------------------------------------------ animacion
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
def ease(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)
AMP = [0.02, 0.05, 0.09, 0.14, 0.2, 0.27]
phase = 0.0
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    swim = 1 - 0.75 * ease((f - 40) / 25)                                         # nada rapido y despues queda flotando
    freq = 2.6 * swim + 0.9 * (1 - swim); phase += 2 * math.pi * freq / FPS
    for i, b in enumerate(rig.pose.bones):
        b.rotation_mode = 'XYZ'
        b.rotation_euler = (0, 0, AMP[i] * (0.35 + 0.65 * swim) * math.sin(phase - 0.9 * i))
        b.keyframe_insert('rotation_euler', frame=f)
    # recorrido: entra desde la izquierda, frena, sube la cabeza mirando hacia arriba
    xs = -2.4 + 2.1 * ease((f - 1) / 55) ** 0.8 + 0.05 * ease((f - 55) / 70)
    zs = 0.02 * math.sin(t * 2.1) - 0.06 + 0.05 * ease((f - 55) / 30)
    rig.location = (xs, 0, zs); rig.keyframe_insert('location', frame=f)
    pitch = -math.radians(16) * ease((f - 52) / 22) + math.radians(1.5) * math.sin(t * 1.7)
    yaw = math.radians(-6) * ease((f - 52) / 22)                                  # gira apenas hacia camara
    rig.rotation_euler = (0, pitch, yaw); rig.keyframe_insert('rotation_euler', frame=f)
    # aletas pectorales/ventrales aletean suave
    for k, o in enumerate(fins[1:]):
        o.rotation_euler.z = 0.25 * math.sin(t * (5 if f < 60 else 2.5) + k); o.keyframe_insert('rotation_euler', index=2, frame=f)
    # ojos: miran hacia arriba (pupila sube) + parpadeo en el frame 66; cejas: una se levanta (duda)
    look = ease((f - 56) / 14)
    blink = max(0.0, 1 - abs(f - 66) / 3.0)
    for (piv, brow, ctl), sgn in zip(eyes, (-1, 1)):
        ctl.scale = (1, 1, 1 - 0.92 * blink); ctl.keyframe_insert('scale', frame=f)
        ctl.rotation_euler = (sgn * 0.38 * look, 0, -sgn * 0.25 * look); ctl.keyframe_insert('rotation_euler', frame=f)
        lift = ease((f - 60) / 10)
        brow.location = (0, 0, 0.010 * lift); brow.rotation_euler = (sgn * 0.0, 0.32 * lift, 0)
        brow.keyframe_insert('location', frame=f); brow.keyframe_insert('rotation_euler', frame=f)
for fc in (rig.animation_data.action.fcurves if rig.animation_data else []):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# ------------------------------------------------------------------ escenario: agua azul estilizada (como la ilustracion de referencia)
def plane(name, w, h, loc, colr, emit=1.0, alpha=1.0, rot=(math.radians(90), 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = name; o.scale = (w, h, 1)
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree; n.nodes.clear()
    out = n.nodes.new('ShaderNodeOutputMaterial'); em = n.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = emit
    if isinstance(colr, tuple) and len(colr) == 2:                               # gradiente vertical
        tc = n.nodes.new('ShaderNodeTexCoord'); sp = n.nodes.new('ShaderNodeSeparateXYZ'); ramp = n.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (*colr[0], 1); ramp.color_ramp.elements[1].color = (*colr[1], 1)
        n.links.new(tc.outputs['UV'], sp.inputs[0]); n.links.new(sp.outputs['Y'], ramp.inputs['Fac']); n.links.new(ramp.outputs['Color'], em.inputs['Color'])
    else: em.inputs['Color'].default_value = (*colr, 1)
    if alpha < 1:
        tr = n.nodes.new('ShaderNodeBsdfTransparent'); mx = n.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = alpha
        n.links.new(tr.outputs[0], mx.inputs[1]); n.links.new(em.outputs[0], mx.inputs[2]); n.links.new(mx.outputs[0], out.inputs[0]); m.surface_render_method = 'BLENDED'
    else: n.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m); return o
plane('FONDO_agua', 30, 17, (0, 9, 1.2), (lin((14, 62, 128)), lin((92, 168, 222))))
def band(name, y, z0, amp, colr, seed, alpha=1.0):                              # colinas/ondas de fondo en silueta
    import random; r = random.Random(seed); m = bpy.data.meshes.new(name); b = bmesh.new(); N = 80; W_ = 26
    top = []
    for i in range(N + 1):
        x = -W_ / 2 + W_ * i / N; z = z0 + amp * (math.sin(x * 0.45 + seed) + 0.5 * math.sin(x * 1.1 + seed * 2))
        top.append(b.verts.new((x, y, z)))
    bot = [b.verts.new((v.co.x, y, -8)) for v in top]
    for i in range(N): b.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    b.to_mesh(m); o = bpy.data.objects.new(name, m); sc.collection.objects.link(o)
    mm = bpy.data.materials.new(name); mm.use_nodes = True; nn = mm.node_tree; nn.nodes.clear()
    out = nn.nodes.new('ShaderNodeOutputMaterial'); em = nn.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*colr, 1)
    nn.links.new(em.outputs[0], out.inputs[0]); o.data.materials.append(mm); return o
band('FONDO_onda1', 7.5, 0.6, 0.35, lin((40, 110, 180)), 1.0)
band('FONDO_onda2', 6.0, -0.4, 0.3, lin((28, 88, 160)), 2.3)
band('FONDO_onda3', 4.6, -1.3, 0.25, lin((18, 66, 132)), 3.7)
def kelp(name, x, y, hgt, colr, seed):                                           # plantas en silueta (se mecen)
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.07; cu.bevel_resolution = 2
    spl = cu.splines.new('BEZIER'); n = 5; spl.bezier_points.add(n - 1)
    for i in range(n):
        bp = spl.bezier_points[i]; bp.co = (x + 0.12 * math.sin(i * 1.3 + seed), y, -1.6 + hgt * i / (n - 1)); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        bp.radius = 1.4 - i / n
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o)
    mm = bpy.data.materials.new(name); mm.use_nodes = True; nn = mm.node_tree; nn.nodes.clear()
    out = nn.nodes.new('ShaderNodeOutputMaterial'); em = nn.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*colr, 1)
    nn.links.new(em.outputs[0], out.inputs[0]); o.data.materials.append(mm)
    o.rotation_mode = 'XYZ'
    for f in range(1, NF + 1, 5):
        o.rotation_euler.y = 0.06 * math.sin(f / FPS * 1.3 + seed); o.keyframe_insert('rotation_euler', index=1, frame=f)
    return o
for i, (x, y, hh, s) in enumerate(((-2.6, 3.2, 1.5, 0.3), (-2.25, 3.4, 1.1, 1.7), (2.5, 3.3, 1.3, 2.9), (2.85, 3.0, 0.9, 4.2))):
    kelp(f'FONDO_planta{i}', x, y, hh, lin((16, 60, 118)), s)
for i in range(5):                                                              # rayos de luz desde arriba a la derecha
    o = plane(f'FONDO_rayo{i}', 0.35 + 0.25 * (i % 2), 9, (0.4 + i * 0.7, 3.5 + 0.2 * i, 1.0), (lin((120, 190, 240)), lin((200, 235, 255))), emit=1.0, alpha=0.06,
              rot=(math.radians(90), math.radians(-24 + 3 * i), 0))
import random; R = random.Random(4)
m_part = mat('particula', (0.75, 0.88, 1.0), 0.3, emit=1.2, alpha=0.6)
for i in range(46):                                                             # particulas / burbujitas en suspension
    bpy.ops.mesh.primitive_uv_sphere_add(radius=R.uniform(0.008, 0.03), location=(R.uniform(-3, 3), R.uniform(0.5, 3.5), R.uniform(-1.6, 1.6)), segments=12, ring_count=8)
    o = bpy.context.object; o.name = f'FONDO_part{i}'; o.data.materials.append(m_part)
    z0 = o.location.z; v = R.uniform(0.05, 0.15)
    o.keyframe_insert('location', index=2, frame=1); o.location.z = z0 + v * NF / FPS; o.keyframe_insert('location', index=2, frame=NF)
    for fc in o.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# ------------------------------------------------------------------ burbujas de aire de la boca + burbuja de pensamiento VACIA
bpy.context.view_layer.update()
m_air = mat('aire', (0.85, 0.95, 1.0), 0.05, alpha=0.45, emit=0.4)
m_think = mat('pensamiento', (0.93, 0.97, 1.0), 0.5, emit=0.9, alpha=0.95)
def mouth_world(f):                                                              # boca en el mundo en ese frame (la cabeza casi no ondula)
    sc.frame_set(f); return rig.matrix_world @ Vector((MX + 0.02, 0, MZ))
for i, (f0, r) in enumerate(((64, 0.018), (70, 0.012), (75, 0.022))):          # burbujitas que suben desde la boca
    p0 = mouth_world(f0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=p0, segments=16, ring_count=10); o = bpy.context.object; o.name = f'AIRE_{i}'
    o.data.materials.append(m_air); o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f0)
    o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=f0 + 4)
    o.location = p0; o.keyframe_insert('location', frame=f0)
    o.location = p0 + Vector((0.06 + 0.03 * i, 0, 0.55)); o.keyframe_insert('location', frame=f0 + 40)
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f0 + 40)
pm = mouth_world(80)
trail = [(pm + Vector((0.07, -0.05, 0.05)), 0.013, 80), (pm + Vector((0.12, -0.05, 0.10)), 0.018, 84), (pm + Vector((0.18, -0.05, 0.155)), 0.024, 88)]
big_c = pm + Vector((0.34, -0.05, 0.27))
def disk(name, loc, rx, rz, f0, dur=7):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1, depth=0.01, location=loc, rotation=(math.radians(90), 0, 0)); o = bpy.context.object
    o.name = name; o.data.materials.append(m_think)
    bev = o.modifiers.new('bev', 'BEVEL'); bev.width = 0.004; bev.segments = 3
    for p in o.data.polygons: p.use_smooth = True
    for f, s in ((f0, 0.0), (f0 + dur * 0.6, 1.12), (f0 + dur, 1.0)):
        o.scale = (rx * s, rz * s, 1); o.keyframe_insert('scale', frame=int(f))
    for k in range(int(f0 + dur) + 2, NF + 1, 6):                               # flota suave
        o.location = loc + Vector((0, 0, 0.008 * math.sin(k / FPS * 2.4))); o.keyframe_insert('location', frame=k)
    return o
for i, (loc, r, f0) in enumerate(trail): disk(f'PENSAMIENTO_burbuja{i}', loc, r, r, f0, 6)
disk('PENSAMIENTO_globo', big_c, 0.14, 0.105, 92, 9)
# ------------------------------------------------------------------ luz, camara, render
sun = bpy.data.objects.new('SOL', bpy.data.lights.new('SOL', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 3.2; sun.data.color = (1.0, 0.97, 0.92); sun.rotation_euler = (math.radians(30), math.radians(-25), 0); sun.data.angle = math.radians(8)
fill = bpy.data.objects.new('RELLENO', bpy.data.lights.new('RELLENO', 'AREA')); sc.collection.objects.link(fill)
fill.data.energy = 120; fill.data.size = 4; fill.data.color = (0.6, 0.8, 1.0); fill.location = (-1.5, -3, -1.2); fill.rotation_euler = (math.radians(-110), 0, math.radians(-25))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (*lin((40, 110, 180)), 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 0.6
cam = bpy.data.objects.new('CAM', bpy.data.cameras.new('CAM')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 50; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.2
for f, y, x in ((1, -2.9, 0.0), (NF, -2.5, 0.1)):
    cam.location = (x, y, 0.12); cam.rotation_euler = (math.radians(90), 0, 0); cam.keyframe_insert('location', frame=f)
cam.data.dof.focus_distance = 2.6
sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.eevee.taa_render_samples = SPP
sc.render.resolution_x = RW; sc.render.resolution_y = int(RW * 9 / 16); sc.render.film_transparent = False
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
sc.render.image_settings.file_format = 'PNG'
if SAVE: bpy.ops.wm.save_as_mainfile(filepath=SAVE)
a, b = (int(v) for v in FR.split('-'))
for f in range(a, b + 1):
    sc.frame_set(f); sc.render.filepath = f'{OUT}/f_{f:04d}.png'; bpy.ops.render.render(write_still=True)
print('FRY_DONE')
