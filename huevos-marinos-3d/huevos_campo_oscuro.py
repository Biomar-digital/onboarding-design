# Huevos marinos bajo lupa con luz de campo oscuro (recrea la foto de 8 huevos sobre placa negra con aro de luz).
# Cada huevo: corion (esfera exterior, linea brillante fina) + vitelo (esfera interior algo descentrada, su contorno
# forma la segunda linea: "dos separaciones"), volumen esferico con brillo lateral, embrion casi recto con cabeza
# bulbosa granulada, racimos de perlitas brillantes y motas. Fondo: placa negra, velo gris a la izquierda, aro lila.
# blender -b --factory-startup -P huevos_campo_oscuro.py -- OUT.png [muestras] [ancho] [frame]
import bpy, bmesh, math, random, sys, os, mathutils
args = sys.argv[sys.argv.index('--') + 1:]; OUT = args[0]
SPP = int(args[1]) if len(args) > 1 else 48; RW = int(args[2]) if len(args) > 2 else 1000
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; random.seed(4)
PX = 100.0; IW, IH = 2000, 1500                               # foto de referencia 2000x1500
def P(x, y, z=0.0): return mathutils.Vector(((x - IW / 2) / PX, -(y - IH / 2) / PX, z))
LDIR = mathutils.Vector((-0.6, 0.55, 0.3)).normalized()       # de donde "llega" el brillo (arriba-izquierda)
def sphere(name, r, loc, seg=48):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc; return o
def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; N.remove(N['Principled BSDF']); return m, N, m.node_tree.links
class G:                                                      # ayuda para armar nodos matematicos
    def __init__(s, N, Lk): s.N, s.Lk = N, Lk
    def m(s, op, a, b=None, c=None):
        n = s.N.new('ShaderNodeMath'); n.operation = op
        for i, x in enumerate((a, b, c)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: s.Lk.new(x, n.inputs[i])
        return n.outputs[0]
    def rng(s, x, a, b, c=0.0, d=1.0, smooth=True):
        n = s.N.new('ShaderNodeMapRange'); s.Lk.new(x, n.inputs[0]); n.inputs[1].default_value = a; n.inputs[2].default_value = b
        n.inputs[3].default_value = c; n.inputs[4].default_value = d
        if smooth: n.interpolation_type = 'SMOOTHSTEP'
        return n.outputs[0]
    def facing(s, blend=0.5):
        n = s.N.new('ShaderNodeLayerWeight'); n.inputs['Blend'].default_value = blend; return n.outputs['Facing']
    def lit(s):                                               # cuanto mira la normal hacia LDIR (0..1)
        g = s.N.new('ShaderNodeNewGeometry'); v = s.N.new('ShaderNodeVectorMath'); v.operation = 'DOT_PRODUCT'
        s.Lk.new(g.outputs['Normal'], v.inputs[0]); v.inputs[1].default_value = LDIR; return s.m('MAXIMUM', v.outputs['Value'], 0.0)
    def glow(s, strength, col=(1, 1, 1), trans=(1, 1, 1), ior=None, back=None):
        e = s.N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*col, 1); s.Lk.new(strength, e.inputs['Strength'])
        if ior: t = s.N.new('ShaderNodeBsdfRefraction'); t.inputs['IOR'].default_value = ior; t.inputs['Roughness'].default_value = 0.0; t.inputs['Color'].default_value = (*trans, 1)
        else: t = s.N.new('ShaderNodeBsdfTransparent'); t.inputs['Color'].default_value = (*trans, 1)
        if back is not None and back < 0.999:                # cara trasera (al salir del huevo): atenua lo que hay detras, no lo de adentro
            gb = s.N.new('ShaderNodeNewGeometry'); mc = s.N.new('ShaderNodeMix'); mc.data_type = 'RGBA'; s.Lk.new(gb.outputs['Backfacing'], mc.inputs['Factor'])
            mc.inputs[6].default_value = (*trans, 1); mc.inputs[7].default_value = (back, back, back, 1); s.Lk.new(mc.outputs[2], t.inputs['Color'])
        a = s.N.new('ShaderNodeAddShader'); s.Lk.new(t.outputs[0], a.inputs[0]); s.Lk.new(e.outputs[0], a.inputs[1])
        s.Lk.new(a.outputs[0], s.N['Material Output'].inputs['Surface'])
