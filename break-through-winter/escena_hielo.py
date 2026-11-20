# BREAK THROUGH WINTER - estanque congelado de una granja en Dinamarca, hora azul.
# Una trucha arcoiris rompe el hielo desde abajo y sube vertical en camara lenta.
#   blender -b -P escena_hielo.py -- trucha_rig.blend escena_hielo.blend
# Despues se renderiza con:  blender -b escena_hielo.blend -a            (animacion 8 s, 25 fps, 1080x1350)
#                            blender -b escena_hielo.blend -f 150        (foto: cuadro del apice)
# Unidades: la trucha mide 1,9 (unos 50 cm reales -> 1 unidad ~ 0,26 m). Hielo arriba en z = 0.
import bpy, sys, math, random, bmesh
import numpy as np
from mathutils import Vector, Euler, Matrix
A = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = A[0], A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
for o in list(bpy.data.objects):                                                  # restos de las vistas de control
    if o.type in ('CAMERA', 'LIGHT'): bpy.data.objects.remove(o)
rng = random.Random(11)
FPS, F0, F1 = 25, 1, 200
FB = 56                                                                           # cuadro en que revienta el hielo
sc.render.fps = FPS; sc.frame_start = F0; sc.frame_end = F1
G = 37.0                                                                          # gravedad en unidades/s2 (9,8 m/s2)
sc.gravity = (0, 0, -G)
def lin(c): return tuple(((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in c)

# ------------------------------------------------------------------ tiempo: rompe a media velocidad y entra en camara lenta extrema
# ts(f) = segundos "reales" de la fisica transcurridos desde el estallido.
KF = [FB, FB + 10, 150, F1 + 10]; KT = [0.0, 0.20, 0.353, 0.40]
def ts(f):
    if f <= FB: return 0.0
    for i in range(len(KF) - 1):
        if f <= KF[i + 1]:
            u = (f - KF[i]) / (KF[i + 1] - KF[i])
            if i == 0: return KT[0] + (KT[1] - KT[0]) * (1 - (1 - u) ** 1.6)          # arranque rapido que frena
            return KT[i] + (KT[i + 1] - KT[i]) * u
    return KT[-1]
def dts(f): return max(ts(f + 0.5) - ts(f - 0.5), 1e-5)

# ------------------------------------------------------------------ nodos
def N(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items(): setattr(n, k, v)
    return n
def M(nt, op, a, b=None, c=None):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op
    for i, x in enumerate((a, b, c)):
        if x is None: continue
        if isinstance(x, (int, float)): n.inputs[i].default_value = x
        else: nt.links.new(x, n.inputs[i])
    return n.outputs[0]
def smooth(nt, x, e0, e1):
    n = nt.nodes.new('ShaderNodeMapRange'); n.interpolation_type = 'SMOOTHSTEP'; n.inputs['From Min'].default_value = e0; n.inputs['From Max'].default_value = e1
    nt.links.new(x, n.inputs['Value']); return n.outputs[0]
def mix(nt, fac, a, b, blend='MIX'):
    n = nt.nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'; n.blend_type = blend; n.clamp_result = True
    if isinstance(fac, (int, float)): n.inputs[0].default_value = fac
    else: nt.links.new(fac, n.inputs[0])
    for idx, x in ((6, a), (7, b)):
        if isinstance(x, tuple): n.inputs[idx].default_value = (*x, 1) if len(x) == 3 else x
        else: nt.links.new(x, n.inputs[idx])
    return n.outputs[2]
def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; return m, m.node_tree, m.node_tree.nodes['Principled BSDF']
def obj(name, me, mat=None, coll=None):
    o = bpy.data.objects.new(name, me); (coll or sc.collection).objects.link(o)
    if mat: me.materials.append(mat)
    return o

# ------------------------------------------------------------------ cielo de hora azul: azul noche arriba, horizonte mas claro, estrellas finas
w = bpy.data.worlds.new('cielo'); sc.world = w; w.use_nodes = True; wn = w.node_tree; wn.nodes.clear()
wo = N(wn, 'ShaderNodeOutputWorld'); bg = N(wn, 'ShaderNodeBackground'); wn.links.new(bg.outputs[0], wo.inputs[0])
tc = N(wn, 'ShaderNodeTexCoord'); sp = N(wn, 'ShaderNodeSeparateXYZ'); wn.links.new(tc.outputs['Generated'], sp.inputs[0])
vz = sp.outputs[2]; vx = sp.outputs[0]
sky = mix(wn, smooth(wn, vz, 0.0, 0.10), lin((92, 122, 168)), lin((40, 66, 118)))         # horizonte -> azul medio
sky = mix(wn, smooth(wn, vz, 0.08, 0.55), sky, lin((8, 16, 42)))                          # -> azul noche
glow = M(wn, 'MULTIPLY', smooth(wn, vz, 0.10, 0.0), smooth(wn, vx, 0.2, 0.9))              # resto de luz calida al costado
sky = mix(wn, M(wn, 'MULTIPLY', glow, 0.35), sky, lin((190, 140, 130)))
st = N(wn, 'ShaderNodeTexVoronoi'); st.inputs['Scale'].default_value = 420.0; wn.links.new(tc.outputs['Generated'], st.inputs['Vector'])
star = M(wn, 'MULTIPLY', smooth(wn, st.outputs['Distance'], 0.045, 0.0), M(wn, 'MULTIPLY', smooth(wn, vz, 0.15, 0.5), 3.0))
wn.links.new(mix(wn, M(wn, 'MINIMUM', star, 1.0), sky, (1.0, 1.0, 1.0)), bg.inputs['Color']); bg.inputs['Strength'].default_value = 1.0

# ------------------------------------------------------------------ hielo: losa de 0,1 de espesor hasta el horizonte, con nieve, grietas y agujero
m_ice, nt, bs = new_mat('hielo')
tco = N(nt, 'ShaderNodeTexCoord'); ss = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(tco.outputs['Object'], ss.inputs[0])
X, Y = ss.outputs[0], ss.outputs[1]
R = M(nt, 'SQRT', M(nt, 'ADD', M(nt, 'MULTIPLY', X, X), M(nt, 'MULTIPLY', Y, Y)))
ANG = M(nt, 'ARCTAN2', Y, X)
n1 = N(nt, 'ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.35; n1.inputs['Detail'].default_value = 8.0; nt.links.new(tco.outputs['Object'], n1.inputs['Vector'])
n2 = N(nt, 'ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 6.0; n2.inputs['Detail'].default_value = 10.0; nt.links.new(tco.outputs['Object'], n2.inputs['Vector'])
snow = smooth(nt, M(nt, 'ADD', n1.outputs['Fac'], M(nt, 'MULTIPLY', n2.outputs['Fac'], 0.25)), 0.64, 0.80)   # parches de nieve soplada
ice_c = mix(nt, n2.outputs['Fac'], lin((22, 40, 60)), lin((74, 104, 130)))                # hielo negro-azulado con vetas
col = mix(nt, snow, ice_c, lin((214, 224, 236)))
# grietas de presion grandes y viejas (blanquecinas) por todo el estanque
vo = N(nt, 'ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 0.22
wv = N(nt, 'ShaderNodeVectorMath'); wv.operation = 'ADD'; nt.links.new(tco.outputs['Object'], wv.inputs[0]); nt.links.new(n1.outputs['Color'], wv.inputs[1])
nt.links.new(wv.outputs[0], vo.inputs['Vector'])
old = M(nt, 'MULTIPLY', smooth(nt, vo.outputs['Distance'], 0.02, 0.0), 0.55)
col = mix(nt, old, col, lin((200, 214, 228)))
# grietas nuevas radiales desde el agujero: crecen con el valor animado "radio_grietas"
rv = N(nt, 'ShaderNodeValue'); rv.name = 'radio_grietas'; rv.outputs[0].default_value = 0.0
pol = N(nt, 'ShaderNodeCombineXYZ'); nt.links.new(M(nt, 'MULTIPLY', ANG, 2.2), pol.inputs[0]); nt.links.new(M(nt, 'MULTIPLY', M(nt, 'LOGARITHM', M(nt, 'ADD', R, 0.05), 2.718), 2.6), pol.inputs[1])
pw = N(nt, 'ShaderNodeVectorMath'); pw.operation = 'ADD'; nt.links.new(pol.outputs[0], pw.inputs[0])
n3 = N(nt, 'ShaderNodeTexNoise'); n3.inputs['Scale'].default_value = 1.6; n3.inputs['Detail'].default_value = 4.0; nt.links.new(tco.outputs['Object'], n3.inputs['Vector'])
sc_n = N(nt, 'ShaderNodeVectorMath'); sc_n.operation = 'SCALE'; nt.links.new(n3.outputs['Color'], sc_n.inputs[0]); sc_n.inputs['Scale'].default_value = 0.6
nt.links.new(sc_n.outputs[0], pw.inputs[1])
vr = N(nt, 'ShaderNodeTexVoronoi'); vr.feature = 'DISTANCE_TO_EDGE'; vr.inputs['Scale'].default_value = 2.0; nt.links.new(pw.outputs[0], vr.inputs['Vector'])
crack_w = M(nt, 'MULTIPLY', 0.010, M(nt, 'ADD', 1.0, M(nt, 'MULTIPLY', R, -0.25)))
crack = smooth(nt, M(nt, 'SUBTRACT', vr.outputs['Distance'], crack_w), 0.0, -0.004)
crack = M(nt, 'MAXIMUM', crack, M(nt, 'MULTIPLY', smooth(nt, M(nt, 'SUBTRACT', vr.outputs['Distance'], M(nt, 'MULTIPLY', crack_w, 4.0)), 0.0, -0.01), 0.35))
crack = M(nt, 'MULTIPLY', crack, smooth(nt, M(nt, 'SUBTRACT', R, rv.outputs[0]), 0.0, -0.25))
col = mix(nt, crack, col, lin((236, 244, 250)))
nt.links.new(col, bs.inputs['Base Color'])
rough = M(nt, 'ADD', M(nt, 'MULTIPLY', snow, 0.55), M(nt, 'MULTIPLY', n2.outputs['Fac'], 0.10))
nt.links.new(M(nt, 'ADD', rough, 0.03), bs.inputs['Roughness'])
bs.inputs['Coat Weight'].default_value = 0.6; bs.inputs['Coat Roughness'].default_value = 0.03
bump = N(nt, 'ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25; bump.inputs['Distance'].default_value = 0.01
nt.links.new(M(nt, 'ADD', M(nt, 'MULTIPLY', n2.outputs['Fac'], 0.4), M(nt, 'MULTIPLY', crack, -0.6)), bump.inputs['Height']); nt.links.new(bump.outputs[0], bs.inputs['Normal'])
me = bpy.data.meshes.new('hielo'); bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=120, y_segments=120, size=2200.0); bm.to_mesh(me); bm.free()
ice = obj('HIELO', me, m_ice)
so = ice.modifiers.new('espesor', 'SOLIDIFY'); so.thickness = 0.10; so.offset = -1
# agujero irregular (se activa al estallar)
me = bpy.data.meshes.new('corte'); bm = bmesh.new(); NV = 22; ring_b, ring_t = [], []
for i in range(NV):
    a = 2 * math.pi * i / NV + rng.uniform(-0.08, 0.08); r = rng.uniform(0.52, 0.80)
    ring_b.append(bm.verts.new((r * math.cos(a), r * math.sin(a), -0.5))); ring_t.append(bm.verts.new((r * math.cos(a), r * math.sin(a), 0.5)))
for i in range(NV):
    j = (i + 1) % NV; bm.faces.new((ring_b[i], ring_b[j], ring_t[j], ring_t[i]))
bm.faces.new(list(reversed(ring_b))); bm.faces.new(ring_t); bm.to_mesh(me); bm.free()
cutter = obj('HIELO_corte', me); cutter.hide_render = True; cutter.display_type = 'WIRE'
bo = ice.modifiers.new('agujero', 'BOOLEAN'); bo.object = cutter; bo.operation = 'DIFFERENCE'; bo.solver = 'EXACT'
for f, on in ((FB - 1, False), (FB, True)):
    bo.show_render = on; bo.show_viewport = on; bo.keyframe_insert('show_render', frame=f); bo.keyframe_insert('show_viewport', frame=f)
for f, r in ((1, 0.0), (18, 0.0), (30, 0.55), (42, 0.9), (54, 1.8), (FB, 2.6), (90, 3.6), (F1, 3.9)):
    rv.outputs[0].default_value = r; rv.outputs[0].keyframe_insert('default_value', frame=f)

# ------------------------------------------------------------------ agua oscura dentro del agujero, con ondas que se abren
m_w, nt, bs = new_mat('agua'); bs.inputs['Base Color'].default_value = (*lin((6, 14, 22)), 1); bs.inputs['Roughness'].default_value = 0.02
bs.inputs['Specular IOR Level'].default_value = 0.6; bs.inputs['Coat Weight'].default_value = 1.0; bs.inputs['Coat Roughness'].default_value = 0.0
tco = N(nt, 'ShaderNodeTexCoord'); wave = N(nt, 'ShaderNodeTexWave'); wave.wave_type = 'RINGS'; wave.inputs['Scale'].default_value = 3.0
wave.inputs['Distortion'].default_value = 2.0; nt.links.new(tco.outputs['Object'], wave.inputs['Vector'])
wph = wave.inputs['Phase Offset']
for f, p in ((FB, 0.0), (F1, -18.0)): wph.default_value = p; wph.keyframe_insert('default_value', frame=f)
bump = N(nt, 'ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; nt.links.new(wave.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs[0], bs.inputs['Normal'])
me = bpy.data.meshes.new('agua'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=1.3); bm.to_mesh(me); bm.free()
water = obj('AGUA', me, m_w); water.location.z = -0.04

# ------------------------------------------------------------------ trucha: rig girado (cabeza arriba), sube del agua en camara lenta
rig = bpy.data.objects['TRUCHA_rig']; body = bpy.data.objects['TRUCHA_cuerpo']
names = ['Head'] + [f'Spine{i}' for i in range(1, 9)]
Z0, ZAP = -1.15, 1.30                                                              # centro del pez: bajo el hielo -> apice
V0 = math.sqrt(2 * G * (ZAP - Z0)); TAP = V0 / G                                    # TAP debe coincidir con KT del apice (0,353)
for f in range(F0, F1 + 1):
    t = ts(f); zc = Z0 + V0 * t - 0.5 * G * t * t if f > FB else Z0
    k = min(1.0, t / TAP)
    rig.location = (0.0, 0.0, zc)
    rig.rotation_euler = (-math.pi / 2 + 0.10 * k, 0.06 * math.sin(2.0 * t * 9), -math.pi / 2 + math.radians(22) - 0.10 * k)
    rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f)
    amp = 0.20 * (1 - 0.55 * k) if f > FB - 8 else 0.05                               # coletazo fuerte al salir, se calma arriba
    for i, n in enumerate(names[1:], 1):
        pb = rig.pose.bones[n]; s = i / 8.0
        lat = amp * (0.15 + 0.85 * s * s) * math.sin(2 * math.pi * (4.5 * t + 0.35 * i) - 0.3)
        arch = -0.07 * k * math.sin(math.pi * s)                                    # se arquea en el aire
        pb.rotation_euler = (arch, 0.0, lat); pb.keyframe_insert('rotation_euler', frame=f)
    jaw = rig.pose.bones['Jaw']; jaw.rotation_mode = 'XYZ'; jaw.rotation_euler = (0.18 * k, 0, 0); jaw.keyframe_insert('rotation_euler', frame=f)
for fc in (rig.animation_data.action.fcurves):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'

# ------------------------------------------------------------------ esquirlas de hielo: losas rotas que salen volando y caen sobre el hielo
m_sh, nt, bs = new_mat('hielo_roto')
bs.inputs['Base Color'].default_value = (*lin((222, 236, 246)), 1); bs.inputs['Roughness'].default_value = 0.12
bs.inputs['Transmission Weight'].default_value = 0.6; bs.inputs['IOR'].default_value = 1.31; bs.inputs['Coat Weight'].default_value = 0.5
n4 = N(nt, 'ShaderNodeTexNoise'); n4.inputs['Scale'].default_value = 18.0; nt.links.new(M(nt, 'MULTIPLY', n4.outputs['Fac'], 0.2), bs.inputs['Roughness'])
if hasattr(m_sh, 'use_raytrace_refraction'): m_sh.use_raytrace_refraction = True
shards = []
for k in range(34):
    a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(0.15, 0.72); size = rng.uniform(0.05, 0.17) * (1.2 if r0 > 0.5 else 1.0)
    th = rng.uniform(0.025, 0.055)
    me = bpy.data.meshes.new(f'esquirla{k}'); bm = bmesh.new()
    pts = [Vector((rng.uniform(-1, 1) * size, rng.uniform(-0.6, 0.6) * size, z)) for _ in range(7) for z in (-th / 2, th / 2)]
    for p in pts: bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts); bm.to_mesh(me); bm.free()
    o = obj(f'HIELO_esquirla_{k:02d}', me, m_sh); o.rotation_mode = 'XYZ'
    p = Vector((r0 * math.cos(a), r0 * math.sin(a), -th / 2))
    out = Vector((math.cos(a), math.sin(a), 0))
    v = out * rng.uniform(1.5, 7.0) * (0.6 + r0) + Vector((0, 0, rng.uniform(4.0, 13.0) * (1.25 - r0)))
    wv_ = Vector((rng.uniform(-14, 14), rng.uniform(-14, 14), rng.uniform(-5, 5)))
    rot = Vector((rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), a))
    t_prev = 0.0; landed = False; sunk = False
    for f in range(F0, F1 + 1):
        t = ts(f); dt = t - t_prev; t_prev = t
        if f > FB and not landed and dt > 0:
            nsub = 4
            for _ in range(nsub):
                h = dt / nsub; v.z -= G * h; p += v * h; rot += wv_ * h
                rr = math.hypot(p.x, p.y)
                if p.z < th / 2 and v.z < 0:
                    if rr > 0.75:                                                    # cae sobre el hielo: rebota poco y se queda
                        p.z = th / 2; v.z *= -0.18; v.x *= 0.55; v.y *= 0.55; wv_ *= 0.4
                        if abs(v.z) < 0.8: landed = True; v = Vector(); rot.x = rot.y = 0.0
                    elif p.z < -0.3: sunk = True                                     # al agua
        o.location = p; o.rotation_euler = rot
        o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
        o.hide_render = (f < FB) or sunk; o.keyframe_insert('hide_render', frame=f)
        o.hide_viewport = o.hide_render; o.keyframe_insert('hide_viewport', frame=f)
    shards.append(o)

# ------------------------------------------------------------------ agua: gotas del estallido, corona de agua y gotas que chorrean del pez
m_d, nt, bs = new_mat('gota')
bs.inputs['Base Color'].default_value = (1, 1, 1, 1); bs.inputs['Roughness'].default_value = 0.0
bs.inputs['Transmission Weight'].default_value = 1.0; bs.inputs['IOR'].default_value = 1.333
if hasattr(m_d, 'use_raytrace_refraction'): m_d.use_raytrace_refraction = True
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0); drop = bpy.context.object; drop.name = 'GOTA'; drop.data.materials.append(m_d)
for p in drop.data.polygons: p.use_smooth = True
drop.location = (0, 0, -50); drop.hide_render = True
def emitter(name, verts, normals):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], [])
    o = obj(name, me); o.hide_render = True; return o
ring = []
for i in range(96):
    a = 2 * math.pi * i / 96; r = rng.uniform(0.25, 0.65); ring.append((r * math.cos(a), r * math.sin(a), 0.0))
em = emitter('AGUA_estallido', ring, None)
def particles(o, name, count, f0, f1, vel, rand, size, sizer, life):
    md = o.modifiers.new(name, 'PARTICLE_SYSTEM'); ps = md.particle_system.settings
    ps.count = count; ps.frame_start = f0; ps.frame_end = f1; ps.lifetime = life
    ps.emit_from = 'VERT' if o.type == 'MESH' and not o.data.polygons else 'FACE'
    ps.normal_factor = 0.0; ps.object_align_factor = vel; ps.factor_random = rand
    ps.render_type = 'OBJECT'; ps.instance_object = drop; ps.particle_size = size; ps.size_random = sizer
    ps.use_rotations = False; ps.physics_type = 'NEWTON'
    return md.particle_system, ps
ps1, s1 = particles(em, 'estallido', 4200, FB, FB + 20, (0, 0, 9.0), 4.0, 0.012, 0.9, 400)
s1.tangent_factor = 0.0; s1.object_factor = 0.0
s1.normal_factor = 0.0
col_ = ice.modifiers.new('choque', 'COLLISION'); ice.collision.damping = 0.8; ice.collision.friction_factor = 0.6
ps2, s2 = particles(body, 'chorreo', 700, FB + 4, F1, (0, 0, 0.0), 0.15, 0.010, 0.7, 400)
s2.emit_from = 'FACE'; s2.normal_factor = 0.4
for ps in (s1, s2):
    for f in range(F0, F1 + 1):                                                     # misma camara lenta que el pez
        ps.timestep = dts(f) if f > FB else 0.04; ps.keyframe_insert('timestep', frame=f)
# corona de agua: lamina cilindrica que se abre alrededor del pez, con borde roto
m_cr, nt, bs = new_mat('corona')
bs.inputs['Base Color'].default_value = (*lin((210, 228, 240)), 1); bs.inputs['Roughness'].default_value = 0.02
bs.inputs['Transmission Weight'].default_value = 0.9; bs.inputs['IOR'].default_value = 1.333
if hasattr(m_cr, 'use_raytrace_refraction'): m_cr.use_raytrace_refraction = True
gco = N(nt, 'ShaderNodeTexCoord'); gs = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(gco.outputs['Generated'], gs.inputs[0])
nz = N(nt, 'ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9.0; nz.inputs['Detail'].default_value = 6.0; nt.links.new(gco.outputs['Object'], nz.inputs['Vector'])
alpha = smooth(nt, M(nt, 'ADD', gs.outputs[2], M(nt, 'MULTIPLY', nz.outputs['Fac'], 0.55)), 1.15, 0.85)
foam = smooth(nt, nz.outputs['Fac'], 0.55, 0.75)
nt.links.new(mix(nt, foam, lin((210, 228, 240)), lin((246, 250, 252))), bs.inputs['Base Color'])
nt.links.new(alpha, bs.inputs['Alpha'])
m_cr.surface_render_method = 'BLENDED'
me = bpy.data.meshes.new('corona'); bm = bmesh.new(); NC, NZc = 72, 14; rows = []
for j in range(NZc + 1):
    v = j / NZc; row = []
    for i in range(NC):
        a = 2 * math.pi * i / NC; r = 1.0 + 0.55 * v * v + 0.05 * math.sin(7 * a + 2 * v)
        row.append(bm.verts.new((r * math.cos(a), r * math.sin(a), v)))
    rows.append(row)
for j in range(NZc):
    for i in range(NC): bm.faces.new((rows[j][i], rows[j][(i + 1) % NC], rows[j + 1][(i + 1) % NC], rows[j + 1][i]))
bm.to_mesh(me); bm.free()
crown = obj('AGUA_corona', me, m_cr); crown.hide_viewport = True   # se descarto: se veia como una caja; el estallido lo hacen las gotas
for p in crown.data.polygons: p.use_smooth = True
crown.modifiers.new('grosor', 'SOLIDIFY').thickness = 0.01
d = crown.modifiers.new('rotura', 'DISPLACE'); tx = bpy.data.textures.new('rotura', 'CLOUDS'); tx.noise_scale = 0.25; d.texture = tx; d.strength = 0.08
for f in range(F0, F1 + 1):
    t = ts(f); u = min(1.0, t / 0.30)
    rad = 0.30 + 0.75 * (1 - (1 - u) ** 2); hgt = 1.10 * math.sin(math.pi * min(1.0, t / 0.40)) ** 0.8 if f > FB else 0.0
    crown.scale = (rad, rad, max(hgt, 0.001)); crown.keyframe_insert('scale', frame=f)
    crown.hide_render = True

# ------------------------------------------------------------------ fondo: bosque bajo y oscuro, granja blanca con una ventana encendida, niebla baja
m_tr, nt, bs = new_mat('bosque'); bs.inputs['Base Color'].default_value = (*lin((14, 22, 32)), 1); bs.inputs['Roughness'].default_value = 0.9
me = bpy.data.meshes.new('bosque'); bm = bmesh.new()
def tree(cx, cy, h, kind):
    if kind == 0:                                                                   # abeto
        for k in range(4):
            z0 = h * (0.18 + 0.2 * k); rr = h * 0.22 * (1 - 0.22 * k)
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=rr, radius2=0.0, depth=h * 0.45,
                                  matrix=Matrix.Translation((cx, cy, z0 + h * 0.22)))
    else:                                                                           # haya / roble pelado: copa irregular
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=h * 0.04, radius2=h * 0.02, depth=h * 0.6, matrix=Matrix.Translation((cx, cy, h * 0.3)))
        for k in range(5):
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=h * rng.uniform(0.14, 0.24),
                                       matrix=Matrix.Translation((cx + rng.uniform(-0.2, 0.2) * h, cy + rng.uniform(-0.1, 0.1) * h, h * rng.uniform(0.55, 0.85))))
