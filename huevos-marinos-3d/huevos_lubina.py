# Huevos marinos (lubina) en 3D, imitando la foto de referencia (referencia/foto_lubina.png, 1280x960).
# Huevo = esfera de vidrio (agua sobre fondo) que aumenta y oscurece el borde inferior; embrion = tubo translucido
# curvado por dentro del borde, con melanoforos negros y puntos naranjas sobre el lomo; gota de aceite amarilla.
# blender -b --factory-startup -P huevos_lubina.py -- OUT.png [muestras] [ancho]
import bpy, bmesh, math, random, sys, os, mathutils, mathutils.kdtree
args = sys.argv[sys.argv.index('--') + 1:]; OUT = args[0]
SPP = int(args[1]) if len(args) > 1 else 64; RW = int(args[2]) if len(args) > 2 else 640
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; random.seed(3)
PX = 100.0                                                   # px de la foto por unidad de escena
def P(x, y, z=0.0): return mathutils.Vector(((x - 640) / PX, -(y - 480) / PX, z))
def sphere(name, r, loc, seg=48):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc; return o
def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; return m, m.node_tree.nodes, m.node_tree.links
def MATH(N, Lk, op, a, b=None):
    n = N.new('ShaderNodeMath'); n.operation = op
    for i, x in enumerate((a, b)):
        if x is None: continue
        if isinstance(x, (int, float)): n.inputs[i].default_value = x
        else: Lk.new(x, n.inputs[i])
    return n.outputs[0]