K = lambda k, d: float(os.environ.get(k, d))
# ---- corion: linea fina brillante en el borde + velo suave + brillo del lado iluminado (se lee esferico)
chor, N, Lk = mat('chorion'); g = G(N, Lk); f = g.facing()
line = g.rng(f, 0.93, 0.995)
sheen = g.m('MULTIPLY', g.rng(f, 0.45, 0.97, 0.0, 1.0), g.m('ADD', 0.25, g.m('MULTIPLY', g.lit(), 1.2)))
g.glow(g.m('ADD', g.m('MULTIPLY', line, K('LINE', '1.5')), g.m('MULTIPLY', sheen, K('SHEEN', '0.16'))), (0.97, 0.95, 0.9), (1, 1, 1), K('CIOR', '1.04'), K('CT', '1'))
# ---- vitelo: segunda linea interior, mas tenue, y un velo lechoso apenas visible
yolk, N, Lk = mat('yolk'); g = G(N, Lk); f = g.facing()
g.glow(g.m('ADD', g.m('MULTIPLY', g.rng(f, 0.9, 0.99), K('YLINE', '0.45')), g.m('MULTIPLY', g.rng(f, 0.3, 0.9), 0.03)), (0.9, 0.9, 0.88), (0.97, 0.97, 0.97), None, K('YT', '1'))
# ---- perlitas (granulos/gotitas de lipido): borde brillante, centro oscuro, punto de brillo del lado de la luz
pearl, N, Lk = mat('pearl'); g = G(N, Lk); f = g.facing(0.4)
spec = g.m('POWER', g.lit(), 6.0)
g.glow(g.m('ADD', g.m('ADD', g.rng(f, 0.4, 0.95, 0.18, K('PEARL', '1.25')), g.m('MULTIPLY', spec, 1.6)), 0.0), (1.0, 0.96, 0.88), (0.55, 0.55, 0.55))
# ---- embrion: tejido translucido, contorno luminoso suave, relleno lechoso con grano fino
emb, N, Lk = mat('embryo'); g = G(N, Lk); f = g.facing()
tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9; nz.inputs['Detail'].default_value = 5; Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
fine = N.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value = 90; fine.inputs['Detail'].default_value = 2; Lk.new(tc.outputs['Object'], fine.inputs['Vector'])
vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 30; Lk.new(tc.outputs['Object'], vo.inputs['Vector'])
fill = g.m('ADD', g.m('ADD', g.m('MULTIPLY', g.rng(nz.outputs['Fac'], 0.4, 0.7), 0.14), g.m('MULTIPLY', fine.outputs['Fac'], 0.05)), g.m('MULTIPLY', g.rng(vo.outputs['Distance'], 0.15, 0.45, 1.0, 0.0), 0.1))
edge = g.m('MULTIPLY', g.rng(f, 0.55, 0.97), g.m('ADD', 0.45, g.m('MULTIPLY', g.lit(), 0.9)))
g.glow(g.m('ADD', g.m('MULTIPLY', edge, K('EDGE', '1.05')), fill), (0.97, 0.93, 0.85), (0.85, 0.85, 0.85))
# cabeza (vesicula): bulbo translucido granulado y con brillo de borde
head, N, Lk = mat('head'); g = G(N, Lk); f = g.facing()
tc = N.new('ShaderNodeTexCoord'); vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 26; Lk.new(tc.outputs['Object'], vo.inputs['Vector'])
gr = g.m('MULTIPLY', g.rng(vo.outputs['Distance'], 0.15, 0.45, 1.0, 0.0), 0.18)
g.glow(g.m('ADD', g.m('ADD', g.m('MULTIPLY', g.rng(f, 0.4, 0.97), g.m('ADD', 0.15, g.m('MULTIPLY', g.lit(), 0.7))), gr), 0.08), (0.97, 0.95, 0.9), (0.8, 0.8, 0.8))
# ---- disposicion trazada sobre la foto (px): huevos (cx, cy, r, z) y embriones (cabeza, cola)
EGGS = [(205, 492, 128, 0.0), (468, 355, 128, 0.05), (895, 212, 128, 0.0), (675, 508, 126, 0.08),
        (932, 518, 128, 0.0), (545, 830, 128, 0.05), (858, 800, 128, 0.0), (850, 1108, 128, -0.05)]