for i in range(900):
    a = math.radians(rng.uniform(-10, 190)); r = rng.uniform(720, 860)
    tree(r * math.cos(a), r * math.sin(a) + 60, rng.uniform(30, 64) * (1.3 if rng.random() < 0.3 else 1.0), 0 if rng.random() < 0.6 else 1)
bm.to_mesh(me); bm.free(); forest = obj('FONDO_bosque', me, m_tr)
# granja: casa blanca de muros encalados y techo oscuro, con ventana calida
m_wall, nt, bs = new_mat('muro'); bs.inputs['Base Color'].default_value = (*lin((150, 156, 168)), 1); bs.inputs['Roughness'].default_value = 0.8
m_roof, nt, bs = new_mat('techo'); bs.inputs['Base Color'].default_value = (*lin((26, 26, 30)), 1)
m_win, nt, bs = new_mat('ventana'); bs.inputs['Emission Color'].default_value = (*lin((255, 176, 92)), 1); bs.inputs['Emission Strength'].default_value = 6.0
HX, HY = -230.0, 690.0
def box(name, c, s, mat):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = obj(name, me, mat); o.location = c; o.scale = s; return o
box('FONDO_casa', (HX, HY, 7), (38, 12, 14), m_wall)
me = bpy.data.meshes.new('techo'); bm = bmesh.new()
vs = [bm.verts.new(p) for p in ((-20, -7.5, 0), (20, -7.5, 0), (20, 7.5, 0), (-20, 7.5, 0), (-20, 0, 10), (20, 0, 10))]
for fz in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)): bm.faces.new([vs[i] for i in fz])
bm.to_mesh(me); bm.free(); roof = obj('FONDO_techo', me, m_roof); roof.location = (HX, HY, 14)
for wx in (-9, 4): box(f'FONDO_ventana{wx}', (HX + wx, HY - 6.05, 6), (3, 0.2, 3.4), m_win)
box('FONDO_granero', (HX + 48, HY + 8, 9), (34, 16, 18), m_roof)
# niebla baja: carteles con ruido delante del bosque
m_fog, nt, bs = new_mat('niebla'); bs.inputs['Base Color'].default_value = (*lin((96, 120, 160)), 1); bs.inputs['Roughness'].default_value = 1.0
bs.inputs['Emission Color'].default_value = (*lin((70, 96, 140)), 1); bs.inputs['Emission Strength'].default_value = 0.6
gco = N(nt, 'ShaderNodeTexCoord'); gs = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(gco.outputs['Generated'], gs.inputs[0])
nf = N(nt, 'ShaderNodeTexNoise'); nf.inputs['Scale'].default_value = 3.0; nf.inputs['Detail'].default_value = 4.0; nt.links.new(gco.outputs['Generated'], nf.inputs['Vector'])
fa = M(nt, 'MULTIPLY', M(nt, 'MULTIPLY', smooth(nt, gs.outputs[2], 1.0, 0.0), smooth(nt, gs.outputs[2], 0.0, 0.15)), M(nt, 'MULTIPLY', smooth(nt, nf.outputs['Fac'], 0.35, 0.7), 0.45))
nt.links.new(fa, bs.inputs['Alpha']); m_fog.surface_render_method = 'BLENDED'
for k, (r, hh) in enumerate(((420, 10), (560, 16), (690, 22))):
    me = bpy.data.meshes.new(f'niebla{k}'); bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0); bm.to_mesh(me); bm.free()
    o = obj(f'FONDO_niebla_{k}', me, m_fog); o.location = (0, r, hh * 0.35); o.rotation_euler = (math.pi / 2, 0, 0); o.scale = (r * 1.6, hh * 0.5, 1)