E = float(os.environ.get('EGG_IOR', '1.25'))
# ---- huevo: vidrio liso (agua dentro del corion, sobre el fondo)
egg, N, Lk = mat('egg'); b = N['Principled BSDF']
b.inputs['Transmission Weight'].default_value = 1; b.inputs['IOR'].default_value = E; b.inputs['Roughness'].default_value = 0.0
# corion fino: el centro se ve claro y el borde vira a marron (mas oscuro abajo), como en la foto
lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
geo = N.new('ShaderNodeNewGeometry'); sxyz = N.new('ShaderNodeSeparateXYZ'); Lk.new(geo.outputs['Normal'], sxyz.inputs[0])
RIM = float(os.environ.get('RIM', '0.1'))
fr = N.new('ShaderNodeMapRange'); Lk.new(lw.outputs['Facing'], fr.inputs[0]); fr.inputs[1].default_value = RIM; fr.inputs[2].default_value = 1.0; fr.interpolation_type = 'SMOOTHSTEP'
bot = MATH(N, Lk, 'ADD', 0.7, MATH(N, Lk, 'MULTIPLY', MATH(N, Lk, 'MAXIMUM', MATH(N, Lk, 'MULTIPLY', sxyz.outputs['Y'], -1.0), 0.0), 0.8))
rc = N.new('ShaderNodeMix'); rc.data_type = 'RGBA'; Lk.new(MATH(N, Lk, 'MINIMUM', MATH(N, Lk, 'MULTIPLY', fr.outputs[0], bot), 1.0), rc.inputs['Factor'])
rc.inputs[6].default_value = (1.0, 0.995, 0.97, 1); rc.inputs[7].default_value = (0.32, 0.17, 0.04, 1)
Lk.new(rc.outputs[2], b.inputs['Base Color'])
glow = N.new('ShaderNodeEmission'); glow.inputs['Color'].default_value = (1.0, 0.98, 0.94, 1)
Lk.new(MATH(N, Lk, 'MULTIPLY', MATH(N, Lk, 'SUBTRACT', 1.0, fr.outputs[0]), float(os.environ.get('GLOW', '0.06'))), glow.inputs['Strength'])
ga = N.new('ShaderNodeAddShader'); Lk.new(b.outputs[0], ga.inputs[0]); Lk.new(glow.outputs[0], ga.inputs[1]); Lk.new(ga.outputs[0], N['Material Output'].inputs['Surface'])
# pliegues tenues del espacio perivitelino (las sombras suaves que se ven dentro de cada huevo)
fold, N, Lk = mat('fold'); b = N['Principled BSDF']
b.inputs['Transmission Weight'].default_value = 1; b.inputs['IOR'].default_value = 1.015; b.inputs['Roughness'].default_value = 0.25
b.inputs['Base Color'].default_value = (0.97, 0.96, 0.94, 1)
# ---- gota de aceite: crema amarillenta, borde oscuro fino
oil, N, Lk = mat('oil'); N.remove(N['Principled BSDF'])
em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (0.66, 0.6, 0.38, 1)
lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
sh_ = N.new('ShaderNodeMapRange'); Lk.new(lw.outputs['Facing'], sh_.inputs[0]); sh_.inputs[3].default_value = 1.05; sh_.inputs[4].default_value = 0.8
Lk.new(sh_.outputs[0], em.inputs['Strength'])                     # un poco mas clara al centro
rim = N.new('ShaderNodeMapRange'); Lk.new(lw.outputs['Facing'], rim.inputs[0]); rim.inputs[1].default_value = 0.62; rim.inputs[2].default_value = 0.74
dk = N.new('ShaderNodeBsdfTransparent'); dk.inputs['Color'].default_value = (0.12, 0.1, 0.09, 1)
mx = N.new('ShaderNodeMixShader'); Lk.new(rim.outputs[0], mx.inputs[0]); Lk.new(em.outputs[0], mx.inputs[1]); Lk.new(dk.outputs[0], mx.inputs[2])
Lk.new(mx.outputs[0], N['Material Output'].inputs['Surface'])
# ---- embrion: tejido casi transparente + pigmentos (atributo 'dors' = 1 en el lomo, hacia el borde del huevo)
emb, N, Lk = mat('embryo'); N.remove(N['Principled BSDF'])
gl = N.new('ShaderNodeBsdfPrincipled'); gl.inputs['Transmission Weight'].default_value = 1; gl.inputs['IOR'].default_value = 1.035
gl.inputs['Roughness'].default_value = 0.25; gl.inputs['Base Color'].default_value = (0.97, 0.95, 0.92, 1)
tc = N.new('ShaderNodeTexCoord'); at = N.new('ShaderNodeAttribute'); at.attribute_name = 'dors'
lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.3
edge = N.new('ShaderNodeMapRange'); Lk.new(lw.outputs['Facing'], edge.inputs[0]); edge.inputs[1].default_value = 0.45; edge.inputs[2].default_value = 0.9; edge.inputs[4].default_value = 0.8
def dots(scale, size, seed):
    v = N.new('ShaderNodeTexVoronoi'); v.inputs['Scale'].default_value = scale; v.inputs['Randomness'].default_value = 1.0
    mp = N.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (seed, seed * 1.7, seed * 0.3); Lk.new(tc.outputs['Object'], mp.inputs['Vector']); Lk.new(mp.outputs[0], v.inputs['Vector'])
    sep = N.new('ShaderNodeSeparateColor'); Lk.new(v.outputs['Color'], sep.inputs[0])
    r = MATH(N, Lk, 'MULTIPLY', size, MATH(N, Lk, 'ADD', 0.6, sep.outputs['Red']))
    d = MATH(N, Lk, 'MINIMUM', 1.0, MATH(N, Lk, 'MAXIMUM', 0.0, MATH(N, Lk, 'DIVIDE', MATH(N, Lk, 'SUBTRACT', r, v.outputs['Distance']), 0.05)))
    return d, sep.outputs['Green']