EMB = [((100, 525), (300, 440)), ((362, 330), (585, 345)), ((782, 215), (1010, 218)), ((718, 410), (632, 608)),
       ((832, 440), (1030, 572)), ((432, 852), (655, 800)), ((806, 690), (880, 905)), ((765, 1040), (940, 1155))]
R_ = random.Random(9)
for k, ((cx, cy, rp, z), (hd, tl)) in enumerate(zip(EGGS, EMB)):
    c = P(cx, cy, z); R = rp / PX
    sphere('chorion', R, c, 128).data.materials.append(chor)
    off = mathutils.Vector((R_.uniform(-1, 1), R_.uniform(-1, 1), 0)).normalized() * R * K('YOFF', '0.05')
    sphere('yolk', R * K('YR', '0.91'), c + off, 96).data.materials.append(yolk)
    # embrion: tubo casi recto apoyado sobre el vitelo, con leve curva, de cabeza a cola
    h = P(*hd) - P(cx, cy); t = P(*tl) - P(cx, cy)
    for v in (h, t):
        if v.length > 0.62 * R: v *= 0.62 * R / v.length
    ph1, ph2 = R_.uniform(0, 6.28), R_.uniform(0, 6.28); n = 40; side = mathutils.Vector((-(t - h).y, (t - h).x, 0)).normalized(); bend = R_.uniform(-0.12, 0.12) * R
    pts = []
    for i in range(n):
        u = i / (n - 1); q = h.lerp(t, u) + side * bend * math.sin(math.pi * u); d = q.length
        q.z = math.sqrt(max((0.86 * R) ** 2 - d * d, 0)) * 0.45; pts.append(c + q)
    cu = bpy.data.curves.new('emb', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.12 * R; cu.bevel_resolution = 6; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(n - 1)
    for i, p in enumerate(pts):
        u = i / (n - 1); sp.points[i].co = (p.x, p.y, p.z, 1); base = 0.75 + 0.25 * math.sin(math.pi * min(u * 1.2, 1)) if u < 0.85 else 0.75 - 1.6 * (u - 0.85)
        sp.points[i].radius = base * (1 + 0.14 * math.sin(u * 9.0 + ph1) + 0.08 * math.sin(u * 23.0 + ph2))   # ancho que cambia: cuerpo organico
    eo = bpy.data.objects.new('embryo', cu); sc.collection.objects.link(eo); cu.materials.append(emb); eo.scale = (1, 1, 1)
    ax0 = (pts[0] - pts[4]).normalized(); hb = sphere('headb', 0.21 * R, pts[0] + ax0 * 0.05 * R, 48); hb.rotation_mode = 'QUATERNION'; hb.rotation_quaternion = ax0.to_track_quat('X', 'Z'); hb.scale = (1.15, 1.0, 0.75)
    ax1 = (pts[-1] - pts[-5]).normalized(); tb = sphere('tailb', 0.12 * R, pts[-1] - ax1 * 0.02 * R, 32); tb.rotation_mode = 'QUATERNION'; tb.rotation_quaternion = ax1.to_track_quat('X', 'Z'); tb.scale = (1.3, 1.0, 0.7)
    bpy.ops.object.select_all(action='DESELECT'); eo.select_set(True); bpy.context.view_layer.objects.active = eo; bpy.ops.object.convert(target='MESH')
    hb.select_set(True); tb.select_set(True); bpy.ops.object.join()
    for i_, (sx_, sy_) in enumerate(((0.07, 0.0), (-0.07, 0.0))):               # copas opticas tenues dentro de la cabeza
        sd_ = ax0.cross(mathutils.Vector((0, 0, 1))).normalized(); eye = sphere('yolk', 0.055 * R, pts[0] + ax0 * 0.08 * R + sd_ * sx_ * R + mathutils.Vector((0, 0, 0.04 * R)), 24); eye.data.materials.append(yolk)
    cn = bpy.data.curves.new('noto', 'CURVE'); cn.dimensions = '3D'; cn.bevel_depth = 0.022 * R; cn.bevel_resolution = 3; spn = cn.splines.new('POLY'); spn.points.add(n - 9)
    for i in range(n - 8):
        q = pts[i + 4] + mathutils.Vector((0, 0, 0.05 * R)); spn.points[i].co = (q.x, q.y, q.z, 1)
    on_ = bpy.data.objects.new('noto', cn); sc.collection.objects.link(on_); cn.materials.append(yolk)   # notocorda: linea interior
    rmh = eo.modifiers.new('r', 'REMESH'); rmh.mode = 'VOXEL'; rmh.voxel_size = 0.012 * R; rmh.use_smooth_shade = True
    tx = bpy.data.textures.new('bump%d' % k, 'CLOUDS'); tx.noise_scale = 0.12 * R; tx.noise_depth = 3
    dm = eo.modifiers.new('d', 'DISPLACE'); dm.texture = tx; dm.strength = 0.045 * R; dm.mid_level = 0.5; dm.texture_coords = 'GLOBAL'   # borde irregular
    eo.modifiers.new('s', 'SMOOTH').iterations = 3
    # racimos de perlitas: sobre el embrion y sueltos en el vitelo (racimos tipo uva, perlas de tamano parecido)
    def cluster(cc, nn, spread, rr=(0.018, 0.027), flat=0.35):
        for _ in range(nn):
            q = cc + mathutils.Vector((R_.gauss(0, spread), R_.gauss(0, spread), R_.gauss(0, spread * flat)))
            if (q - c).length > 0.88 * R: continue
            sphere('pearl', R * R_.uniform(*rr), q, 16).data.materials.append(pearl)
    for _ in range(R_.randint(2, 3)):
        p = R_.choice(pts[4:-4]); nn = R_.randint(15, 35); cluster(p + mathutils.Vector((0, 0, 0.1 * R)), nn, 0.016 * R * math.sqrt(nn))
    for _ in range(R_.randint(4, 7)):
        a = R_.uniform(0, 6.28); r_ = R * 0.75 * math.sqrt(R_.random())
        cc = c + mathutils.Vector((r_ * math.cos(a), r_ * math.sin(a), 0)); cc.z = c.z + math.sqrt(max((0.85 * R) ** 2 - r_ * r_, 0)) * R_.uniform(-0.6, 0.6)
        nn = R_.randint(15, 45); cluster(cc, nn, 0.015 * R * math.sqrt(nn))
    for _ in range(90):                                       # motas finas
        a = R_.uniform(0, 6.28); r_ = R * 0.86 * math.sqrt(R_.random())
        q = c + mathutils.Vector((r_ * math.cos(a), r_ * math.sin(a), R_.uniform(-0.5, 0.5) * R))
        sphere('pearl', R * R_.uniform(0.005, 0.01), q, 8).data.materials.append(pearl)
# ---- placa de fondo (emisiva, fuera de foco): negra a la derecha, velo gris a la izquierda, fibras y polvo
pl = bpy.data.objects.new('plate', bpy.data.meshes.new('plate')); sc.collection.objects.link(pl)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=16); bm.to_mesh(pl.data); bm.free(); pl.location = (0, 0, -14)
pm, N, Lk = mat('plate'); g = G(N, Lk); tc = N.new('ShaderNodeTexCoord'); sx = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Object'], sx.inputs[0])
veil = g.rng(sx.outputs['X'], 4.0, -12.0, 0.0, K('VEIL', '0.11'))                  # gris a la izquierda
nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.25; Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (0.8, 0.8, 0.72, 1)
Lk.new(g.m('MULTIPLY', veil, g.m('ADD', 0.6, g.m('MULTIPLY', nz.outputs['Fac'], 0.8))), e.inputs['Strength']); Lk.new(e.outputs[0], N['Material Output'].inputs['Surface']); pl.data.materials.append(pm)
# aro de luz lila de la placa (abajo a la derecha subiendo hacia arriba a la derecha)
ring = bpy.data.objects.new('ring', bpy.data.meshes.new('ring')); sc.collection.objects.link(ring)
bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=False, segments=256, radius=1.0); bm.to_mesh(ring.data); bm.free()
ring.location = P(200, -300, -11.0); ring.scale = (18.5, 19.7, 1); ring.rotation_euler = (0, 0, 0.0)
sk = ring.modifiers.new('w', 'SKIN')
for v in ring.data.skin_vertices[0].data: v.radius = (0.035, 0.035)
ring.modifiers.new('s', 'SUBSURF').levels = 2
rm, N, Lk = mat('ring'); g = G(N, Lk); f = g.facing(0.5)
g.glow(g.m('MULTIPLY', g.rng(f, 1.0, 0.0), K('RING', '0.6')), (0.82, 0.8, 1.0))
ring.data.materials.append(rm)
fib, N, Lk = mat('fiber'); g = G(N, Lk); f = g.facing(0.5); tc = N.new('ShaderNodeTexCoord'); bn = N.new('ShaderNodeTexNoise'); bn.inputs['Scale'].default_value = 4.0; bn.inputs['Detail'].default_value = 1; Lk.new(tc.outputs['Object'], bn.inputs['Vector'])
g.glow(g.m('MULTIPLY', g.rng(f, 1.0, 0.2), g.m('ADD', 0.12, g.rng(bn.outputs['Fac'], 0.55, 0.75, 0.0, 0.6))), (0.88, 0.87, 0.82))
for (a, b_, w) in (((180, 1230), (860, -40), 0.05), ((1240, 110), (1560, 480), 0.07), ((300, 1430), (560, 1100), 0.04)):
    A = P(*a, -9.0); B = P(*b_, -9.0); cu = bpy.data.curves.new('fib', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = w * 0.8; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(7)
    for i in range(8):
        q = A.lerp(B, i / 7) + mathutils.Vector((R_.gauss(0, 0.05), R_.gauss(0, 0.05), 0)); sp.points[i].co = (q.x, q.y, q.z, 1); sp.points[i].radius = R_.uniform(0.5, 1.4)
    o = bpy.data.objects.new('fiber', cu); sc.collection.objects.link(o); cu.materials.append(fib)
dust, N, Lk = mat('dust'); g = G(N, Lk); f = g.facing(0.5); g.glow(g.m('MULTIPLY', g.rng(f, 1.0, 0.0), 0.9), (0.9, 0.9, 0.9))
for _ in range(220):
    q = P(R_.uniform(0, IW), R_.uniform(0, IH), R_.uniform(-8.0, 0.4))
    if any((q.xy - P(cx, cy).xy).length < rp / PX * 1.02 for cx, cy, rp, _ in EGGS) and q.z > -1: continue
    sphere('dust', R_.uniform(0.006, 0.02), q, 8).data.materials.append(dust)
# ---- mundo negro; camara de lupa con foco corto (lo que esta fuera del plano de los huevos se desenfoca)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.005, 0.005, 1)
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = IW / PX
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); cam.location = (0, 0, 30); sc.camera = cam
if os.environ.get('ZOOM'):                                    # ZOOM=x,y,ancho_px: acercamiento sobre la foto
    zx, zy, zw = [float(v) for v in os.environ['ZOOM'].split(',')]; q = P(zx, zy); cam.location = (q.x, q.y, 30); cd.ortho_scale = zw / PX
cd.dof.use_dof = True; cd.dof.focus_distance = 30.0; cd.dof.aperture_fstop = K('FSTOP', '0.4')
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SPP; sc.cycles.use_denoising = False
sc.cycles.max_bounces = 16; sc.cycles.transparent_max_bounces = 64
sc.render.resolution_x = RW; sc.render.resolution_y = RW * IH // IW
sc.view_settings.view_transform = 'Standard'
# compositor: halo suave de la optica (bloom) y grano leve del sensor
sc.use_nodes = True; ct = sc.node_tree; ct.nodes.clear(); rl = ct.nodes.new('CompositorNodeRLayers')
gl = ct.nodes.new('CompositorNodeGlare'); gl.glare_type = 'FOG_GLOW'; gl.quality = 'HIGH'; gl.size = 7; gl.threshold = 0.6; gl.mix = -0.6
co = ct.nodes.new('CompositorNodeComposite'); ct.links.new(rl.outputs['Image'], gl.inputs['Image']); ct.links.new(gl.outputs['Image'], co.inputs['Image'])
if os.environ.get('HIDE'):
    for o in sc.objects:
        if o.name.startswith(tuple(os.environ['HIDE'].split(','))): o.hide_render = True
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print('DONE')