# ------------------------------------------------------------------ luz: llave calida dorada desde adelante, contraluz frio, cielo de relleno
def area(name, loc, target, energy, color, size):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.color = color; l.size = size; l.shape = 'DISK'
    o = obj(name, l); o.location = loc; d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return o
k_ = bpy.data.lights.new('LUZ_llave_dorada', 'SPOT'); k_.energy = 2400; k_.color = lin((255, 172, 84)); k_.spot_size = math.radians(24); k_.spot_blend = 0.6; k_.shadow_soft_size = 0.6
ko = obj('LUZ_llave_dorada', k_); ko.location = (-3.6, -4.6, 3.4); ko.rotation_euler = (Vector((0, 0, 1.3)) - ko.location).to_track_quat('-Z', 'Y').to_euler()
area('LUZ_contra_fria', (1.5, 5.5, 3.2), (0, 0, 1.0), 3200, lin((150, 190, 255)), 2.0)
area('LUZ_relleno', (4.0, -3.0, 3.0), (0, 0, 1.0), 220, lin((120, 150, 220)), 4.0)
sun = bpy.data.lights.new('LUZ_cielo', 'SUN'); sun.energy = 0.35; sun.color = lin((150, 175, 230)); so_ = obj('LUZ_cielo', sun); so_.rotation_euler = (math.radians(60), 0, math.radians(200))