mel, mg = dots(11.0, 0.2, 0.0)                               # melanoforos: negros, densos en el lomo
mel = MATH(N, Lk, 'MULTIPLY', mel, MATH(N, Lk, 'LESS_THAN', mg, MATH(N, Lk, 'MULTIPLY', MATH(N, Lk, 'POWER', at.outputs['Fac'], 1.4), 0.9)))
ery, eg = dots(13.0, 0.19, 5.0)                              # puntos naranjas/rojizos, mas repartidos
ery = MATH(N, Lk, 'MULTIPLY', ery, MATH(N, Lk, 'LESS_THAN', eg, MATH(N, Lk, 'ADD', 0.2, MATH(N, Lk, 'MULTIPLY', at.outputs['Fac'], 0.45))))
nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 14; nz.inputs['Detail'].default_value = 6; Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
tissue = N.new('ShaderNodeMix'); tissue.data_type = 'RGBA'; Lk.new(nz.outputs['Fac'], tissue.inputs['Factor'])
tissue.inputs[6].default_value = (0.95, 0.9, 0.86, 1); tissue.inputs[7].default_value = (0.84, 0.76, 0.7, 1)
tt = N.new('ShaderNodeBsdfTransparent'); Lk.new(tissue.outputs[2], tt.inputs['Color'])
base = N.new('ShaderNodeMixShader'); base.inputs[0].default_value = 0.5; Lk.new(tt.outputs[0], base.inputs[1]); Lk.new(gl.outputs[0], base.inputs[2])
ed = N.new('ShaderNodeBsdfTransparent'); ed.inputs['Color'].default_value = (0.5, 0.42, 0.36, 1)
m1 = N.new('ShaderNodeMixShader'); Lk.new(edge.outputs[0], m1.inputs[0]); Lk.new(base.outputs[0], m1.inputs[1]); Lk.new(ed.outputs[0], m1.inputs[2])
eo_ = N.new('ShaderNodeBsdfTransparent'); eo_.inputs['Color'].default_value = (0.85, 0.3, 0.1, 1)
m2 = N.new('ShaderNodeMixShader'); Lk.new(MATH(N, Lk, 'MULTIPLY', ery, 1.0), m2.inputs[0]); Lk.new(m1.outputs[0], m2.inputs[1]); Lk.new(eo_.outputs[0], m2.inputs[2])
mo = N.new('ShaderNodeBsdfTransparent'); mo.inputs['Color'].default_value = (0.08, 0.07, 0.08, 1)
m3 = N.new('ShaderNodeMixShader'); Lk.new(MATH(N, Lk, 'MULTIPLY', mel, 0.95), m3.inputs[0]); Lk.new(m2.outputs[0], m3.inputs[1]); Lk.new(mo.outputs[0], m3.inputs[2])
Lk.new(m3.outputs[0], N['Material Output'].inputs['Surface'])
yolk, N, Lk = mat('yolk'); b = N['Principled BSDF']; b.inputs['Transmission Weight'].default_value = 1; b.inputs['IOR'].default_value = 1.02; b.inputs['Roughness'].default_value = 0.15
lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5; yr = N.new('ShaderNodeMapRange'); Lk.new(lw.outputs['Facing'], yr.inputs[0]); yr.inputs[1].default_value = 0.88; yr.inputs[2].default_value = 1.0
yc = N.new('ShaderNodeMix'); yc.data_type = 'RGBA'; Lk.new(yr.outputs[0], yc.inputs['Factor']); yc.inputs[6].default_value = (1, 0.99, 0.97, 1); yc.inputs[7].default_value = (0.95, 0.93, 0.9, 1); Lk.new(yc.outputs[2], b.inputs['Base Color'])
wisp, N, Lk = mat('wisp'); N.remove(N['Principled BSDF']); wt_ = N.new('ShaderNodeBsdfTransparent'); wt_.inputs['Color'].default_value = (0.97, 0.95, 0.93, 1)
wl = N.new('ShaderNodeLayerWeight'); wl.inputs['Blend'].default_value = 0.4; wd = N.new('ShaderNodeBsdfTransparent'); wd.inputs['Color'].default_value = (0.82, 0.76, 0.7, 1)
wm = N.new('ShaderNodeMixShader'); Lk.new(wl.outputs['Facing'], wm.inputs[0]); Lk.new(wt_.outputs[0], wm.inputs[1]); Lk.new(wd.outputs[0], wm.inputs[2]); Lk.new(wm.outputs[0], N['Material Output'].inputs['Surface'])
star, N, Lk = mat('star'); N.remove(N['Principled BSDF']); t_ = N.new('ShaderNodeBsdfTransparent'); t_.inputs['Color'].default_value = (0.1, 0.09, 0.08, 1)
Lk.new(t_.outputs[0], N['Material Output'].inputs['Surface'])
# ---- disposicion medida sobre la foto (px): huevos (cx, cy, r, z), embriones (cabeza primero), gotas (x, y, r, huevo)
EGGS = [(266, 380, 222, 0.0), (704, 263, 222, 0.15), (1020, 583, 222, 0.0), (586, 699, 227, 0.0),
        (150, 810, 225, -0.5), (915, 1018, 225, -1.6), (515, 1135, 225, -1.2)]
EMB = [[(85, 380), (110, 290), (190, 215), (290, 195), (390, 230), (455, 320), (475, 450), (440, 580)],
       [(525, 175), (548, 235), (620, 268), (720, 268), (820, 245), (905, 240)],
       [(1110, 742), (1000, 735), (900, 690), (840, 590), (850, 470)],
       [(430, 545), (520, 500), (640, 520), (740, 600), (785, 720), (750, 840), (690, 890)],
       [(15, 690), (40, 800), (110, 905)],
       [(720, 880), (820, 830), (930, 820), (1040, 850)],
       [(360, 930), (440, 912), (530, 908), (640, 930)]]
OILS = [(363, 520, 42, 0), (615, 255, 34, 1), (1025, 492, 37, 2), (488, 850, 42, 3), (250, 655, 37, 4), (298, 690, 17, 4)]
def egg_at(k):
    cx, cy, rp, z = EGGS[k]; c = P(cx, cy, z); R = rp / PX
    o = sphere('egg', R, c, 128); o.data.materials.append(egg)
    sh = o.modifiers.new('shell', 'SOLIDIFY'); sh.thickness = (0.008 if os.environ.get('LOOK') == 'dark' else 0.03) * R; sh.offset = -1
    for _ in range(int(os.environ.get('FOLDS','0'))):         # pliegues internos suaves
        f = sphere('fold', R * random.uniform(0.45, 0.6), c + mathutils.Vector((random.uniform(-.3, .3) * R, random.uniform(-.3, .3) * R, -0.35 * R)), 48)
        f.scale = (1.0, random.uniform(0.25, 0.5), 0.6); f.rotation_euler = (0, 0, random.uniform(0, 3.14)); f.data.materials.append(fold)
    y_ = sphere('yolk', 0.8 * R, c + mathutils.Vector((random.uniform(-.08, .08) * R, random.uniform(-.08, .08) * R, -0.1 * R)), 96); y_.data.materials.append(yolk)
    for _ in range(2):
        a0 = random.uniform(0, 6.28); L_ = random.uniform(0.5, 0.9); cw = bpy.data.curves.new('wisp', 'CURVE'); cw.dimensions = '3D'; cw.bevel_depth = 0.07 * R; cw.bevel_resolution = 3
        sw = cw.splines.new('POLY'); sw.points.add(9); bend = random.uniform(-0.5, 0.5)
        for j in range(10):
            u = j / 9 - 0.5; ax = mathutils.Vector((math.cos(a0), math.sin(a0), 0)); nx = mathutils.Vector((-ax.y, ax.x, 0))
            q = c + ax * u * L_ * R * 1.4 + nx * (bend * (u * u - 0.25) * R + random.uniform(-.25, .25) * R * 0) + mathutils.Vector((0, 0, -0.55 * R)); sw.points[j].co = (q.x, q.y, q.z, 1); sw.points[j].radius = math.sin((j / 9) * math.pi) + 0.1
        ow = bpy.data.objects.new('wisp', cw); sc.collection.objects.link(ow); ow.location = mathutils.Vector((random.uniform(-.2, .2) * R, random.uniform(-.2, .2) * R, 0)); ow.scale = (1, 1, 0.5); cw.materials.append(wisp)
    pts = []
    rr = 0.84 * R
    for x, y in EMB[k]:
        q = P(x, y) - P(cx, cy); d = q.length
        if d > rr: q *= rr / d; d = rr
        q.z = math.sqrt(max(rr * rr - d * d, 0)) * 0.55; pts.append(c + q)
    sm = []
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, len(pts) - 1)]
        for s in range(12):
            t = s / 12; sm.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    sm.append(pts[-1]); n = len(sm)
    cu = bpy.data.curves.new('emb', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.15 * R; cu.bevel_resolution = 6; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(n - 1)
    for i, p in enumerate(sm):
        u = i / (n - 1); sp.points[i].co = (p.x, p.y, p.z, 1)
        sp.points[i].radius = (0.3 + 0.7 * math.sin(min(u / 0.08, 1) * math.pi / 2)) if u < 0.5 else 1.0 - 0.6 * ((u - 0.5) / 0.5) ** 1.5
    eo = bpy.data.objects.new('embryo', cu); sc.collection.objects.link(eo)
    hd = sphere('head', 0.2 * R, sm[0] + (sm[0] - sm[4]).normalized() * 0.02 * R, 40)
    bpy.ops.object.select_all(action='DESELECT'); eo.select_set(True); bpy.context.view_layer.objects.active = eo; bpy.ops.object.convert(target='MESH')
    hd.select_set(True); bpy.ops.object.join()
    rm = eo.modifiers.new('weld', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = 0.012 * R; rm.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier='weld')
    # cuerpo achatado hacia el lente y atributo de lomo (lado hacia el borde del huevo)
    kd = mathutils.kdtree.KDTree(n)
    for i, p in enumerate(sm): kd.insert(p, i)
    kd.balance(); mw = eo.matrix_world; mi = mw.inverted(); me = eo.data
    att = me.attributes.new('dors', 'FLOAT', 'POINT')
    for v in me.vertices:
        wv = mw @ v.co; co, i, _ = kd.find(wv); wv.z = co.z + (wv.z - co.z) * 0.6; v.co = mi @ wv
        out = co - c; out.z = 0; off = wv - co; off.z = 0
        s = off.dot(out.normalized()) / (0.15 * R) if out.length > 1e-6 else 0
        att.data[v.index].value = max(0.0, min(1.0, 0.5 + 0.8 * s))
    me.materials.append(emb)
    return c, R
CR = [egg_at(k) for k in range(len(EGGS))]
for x, y, rp, k in OILS:
    c, R = CR[k]; q = P(x, y) - P(EGGS[k][0], EGGS[k][1]); d = q.length
    o = sphere('oil', rp / PX, c + q + mathutils.Vector((0, 0, math.sqrt(max((0.8 * R) ** 2 - d * d, 0)) * 0.3)), 48); o.data.materials.append(oil)
    if k == 2:                                               # melanoforos estrellados sobre la gota
        for _ in range(4):
            s_ = sphere('star', 0.008, o.location + mathutils.Vector((random.uniform(-.2, .2), random.uniform(-.2, .2), rp / PX * 0.9)), 8)
            s_.scale = (random.uniform(3, 6), 0.6, 0.5); s_.rotation_euler = (0, 0, random.uniform(0, 3.14)); s_.data.materials.append(star)
# ---- luz: difusor detras (abajo) con caida suave segun el angulo; el lado que no ve el difusor queda marron
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; wn = w.node_tree; wb = wn.nodes['Background']
wtc = wn.nodes.new('ShaderNodeTexCoord'); vm = wn.nodes.new('ShaderNodeVectorMath'); vm.operation = 'DOT_PRODUCT'
TILT = float(os.environ.get('TILT', '0.25'))
d_ = mathutils.Vector((0, -TILT, -1)).normalized(); vm.inputs[1].default_value = d_
wn.links.new(wtc.outputs['Generated'], vm.inputs[0])
cone = wn.nodes.new('ShaderNodeMapRange'); wn.links.new(vm.outputs['Value'], cone.inputs[0])
CA = float(os.environ.get('CONE', '30'))
cone.inputs[1].default_value = math.cos(math.radians(CA * 1.8)); cone.inputs[2].default_value = math.cos(math.radians(CA * 0.4)); cone.interpolation_type = 'SMOOTHERSTEP'
mixc = wn.nodes.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; wn.links.new(cone.outputs[0], mixc.inputs['Factor'])
mixc.inputs[6].default_value = (0.22, 0.14, 0.06, 1); mixc.inputs[7].default_value = (0.6, 0.56, 0.45, 1)
wn.links.new(mixc.outputs[2], wb.inputs['Color']); wb.inputs['Strength'].default_value = 1.0
# ---- LOOK=dark: campo oscuro (como las fotos de lupa con aro de luz): fondo negro, luz rasante desde los costados,
# el corion se ve como un aro brillante, el embrion y los granulos blancos y lechosos; aro de luz desenfocado detras.
if os.environ.get('LOOK') == 'dark':
    wb.inputs['Color'].default_value = (0, 0, 0, 1)
    for l in list(wn.links):
        if l.to_node == wb and l.to_socket.name == 'Color': wn.links.remove(l)
    zs = wn.nodes.new('ShaderNodeSeparateXYZ'); wn.links.new(wtc.outputs['Generated'], zs.inputs[0])
    band = wn.nodes.new('ShaderNodeMapRange'); wn.links.new(zs.outputs['Z'], band.inputs[0]); band.interpolation_type = 'SMOOTHSTEP'
    band.inputs[1].default_value = -0.5; band.inputs[2].default_value = -0.2; band.inputs[3].default_value = 0.0; band.inputs[4].default_value = 1.0
    cut = wn.nodes.new('ShaderNodeMapRange'); wn.links.new(zs.outputs['Z'], cut.inputs[0]); cut.inputs[1].default_value = -0.1; cut.inputs[2].default_value = 0.15; cut.inputs[3].default_value = 1.0; cut.inputs[4].default_value = 0.0
    bm_ = wn.nodes.new('ShaderNodeMath'); bm_.operation = 'MULTIPLY'; wn.links.new(band.outputs[0], bm_.inputs[0]); wn.links.new(cut.outputs[0], bm_.inputs[1])
    wb.inputs['Color'].default_value = (0.9, 0.9, 1.0, 1); sm_ = wn.nodes.new('ShaderNodeMath'); sm_.operation = 'MULTIPLY'; sm_.inputs[1].default_value = float(os.environ.get('DSTR', '2.0')); wn.links.new(bm_.outputs[0], sm_.inputs[0]); wn.links.new(sm_.outputs[0], wb.inputs['Strength'])
    # corion: vidrio limpio, sin tinte (el aro brillante sale del reflejo/refraccion de la luz rasante)
    bb = egg.node_tree.nodes['Principled BSDF']
    for l in list(egg.node_tree.links):
        if l.to_socket == bb.inputs['Base Color']: egg.node_tree.links.remove(l)
    bb.inputs['Base Color'].default_value = (1, 1, 1, 1); glow.inputs['Strength'].default_value = 0
    bb.inputs['Specular IOR Level'].default_value = float(os.environ.get('SPEC', '0.15'))
    # corion en campo oscuro: transparente, solo el borde brilla (linea fina + halo suave hacia adentro)
    N, Lk = egg.node_tree.nodes, egg.node_tree.links
    clw = N.new('ShaderNodeLayerWeight'); clw.inputs['Blend'].default_value = 0.5
    line = N.new('ShaderNodeMapRange'); Lk.new(clw.outputs['Facing'], line.inputs[0]); line.inputs[1].default_value = 0.9; line.inputs[2].default_value = 0.985; line.interpolation_type = 'SMOOTHSTEP'
    halo = N.new('ShaderNodeMapRange'); Lk.new(clw.outputs['Facing'], halo.inputs[0]); halo.inputs[1].default_value = 0.55; halo.inputs[2].default_value = 0.95; halo.inputs[4].default_value = 0.035
    cem = N.new('ShaderNodeEmission'); cem.inputs['Color'].default_value = (0.95, 0.94, 0.9, 1)
    Lk.new(MATH(N, Lk, 'ADD', MATH(N, Lk, 'MULTIPLY', line.outputs[0], float(os.environ.get('RIMB', '1.6'))), halo.outputs[0]), cem.inputs['Strength'])
    ctr = N.new('ShaderNodeBsdfTransparent'); cad = N.new('ShaderNodeAddShader'); Lk.new(ctr.outputs[0], cad.inputs[0]); Lk.new(cem.outputs[0], cad.inputs[1])
    Lk.new(cad.outputs[0], N['Material Output'].inputs['Surface'])
    for o in sc.objects:
        if o.name.startswith('egg'):
            for m_ in list(o.modifiers): o.modifiers.remove(m_)
    for l in list(egg.node_tree.links):
        if l.to_socket == glow.inputs['Strength']: egg.node_tree.links.remove(l)
    # embrion: tejido lechoso que dispersa la luz (difuso + translucido), granulos blancos en lugar de pigmento oscuro
    N, Lk = emb.node_tree.nodes, emb.node_tree.links
    tl = N.new('ShaderNodeBsdfTranslucent'); tl.inputs['Color'].default_value = (0.95, 0.94, 0.92, 1)
    df = N.new('ShaderNodeBsdfDiffuse'); df.inputs['Color'].default_value = (0.9, 0.89, 0.87, 1)
    tr = N.new('ShaderNodeBsdfTransparent')
    milk = N.new('ShaderNodeMixShader'); milk.inputs[0].default_value = 0.2; Lk.new(tl.outputs[0], milk.inputs[1]); Lk.new(df.outputs[0], milk.inputs[2])
    bv = N.new('ShaderNodeTexVoronoi'); bv.inputs['Scale'].default_value = 40; Lk.new(tc.outputs['Object'], bv.inputs['Vector'])
    bfac = MATH(N, Lk, 'MINIMUM', 1.0, MATH(N, Lk, 'ADD', MATH(N, Lk, 'MULTIPLY', MATH(N, Lk, 'LESS_THAN', bv.outputs['Distance'], 0.3), 0.55), MATH(N, Lk, 'MULTIPLY', nz.outputs['Fac'], 0.45)))
    body = N.new('ShaderNodeMixShader'); Lk.new(bfac, body.inputs[0]); Lk.new(tr.outputs[0], body.inputs[1]); Lk.new(milk.outputs[0], body.inputs[2])
    wd_ = N.new('ShaderNodeBsdfTranslucent'); wd_.inputs['Color'].default_value = (1, 1, 1, 1)
    gm = N.new('ShaderNodeMixShader'); Lk.new(MATH(N, Lk, 'MINIMUM', 1.0, MATH(N, Lk, 'ADD', mel, ery)), gm.inputs[0]); Lk.new(body.outputs[0], gm.inputs[1]); Lk.new(wd_.outputs[0], gm.inputs[2])
    Lk.new(gm.outputs[0], N['Material Output'].inputs['Surface'])
    # gota de aceite: lente de vidrio clara
    N, Lk = oil.node_tree.nodes, oil.node_tree.links
    og = N.new('ShaderNodeBsdfPrincipled'); og.inputs['Transmission Weight'].default_value = 1; og.inputs['IOR'].default_value = 1.15; og.inputs['Roughness'].default_value = 0.05
    og.inputs['Base Color'].default_value = (1, 0.97, 0.88, 1); Lk.new(og.outputs[0], N['Material Output'].inputs['Surface'])
    for o in list(sc.objects):
        if o.name.startswith(('yolk', 'wisp')): o.hide_render = True
    # racimos de granulos blancos dentro de cada huevo
    gmat, N, Lk = mat('gran'); N.remove(N['Principled BSDF']); gd = N.new('ShaderNodeBsdfDiffuse'); gd.inputs['Color'].default_value = (0.95, 0.95, 0.95, 1)
    gt = N.new('ShaderNodeBsdfTranslucent'); gx = N.new('ShaderNodeMixShader'); gx.inputs[0].default_value = 0.85
    Lk.new(gd.outputs[0], gx.inputs[1]); Lk.new(gt.outputs[0], gx.inputs[2])
    gl_ = N.new('ShaderNodeLayerWeight'); ge = N.new('ShaderNodeEmission'); ge.inputs['Color'].default_value = (1, 1, 1, 1)
    gr_ = N.new('ShaderNodeMapRange'); Lk.new(gl_.outputs['Facing'], gr_.inputs[0]); gr_.inputs[3].default_value = 0.7; gr_.inputs[4].default_value = 0.15; Lk.new(gr_.outputs[0], ge.inputs['Strength'])
    ga_ = N.new('ShaderNodeAddShader'); Lk.new(gx.outputs[0], ga_.inputs[0]); Lk.new(ge.outputs[0], ga_.inputs[1]); Lk.new(ga_.outputs[0], N['Material Output'].inputs['Surface'])
    gme = bpy.data.meshes.new('g'); bmg = bmesh.new(); bmesh.ops.create_icosphere(bmg, subdivisions=2, radius=1.0); bmg.to_mesh(gme); bmg.free()
    for p_ in gme.polygons: p_.use_smooth = True
    gme.materials.append(gmat); R_ = random.Random(21)
    for (c, R) in CR:
        for _ in range(14):
            a = R_.uniform(0, 6.28); r_ = R * 0.78 * math.sqrt(R_.random()); cc = c + mathutils.Vector((r_ * math.cos(a), r_ * math.sin(a), R_.uniform(-0.3, 0.5) * R))
            sz = R_.uniform(0.05, 0.13) * R
            for _ in range(R_.randint(6, 22)):
                q = cc + mathutils.Vector((R_.gauss(0, sz), R_.gauss(0, sz), R_.gauss(0, sz * 0.4)))
                if (q - c).length > 0.9 * R: continue
                g = bpy.data.objects.new('gran', gme); sc.collection.objects.link(g); g.location = q; g.scale = (R * R_.uniform(0.014, 0.026),) * 3
        for _ in range(40):                                  # puntitos sueltos
            a = R_.uniform(0, 6.28); r_ = R * 0.85 * math.sqrt(R_.random()); q = c + mathutils.Vector((r_ * math.cos(a), r_ * math.sin(a), R_.uniform(-0.4, 0.5) * R))
            g = bpy.data.objects.new('gran', gme); sc.collection.objects.link(g); g.location = q; g.scale = (R * R_.uniform(0.006, 0.012),) * 3
    # aro de luz desenfocado detras (el borde iluminado de la placa)
    bpy.ops.mesh.primitive_torus_add(major_radius=9.0, minor_radius=1.1, major_segments=128, minor_segments=24, location=(11.5, -3.5, -9))
    ring = bpy.context.object; ring.scale = (0.75, 1.0, 1.0)
    rmat, N, Lk = mat('ring'); N.remove(N['Principled BSDF']); re_ = N.new('ShaderNodeEmission'); re_.inputs['Color'].default_value = (0.62, 0.6, 0.78, 1); rlw = N.new('ShaderNodeLayerWeight'); rlw.inputs['Blend'].default_value = 0.5
    rpw = N.new('ShaderNodeMath'); rpw.operation = 'POWER'; Lk.new(rlw.outputs['Facing'], rpw.inputs[0]); rpw.inputs[1].default_value = 2.5
    rinv = N.new('ShaderNodeMath'); rinv.operation = 'MULTIPLY_ADD'; Lk.new(rpw.outputs[0], rinv.inputs[0]); rinv.inputs[1].default_value = -0.8; rinv.inputs[2].default_value = 0.8; Lk.new(rinv.outputs[0], re_.inputs['Strength'])
    rtr = N.new('ShaderNodeBsdfTransparent'); rmx = N.new('ShaderNodeAddShader'); Lk.new(re_.outputs[0], rmx.inputs[0]); Lk.new(rtr.outputs[0], rmx.inputs[1]); re_ = rmx
    Lk.new(re_.outputs[0], N['Material Output'].inputs['Surface']); ring.data.materials.append(rmat)
    # fondo: placa oscura apenas verdosa con un velo de luz
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -10)); pl = bpy.context.object
    pm_, N, Lk = mat('plate'); N.remove(N['Principled BSDF']); pe = N.new('ShaderNodeEmission'); pn = N.new('ShaderNodeTexNoise'); pn.inputs['Scale'].default_value = 0.08
    pr = N.new('ShaderNodeMapRange'); Lk.new(pn.outputs['Fac'], pr.inputs[0]); pr.inputs[3].default_value = 0.008; pr.inputs[4].default_value = 0.09
    pe.inputs['Color'].default_value = (0.55, 0.62, 0.58, 1); Lk.new(pr.outputs[0], pe.inputs['Strength']); Lk.new(pe.outputs[0], N['Material Output'].inputs['Surface']); pl.data.materials.append(pm_)
if os.environ.get('HIDE'):
    for o in sc.objects:
        if o.name.startswith(tuple(os.environ['HIDE'].split(','))): o.hide_render = True
# ---- camara de lupa: ortografica, foco en el plano de los huevos de arriba
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = 1280 / PX
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); cam.location = (0, 0, 30); sc.camera = cam
cd.dof.use_dof = True; cd.dof.focus_distance = 30.0; cd.dof.aperture_fstop = float(os.environ.get('FSTOP', '0.6'))
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SPP; sc.cycles.use_denoising = SPP < 100
sc.cycles.max_bounces = 24; sc.cycles.transmission_bounces = 24; sc.cycles.transparent_max_bounces = 32
sc.render.resolution_x = RW; sc.render.resolution_y = RW * 3 // 4
sc.view_settings.view_transform = 'Standard'
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print('DONE')