# ------------------------------------------------------------------ camara: baja, casi a ras del hielo, empuje lento
cam = obj('CAMARA', bpy.data.cameras.new('CAMARA')); sc.camera = cam; cam.data.lens = 50; cam.data.clip_end = 5000
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 8.0
tgt = obj('CAMARA_mira', None); tgt.empty_display_size = 0.2
cam.data.dof.focus_object = tgt
tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
for f, cl, tl in ((F0, (0.6, -8.4, 0.32), (0, 0, 0.55)), (FB, (0.45, -7.6, 0.34), (0, 0, 0.75)), (150, (0.3, -6.9, 0.40), (0, 0, 1.25)), (F1, (0.25, -6.7, 0.42), (0, 0, 1.30))):
    cam.location = cl; tgt.location = tl; cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f)

# ------------------------------------------------------------------ render
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1350, 100
sc.render.engine = 'BLENDER_EEVEE_NEXT'
ee = sc.eevee
for k, v in (('taa_render_samples', 96), ('use_raytracing', True), ('use_shadows', True), ('use_volumetric_shadows', True)):
    if hasattr(ee, k): setattr(ee, k, v)
try: ee.ray_tracing_options.resolution_scale = '1'
except Exception: pass
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.35
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except TypeError: pass
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = '//render/btw_'
# cycles listo por si se renderiza en una granja con GPU
sc.cycles.samples = 256; sc.cycles.use_denoising = True
bpy.ops.ptcache.bake_all(bake=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print('ESCENA_OK', OUT, 'apice t', round(TAP, 3))
