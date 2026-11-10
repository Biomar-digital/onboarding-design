# Video 3D del fry de trucha (personaje): nada, frena, mira hacia arriba con duda y aparece una burbuja de pensamiento vacia.
# El cuerpo y las aletas salen de la silueta exacta del icono (.ai -> svg -> extraer_silueta.py -> silueta.json).
# Piel y ojos como el fry real; agua con el mismo sistema del film del camaron (volumen con dispersion, gobo de
# causticas que abre los rayos, superficie con olas vista desde abajo, particulas). Eevee, 1920x1080, 25 fps, 5 s.
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
rings = []; ring_u = []
for k in range(NS + 1):
    u = k / NS; x = X0 + 1.2 + u * (X1 - X0 - 2.4)
    sct = section(x)
    if sct is None: continue
    top, bot = sct; X, Zt = P(x, top); _, Zb = P(x, bot)
    zc, h = (Zt + Zb) / 2, (Zt - Zb) / 2; w = h * thick(u)
    if u > 0.94: w *= max(0.25, 1 - (u - 0.94) / 0.06 * 0.6)
    rings.append([(X, w * math.sin(2 * math.pi * j / M), zc + h * math.cos(2 * math.pi * j / M)) for j in range(M)]); ring_u.append(u)
me = bpy.data.meshes.new('fry'); bm = bmesh.new()
vv = [[bm.verts.new(p) for p in r] for r in rings]
for a, b in zip(vv[:-1], vv[1:]):
    for j in range(M): bm.faces.new((a[j], a[(j + 1) % M], b[(j + 1) % M], b[j]))
bm.faces.new(vv[0][::-1]); bm.faces.new(vv[-1])
bm.to_mesh(me); body = bpy.data.objects.new('FRY_cuerpo', me); sc.collection.objects.link(body)
att = me.attributes.new('pez', 'FLOAT_VECTOR', 'POINT')                          # u cola->nariz, c panza(-1)..lomo(1), s lado
for k, u in enumerate(ring_u):
    for j in range(M): att.data[k * M + j].vector = (u, math.cos(2 * math.pi * j / M), math.sin(2 * math.pi * j / M))
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
# ---- piel como el fry real (foto de referencia): plateado, lomo verde-azulado oscuro, panza blanca, marcas "parr" ovaladas
#      azul-grisaceas sobre la linea lateral, pintitas oscuras en el lomo, rosado suave en el flanco, borde del operculo
#      e iridiscencia. Las coordenadas salen del atributo 'pez' (u: cola->nariz, c: panza -1 .. lomo 1, s: lado).
def caustic(nt, strength):                                                       # causticas animadas desde arriba (posicion en el mundo)
    geo = nt.nodes.new('ShaderNodeNewGeometry'); vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.voronoi_dimensions = '4D'; vo.feature = 'DISTANCE_TO_EDGE'
    vo.inputs['Scale'].default_value = 7.0
    wn = nt.nodes.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = 4.0; wn.inputs['Detail'].default_value = 1.0; nt.links.new(geo.outputs['Position'], wn.inputs['Vector'])
    wa = nt.nodes.new('ShaderNodeVectorMath'); wa.operation = 'SCALE'; wa.inputs['Scale'].default_value = 0.09; nt.links.new(wn.outputs['Color'], wa.inputs[0])
    wp = nt.nodes.new('ShaderNodeVectorMath'); wp.operation = 'ADD'; nt.links.new(geo.outputs['Position'], wp.inputs[0]); nt.links.new(wa.outputs[0], wp.inputs[1])
    nt.links.new(wp.outputs[0], vo.inputs['Vector'])
    for f in (1, NF):
        vo.inputs['W'].default_value = f * 0.03; vo.inputs['W'].keyframe_insert('default_value', frame=f)
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.06
    mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0; nt.links.new(vo.outputs['Distance'], mr.inputs['Value'])
    sn = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'], sn.inputs[0])
    up = nt.nodes.new('ShaderNodeMath'); up.operation = 'MAXIMUM'; up.inputs[1].default_value = 0.0; nt.links.new(sn.outputs['Z'], up.inputs[0])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; nt.links.new(mr.outputs[0], m1.inputs[0]); nt.links.new(up.outputs[0], m1.inputs[1])
    vz = nt.nodes.new('ShaderNodeTexNoise'); vz.inputs['Scale'].default_value = 1.2; nt.links.new(geo.outputs['Position'], vz.inputs['Vector'])
    vr = nt.nodes.new('ShaderNodeMapRange'); vr.inputs['From Min'].default_value = 0.35; vr.inputs['From Max'].default_value = 0.7; nt.links.new(vz.outputs['Fac'], vr.inputs['Value'])
    m3 = nt.nodes.new('ShaderNodeMath'); m3.operation = 'MULTIPLY'; nt.links.new(m1.outputs[0], m3.inputs[0]); nt.links.new(vr.outputs[0], m3.inputs[1])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = strength; nt.links.new(m3.outputs[0], m2.inputs[0])
    return m2.outputs[0]
def N(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items(): n.inputs[k].default_value = v
    return n
def M(nt, op, a, b=None, clamp=False):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op; n.use_clamp = clamp
    for i, x in enumerate((a, b)):
        if x is None: continue
        if isinstance(x, (int, float)): n.inputs[i].default_value = x
        else: nt.links.new(x, n.inputs[i])
    return n.outputs[0]
def smooth(nt, x, e0, e1):
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; mr.inputs['From Min'].default_value = e0; mr.inputs['From Max'].default_value = e1
    nt.links.new(x, mr.inputs['Value']); return mr.outputs['Result']
def mixc(nt, fac, a, b):
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    for sock, v in ((mx.inputs[0], fac), (mx.inputs[6], a), (mx.inputs[7], b)):
        if isinstance(v, tuple): sock.default_value = v if len(v) == 4 else (*v, 1)
        elif isinstance(v, (int, float)): sock.default_value = v
        else: nt.links.new(v, sock)
    return mx.outputs[2]
m_body = bpy.data.materials.new('piel_fry'); m_body.use_nodes = True; nt = m_body.node_tree; bs = nt.nodes['Principled BSDF']
at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'pez'; sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(at.outputs['Vector'], sp.inputs[0])
U, C, SD = sp.outputs[0], sp.outputs[1], sp.outputs[2]
rmp = nt.nodes.new('ShaderNodeValToRGB'); rmp.color_ramp.interpolation = 'B_SPLINE'
el = rmp.color_ramp.elements; el[0].position = 0.0; el[0].color = (*lin((245, 250, 252)), 1); el[1].position = 1.0; el[1].color = (*lin((40, 96, 140)), 1)
for pos, c in ((0.45, (196, 226, 242)), (0.72, (104, 166, 206))): e = el.new(pos); e.color = (*lin(c), 1)
nt.links.new(smooth(nt, C, -1.0, 1.0), rmp.inputs['Fac'])
col = rmp.outputs['Color']
noi = N(nt, 'ShaderNodeTexNoise', Scale=6.0, Detail=3.0); nt.links.new(at.outputs['Vector'], noi.inputs['Vector'])
# marcas parr: 9 ovalos sobre la linea lateral, de u=0.18 a 0.80
ph = M(nt, 'ADD', M(nt, 'MULTIPLY', U, 2 * math.pi * 9.5), M(nt, 'MULTIPLY', noi.outputs['Fac'], 1.2))
wav = M(nt, 'MULTIPLY_ADD', M(nt, 'COSINE', ph), 0.5); nt.nodes[-1].inputs[2].default_value = 0.5
lat = M(nt, 'ABSOLUTE', M(nt, 'SUBTRACT', C, 0.08))
ell = M(nt, 'SQRT', M(nt, 'ADD', M(nt, 'POWER', M(nt, 'DIVIDE', M(nt, 'SUBTRACT', 1.0, wav), 0.42), 2.0), M(nt, 'POWER', M(nt, 'DIVIDE', lat, 0.36), 2.0)))
parr = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, ell, 0.55, 1.0)),
         M(nt, 'MULTIPLY', smooth(nt, U, 0.16, 0.24), M(nt, 'SUBTRACT', 1.0, smooth(nt, U, 0.74, 0.82))))
col = mixc(nt, M(nt, 'MULTIPLY', parr, 0.85), col, lin((58, 104, 140)))
# pintitas oscuras en el lomo y la parte alta del flanco
vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 1.0; vor.inputs['Randomness'].default_value = 0.9
vm = nt.nodes.new('ShaderNodeVectorMath'); vm.operation = 'MULTIPLY'; vm.inputs[1].default_value = (55.0, 9.0, 9.0)
nt.links.new(at.outputs['Vector'], vm.inputs[0]); nt.links.new(vm.outputs[0], vor.inputs['Vector'])
spots = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, vor.outputs['Distance'], 0.14, 0.2)),
          M(nt, 'MULTIPLY', smooth(nt, C, 0.0, 0.3), M(nt, 'MULTIPLY', smooth(nt, U, 0.12, 0.2), M(nt, 'SUBTRACT', 1.0, smooth(nt, U, 0.86, 0.93)))))
col = mixc(nt, M(nt, 'MULTIPLY', spots, 0.85), col, lin((38, 48, 54)))
# rosado suave en el flanco (mas hacia la cola) y borde del operculo
pink = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, lat, 0.1, 0.4)), M(nt, 'SUBTRACT', 1.0, smooth(nt, U, 0.35, 0.8)))
col = mixc(nt, M(nt, 'MULTIPLY', pink, 0.1), col, lin((232, 160, 170)))
oper = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, M(nt, 'ABSOLUTE', M(nt, 'SUBTRACT', M(nt, 'SUBTRACT', U, M(nt, 'MULTIPLY', M(nt, 'MULTIPLY', C, C), 0.025)), 0.80)), 0.003, 0.008)),
         M(nt, 'SUBTRACT', 1.0, smooth(nt, M(nt, 'ABSOLUTE', C), 0.6, 0.8)))
col = mixc(nt, M(nt, 'MULTIPLY', oper, 0.55), col, lin((60, 80, 88)))
nt.links.new(col, bs.inputs['Base Color'])
bs.inputs['Metallic'].default_value = 0.12; bs.inputs['Roughness'].default_value = 0.38; bs.inputs['Specular IOR Level'].default_value = 0.4
bs.inputs['Coat Weight'].default_value = 0.15; bs.inputs['Coat Roughness'].default_value = 0.15
bs.inputs['Thin Film Thickness'].default_value = 260.0; bs.inputs['Thin Film IOR'].default_value = 1.5
bs.inputs['Subsurface Weight'].default_value = 0.15; bs.inputs['Subsurface Radius'].default_value = (0.04, 0.06, 0.07)
bs.inputs['Emission Color'].default_value = (*lin((255, 250, 225)), 1); nt.links.new(caustic(nt, 0.35), bs.inputs['Emission Strength'])
body.data.materials.append(m_body)
# aletas: translucidas con radios finos y un toque rosado
m_fin = bpy.data.materials.new('aletas_fry'); m_fin.use_nodes = True; nt = m_fin.node_tree; bs = nt.nodes['Principled BSDF']   # translucidas
tc = nt.nodes.new('ShaderNodeTexCoord'); wv = N(nt, 'ShaderNodeTexWave', Scale=28.0, Distortion=0.6)
wv.bands_direction = 'X'; nt.links.new(tc.outputs['Generated'], wv.inputs['Vector'])
rays = smooth(nt, wv.outputs['Fac'], 0.55, 0.9)
bs.inputs['Base Color'].default_value = (*lin((200, 225, 238)), 1); bs.inputs['Roughness'].default_value = 0.35
nt.links.new(M(nt, 'MULTIPLY_ADD', rays, 0.3), bs.inputs['Alpha']); nt.nodes[-1].inputs[2].default_value = 0.5
m_fin.surface_render_method = 'DITHERED'
for f in fins: f.data.materials.append(m_fin)
# ojo real: iris plateado-dorado con estrias, pupila negra grande y brillante, brillo puntual
m_white = bpy.data.materials.new('iris'); m_white.use_nodes = True; nt = m_white.node_tree; bs = nt.nodes['Principled BSDF']
noi = N(nt, 'ShaderNodeTexNoise', Scale=40.0, Detail=2.0)
bs.inputs['Metallic'].default_value = 0.25; bs.inputs['Roughness'].default_value = 0.3
nt.links.new(mixc(nt, noi.outputs['Fac'], lin((150, 170, 180)), lin((225, 232, 236))), bs.inputs['Base Color'])   # iris plateado como el fry real
bs.inputs['Coat Weight'].default_value = 1.0; bs.inputs['Coat Roughness'].default_value = 0.02
m_navy = mat('pupila', (0.004, 0.005, 0.006), 0.05); m_navy.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 1.0
m_hl = mat('brillo', (1, 1, 1), 0.1, emit=6)
m_brow = mat('ceja', lin((44, 58, 62)), 0.4)
m_lid = mat('parpado', lin((112, 162, 188)), 0.35, rim=lin((52, 88, 110)))   # opaco: sin SSS (una cascara fina con SSS se ve de vidrio)
# ------------------------------------------------------------------ cara: ojos, ceja, boca (sobre el ojo y la boca del icono)
EX, EZ = P(1292, 552); ER = 0.058
eyes = []
for sgn in (-1, 1):
    yb = sgn * half_w(EX) * 0.66
    piv = bpy.data.objects.new(f'FRY_ojo_piv_{sgn}', None); sc.collection.objects.link(piv); piv.location = (EX, yb, EZ)
    ctl = bpy.data.objects.new(f'FRY_ojo_ctl_{sgn}', None); sc.collection.objects.link(ctl); ctl.parent = piv   # mirada + parpadeo
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER, location=(0, 0, 0), segments=32, ring_count=16); ball = bpy.context.object
    ball.name = f'FRY_ojo_{sgn}'; ball.data.materials.append(m_white); ball.parent = ctl
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.5, location=(0.004, sgn * ER * 0.84, 0.004), segments=24, ring_count=12); pup = bpy.context.object
    pup.scale.y = 0.55; pup.data.materials.append(m_navy); pup.parent = ctl; pup.name = f'FRY_pupila_{sgn}'
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.13, location=(0.016, sgn * ER * 1.0, 0.02)); hl = bpy.context.object
    hl.data.materials.append(m_hl); hl.parent = ctl; hl.name = f'FRY_brillo_{sgn}'
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.06, location=(-0.012, sgn * ER * 1.0, -0.014)); hl2 = bpy.context.object
    hl2.data.materials.append(m_hl); hl2.parent = ctl; hl2.name = f'FRY_brillo2_{sgn}'
    # parpado superior: media cascara del color del cuerpo; girando en X baja/sube (expresion)
    lm = bpy.data.meshes.new(f'parpado_{sgn}'); lb = bmesh.new()
    bmesh.ops.create_uvsphere(lb, u_segments=32, v_segments=16, radius=ER * 1.08)
    bmesh.ops.delete(lb, geom=[v for v in lb.verts if v.co.z < -0.001], context='VERTS'); lb.to_mesh(lm)
    lid = bpy.data.objects.new(f'FRY_parpado_{sgn}', lm); sc.collection.objects.link(lid); lid.parent = piv; lid.data.materials.append(m_lid)
    so_ = lid.modifiers.new('grosor', 'SOLIDIFY'); so_.thickness = ER * 0.12; so_.offset = 1
    lid.rotation_mode = 'XYZ'
    for p in lm.polygons: p.use_smooth = True
    for o in (ball, pup, hl):
        for p in o.data.polygons: p.use_smooth = True
    # ceja: arco fino sobre el ojo, apoyado en la superficie del cuerpo
    cu = bpy.data.curves.new(f'ceja_{sgn}', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0034; cu.bevel_resolution = 3
    spl = cu.splines.new('BEZIER'); spl.bezier_points.add(2)
    for i, (dx, dz) in enumerate(((-0.034, 0.040), (0.0, 0.052), (0.030, 0.046))):
        bp = spl.bezier_points[i]; bp.co = (dx, sgn * 0.004, dz); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    brow = bpy.data.objects.new(f'FRY_ceja_{sgn}', cu); sc.collection.objects.link(brow); brow.parent = piv
    brow.data.materials.append(m_brow)
    brow.hide_render = True; brow.hide_viewport = True                         # sin cejas dibujadas: la expresion la dan los parpados
    eyes.append((piv, brow, ctl, lid))
MX, MZ = P(1371, 604)
cu = bpy.data.curves.new('boca', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0032; cu.bevel_resolution = 3
for sgn in (-1, 1):
    spl = cu.splines.new('BEZIER'); spl.bezier_points.add(2); yb = sgn * half_w(MX - 0.012) * 0.92
    for i, (dx, dz) in enumerate(((-0.028, -0.006), (-0.012, 0.0), (0.004, -0.002))):
        bp = spl.bezier_points[i]; bp.co = (MX + dx, yb * (1 - 0.3 * (i == 2)), MZ + dz); bp.handle_left_type = bp.handle_right_type = 'AUTO'
mouth = bpy.data.objects.new('FRY_boca', cu); sc.collection.objects.link(mouth); mouth.data.materials.append(m_brow)
# ------------------------------------------------------------------ rig: 10 huesos de la cabeza a la cola (ola de nado continua), pesos por posicion en X
arm_d = bpy.data.armatures.new('rig'); rig = bpy.data.objects.new('FRY_rig', arm_d); sc.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
JX = [0.52, 0.30, 0.18, 0.08, -0.02, -0.12, -0.22, -0.31, -0.40, -0.47, -0.53]
bones = []
for i in range(len(JX) - 1):
    b = arm_d.edit_bones.new(f'b{i}'); b.head = (JX[i], 0, 0); b.tail = (JX[i + 1], 0, 0); b.roll = 0
    if bones: b.parent = bones[-1]; b.use_connect = True
    bones.append(b)
bpy.ops.object.mode_set(mode='OBJECT')
NB = len(JX) - 1
def bone_tail_inv():                                                             # hijo de hueso: Blender lo ubica en la COLA del hueso, con su orientacion
    bl = rig.data.bones['b0']; M_ = bl.matrix_local.copy(); M_.translation = bl.tail_local
    return (rig.matrix_world @ M_).inverted()
def weigh(o):
    vg = {i: o.vertex_groups.new(name=f'b{i}') for i in range(NB)}
    mw = o.matrix_world; c = [(JX[i] + JX[i + 1]) / 2 for i in range(NB)]
    for v in o.data.vertices:
        X = (mw @ v.co).x
        if X >= c[0]: vg[0].add([v.index], 1.0, 'REPLACE'); continue
        if X <= c[-1]: vg[NB - 1].add([v.index], 1.0, 'REPLACE'); continue
        for i in range(NB - 1):
            if c[i + 1] <= X <= c[i]:
                t = (c[i] - X) / (c[i] - c[i + 1]); t = t * t * (3 - 2 * t); vg[i].add([v.index], 1 - t, 'REPLACE'); vg[i + 1].add([v.index], t, 'REPLACE'); break
# aletas pares: pivote en su base (antes giraban alrededor del centro del pez)
for o in fins[1:]:
    me_ = o.data; xs_ = [v.co.x for v in me_.vertices]; zs_ = [v.co.z for v in me_.vertices]
    piv_ = Vector((max(xs_) - 0.012, 0, max(zs_)))
    for v in me_.vertices: v.co -= piv_
    o.location = (piv_.x, o.location.y, piv_.z); o.rotation_mode = 'XYZ'
bpy.context.view_layer.update()
for o in [body, mouth] + fins:
    if o.type == 'CURVE':
        o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'b0'; o.matrix_parent_inverse = bone_tail_inv(); continue
    mw0 = o.matrix_world.copy(); weigh(o); am = o.modifiers.new('arm', 'ARMATURE'); am.object = rig
    o.modifiers.move(len(o.modifiers) - 1, 0)
    if o in fins[1:]: o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'b2'; o.matrix_parent_inverse = (rig.matrix_world @ rig.data.bones['b2'].matrix_local @ Matrix.Translation((0, rig.data.bones['b2'].length, 0))).inverted(); o.modifiers.remove(am)
    else: o.parent = rig
for piv, brow, ctl, lid in eyes:
    piv.parent = rig; piv.parent_type = 'BONE'; piv.parent_bone = 'b0'
    piv.matrix_parent_inverse = bone_tail_inv()
# ------------------------------------------------------------------ animacion: nada, frena (curva en C + aletas abiertas), mira a camara,
# duda (entrecierra el ojo y sube la cabeza), y se ilumina de curiosidad cuando aparece la burbuja
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
def ease(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)
def bump(f, a, b): return math.sin(math.pi * min(max((f - a) / (b - a), 0), 1))
ENV = [0.10 + 0.9 * (i / (NB - 1)) ** 1.6 for i in range(NB)]                    # amplitud crece hacia la cola
phase = 0.0
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    cruise = 1 - ease((f - 40) / 12); hover = ease((f - 56) / 12)
    freq = 3.0 * cruise + 0.7 * hover + 1.4 * (1 - cruise) * (1 - hover); phase += 2 * math.pi * freq / FPS
    amp = 0.21 * cruise + 0.05 * hover + 0.12 * (1 - cruise) * (1 - hover)
    cbend = 0.11 * bump(f, 42, 60)                                                # frenada: curva en C
    for i, b in enumerate(rig.pose.bones):
        b.rotation_mode = 'XYZ'
        ang = amp * ENV[i] * math.sin(phase - 0.75 * i) * (1.6 if i else 1) - (0.06 * amp * math.sin(phase + 0.6) if i == 0 else 0)
        b.rotation_euler = (0, 0, ang + cbend * (0.4 if i == 0 else 1.0) * (1 if i < NB - 3 else 0.6))
        b.keyframe_insert('rotation_euler', frame=f)
    xs = -2.45 + 2.2 * (1 - (1 - min(1, (f - 1) / 58)) ** 2.2) + 0.03 * hover * math.sin(t * 1.3)
    zs = -0.07 + 0.015 * math.sin(t * 2.0) + 0.06 * ease((f - 64) / 26)
    rig.location = (xs, 0, zs); rig.keyframe_insert('location', frame=f)
    turn = ease((f - 54) / 10) * (1 - 0.5 * ease((f - 70) / 14))                   # gira hacia camara
    up_ = ease((f - 66) / 20)                                                    # sube la cabeza (duda) hacia la burbuja
    tilt = math.radians(6) * bump(f, 64, 100)                                    # inclina la cabeza (gesto de pregunta)
    rig.rotation_euler = (tilt, -math.radians(17) * up_ + math.radians(1.2) * math.sin(t * 1.7), -math.radians(14) * turn)
    rig.keyframe_insert('rotation_euler', frame=f)
    # aletas pares: remo rapido al nadar, se abren para frenar, remo suave para quedarse quieto
    brake = bump(f, 40, 62)
    for k, o in enumerate(fins[1:]):
        sg = 1 if 'aleta' in o.name and o.name.endswith('_1') else -1
        flap = math.sin(t * 2 * math.pi * (3.2 * cruise + 2.0 * hover + 1.0) + k * 0.7)
        o.rotation_euler = (sg * (math.radians(-12) - math.radians(55) * brake - math.radians(10) * (0.5 + 0.5 * flap) * (0.3 + 0.7 * hover)), 0,
                            math.radians(14) * flap * (0.4 + 0.6 * hover))
        o.keyframe_insert('rotation_euler', frame=f)
    # ojos y parpados: mira a camara, entrecierra (duda), mira hacia arriba, se abre al ver la burbuja
    look_cam = ease((f - 54) / 6) * (1 - ease((f - 68) / 8)); look_up = ease((f - 68) / 10)
    squint = ease((f - 62) / 6) * (1 - ease((f - 92) / 6)); wide = ease((f - 92) / 5)
    for (piv, brow, ctl, lid), sgn in zip(eyes, (-1, 1)):
        cover = 0.16 + 0.24 * squint * (1 if sgn == -1 else 0.35) - 0.12 * wide
        lid.rotation_euler = (sgn * math.radians(90 - 180 * cover), 0, 0); lid.keyframe_insert('rotation_euler', frame=f)
        ctl.rotation_euler = (sgn * 0.28 * look_up, 0, -sgn * (0.22 * look_up - 0.35 * look_cam)); ctl.keyframe_insert('rotation_euler', frame=f)
        s_ = 1 + 0.06 * wide; ctl.scale = (s_, s_, s_); ctl.keyframe_insert('scale', frame=f)
for fc in (rig.animation_data.action.fcurves if rig.animation_data else []):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# ------------------------------------------------------------------ agua: el mismo sistema del film del camaron (escala de este set: 1 u = largo del fry)
WT = 2.6                                                                        # superficie del agua
TEAL = lin((52, 165, 200))                                                       # turquesa claro y saturado (look animacion)
def emit_mat(name, colr, strength=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree; n.nodes.clear()
    out = n.nodes.new('ShaderNodeOutputMaterial'); em = n.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*colr, 1)
    em.inputs['Strength'].default_value = strength; n.links.new(em.outputs[0], out.inputs[0]); return m
# 1) volumen de agua con dispersion hacia adelante (como MAT_WaterVolume): da profundidad y deja ver los rayos
VOLUMEN = '--volumen' in argv                                                    # volumen real (lento sin GPU) o niebla de profundidad
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.0, (WT - 3.0) / 2)); vol = bpy.context.object; vol.hide_render = not VOLUMEN; vol.visible_shadow = VOLUMEN; vol.name = 'AGUA_volumen'; vol.scale = (22, 16, WT + 3.0)
mv = bpy.data.materials.new('agua_volumen'); mv.use_nodes = True; n = mv.node_tree; n.nodes.clear()
out = n.nodes.new('ShaderNodeOutputMaterial'); pv = n.nodes.new('ShaderNodeVolumePrincipled')
pv.inputs['Color'].default_value = (*lin((150, 215, 225)), 1); pv.inputs['Density'].default_value = 0.16
pv.inputs['Anisotropy'].default_value = 0.75; pv.inputs['Absorption Color'].default_value = (*lin((140, 205, 215)), 1)
n.links.new(pv.outputs[0], out.inputs['Volume']); vol.data.materials.append(mv)
# 2) gobo de causticas sobre la superficie (como MAT_Gobo): su sombra dibuja las causticas y abre los rayos en el volumen
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 3.0, WT + 1.2)); gobo = bpy.context.object; gobo.name = 'GOBO'; gobo.scale = (30, 26, 1)
gobo.hide_render = not VOLUMEN; gobo.visible_camera = False; gobo.visible_glossy = False; gobo.visible_diffuse = False
mg = bpy.data.materials.new('gobo'); mg.use_nodes = True; n = mg.node_tree; n.nodes.clear()
out = n.nodes.new('ShaderNodeOutputMaterial'); dif = n.nodes.new('ShaderNodeBsdfDiffuse'); dif.inputs['Color'].default_value = (0, 0, 0, 1)
tr = n.nodes.new('ShaderNodeBsdfTransparent'); mx = n.nodes.new('ShaderNodeMixShader')
tc = n.nodes.new('ShaderNodeTexCoord'); mp = n.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (30 / 0.55, 26 / 0.55, 1)
n.links.new(tc.outputs['Object'], mp.inputs['Vector'])
vo = n.nodes.new('ShaderNodeTexVoronoi'); vo.voronoi_dimensions = '4D'; vo.feature = 'DISTANCE_TO_EDGE'
n.links.new(mp.outputs['Vector'], vo.inputs['Vector']); vo.inputs['W'].default_value = 0.0; vo.name = 'CAUSTIC_W'
nz = n.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 0.08; nz.name = 'SHAFT_W'
n.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
ed = n.nodes.new('ShaderNodeMapRange'); ed.inputs['From Min'].default_value = 0.0; ed.inputs['From Max'].default_value = 0.07   # lineas de caustica = luz
n.links.new(vo.outputs['Distance'], ed.inputs['Value'])
sh = n.nodes.new('ShaderNodeMapRange'); sh.inputs['From Min'].default_value = 0.35; sh.inputs['From Max'].default_value = 0.65  # manchas grandes de sombra = haces
sh.inputs['To Min'].default_value = 0.35; sh.inputs['To Max'].default_value = 1.0; n.links.new(nz.outputs['Fac'], sh.inputs['Value'])
al = n.nodes.new('ShaderNodeMath'); al.operation = 'MULTIPLY'; n.links.new(ed.outputs[0], al.inputs[0]); al.inputs[1].default_value = 1.0
al2 = n.nodes.new('ShaderNodeMath'); al2.operation = 'SUBTRACT'; al2.inputs[0].default_value = 1.0
n.links.new(al.outputs[0], al2.inputs[1])                                          # opacidad: 1 - luz
lit = n.nodes.new('ShaderNodeMath'); lit.operation = 'MULTIPLY'; n.links.new(al2.outputs[0], lit.inputs[0]); n.links.new(sh.outputs[0], lit.inputs[1])
op = n.nodes.new('ShaderNodeMath'); op.operation = 'SUBTRACT'; op.inputs[0].default_value = 1.0; n.links.new(lit.outputs[0], op.inputs[1])  # transmitido
n.links.new(op.outputs[0], mx.inputs['Fac']); n.links.new(dif.outputs[0], mx.inputs[1]); n.links.new(tr.outputs[0], mx.inputs[2])
n.links.new(mx.outputs[0], out.inputs[0]); mg.surface_render_method = 'DITHERED'
try: mg.use_transparent_shadow = True
except Exception: pass
gobo.data.materials.append(mg)
for f in range(1, NF + 1, 4):
    vo.inputs['W'].default_value = f * 0.035; vo.inputs['W'].keyframe_insert('default_value', frame=f)
    nz.inputs['W'].default_value = f * 0.01; nz.inputs['W'].keyframe_insert('default_value', frame=f)
# 3) superficie con olas vista desde abajo (como MAT_Pond_Water_Surface): espejo brillante que se mueve
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 4.0, WT)); surf = bpy.context.object; surf.name = 'AGUA_superficie'; surf.scale = (24, 18, 1)
ms = bpy.data.materials.new('superficie'); ms.use_nodes = True; n = ms.node_tree; bs = n.nodes['Principled BSDF']
bs.inputs['Base Color'].default_value = (*lin((200, 240, 245)), 1); bs.inputs['Roughness'].default_value = 0.05; bs.inputs['Metallic'].default_value = 0.6
bs.inputs['Emission Color'].default_value = (*lin((215, 245, 250)), 1); bs.inputs['Emission Strength'].default_value = 1.4
tc = n.nodes.new('ShaderNodeTexCoord'); mp = n.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (24, 18, 1); n.links.new(tc.outputs['Object'], mp.inputs['Vector'])
wz = n.nodes.new('ShaderNodeTexNoise'); wz.noise_dimensions = '4D'; wz.inputs['Scale'].default_value = 1.4; wz.inputs['Detail'].default_value = 6
n.links.new(mp.outputs['Vector'], wz.inputs['Vector'])
bump = n.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.6; n.links.new(wz.outputs['Fac'], bump.inputs['Height']); n.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
cr = n.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[1].position = 0.7
n.links.new(wz.outputs['Fac'], cr.inputs['Fac']); em = n.nodes.new('ShaderNodeMath'); em.operation = 'MULTIPLY_ADD'
n.links.new(cr.outputs['Color'], em.inputs[0]); em.inputs[1].default_value = 2.2; em.inputs[2].default_value = 0.6; n.links.new(em.outputs[0], bs.inputs['Emission Strength'])
surf.data.materials.append(ms); surf.visible_shadow = False                 # la superficie no tapa el sol
for f in range(1, NF + 1, 4): wz.inputs['W'].default_value = f * 0.02; wz.inputs['W'].keyframe_insert('default_value', frame=f)
# 4) lecho del rio: arena clara con causticas, piedritas redondeadas de colores y plantas que se mecen
FZ = -0.62
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 5.0, FZ)); bot = bpy.context.object; bot.name = 'FONDO_arena'; bot.scale = (60, 50, 1)
mb = bpy.data.materials.new('arena'); mb.use_nodes = True; n = mb.node_tree; bs = n.nodes['Principled BSDF']
tc = n.nodes.new('ShaderNodeTexCoord'); nb = n.nodes.new('ShaderNodeTexNoise'); nb.inputs['Scale'].default_value = 60.0; n.links.new(tc.outputs['Generated'], nb.inputs['Vector'])
cb = n.nodes.new('ShaderNodeValToRGB'); cb.color_ramp.elements[0].color = (*lin((176, 164, 128)), 1); cb.color_ramp.elements[1].color = (*lin((214, 202, 164)), 1)
n.links.new(nb.outputs['Fac'], cb.inputs['Fac']); n.links.new(cb.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.9
bs.inputs['Emission Color'].default_value = (*lin((255, 248, 220)), 1); n.links.new(caustic(n, 0.9), bs.inputs['Emission Strength'])
bot.data.materials.append(mb)
import random; R = random.Random(4)
PAL = [(150, 128, 104), (122, 116, 108), (176, 150, 112), (110, 120, 116), (160, 104, 84), (190, 176, 150), (96, 104, 92)]
pmats = []
for i, c in enumerate(PAL):
    m = bpy.data.materials.new(f'piedra_{i}'); m.use_nodes = True; nn = m.node_tree; b_ = nn.nodes['Principled BSDF']
    b_.inputs['Base Color'].default_value = (*lin(c), 1); b_.inputs['Roughness'].default_value = 0.55
    b_.inputs['Emission Color'].default_value = (*lin((255, 248, 220)), 1); nn.links.new(caustic(nn, 0.3), b_.inputs['Emission Strength']); pmats.append(m)
for i in range(170):                                                            # piedritas (mas grandes y espaciadas lejos)
    y = R.uniform(-0.6, 7.5); x = R.uniform(-1.3 - 0.45 * y, 1.3 + 0.45 * y); r = R.uniform(0.03, 0.11) * (1 + 0.12 * max(y, 0))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(x, y, FZ + r * 0.25)); o = bpy.context.object; o.name = f'FONDO_piedra_{i}'
    o.scale = (r * R.uniform(1.0, 1.6), r * R.uniform(0.9, 1.4), r * R.uniform(0.45, 0.7)); o.rotation_euler.z = R.uniform(0, 6.3)
    o.data.materials.append(pmats[R.randrange(len(pmats))])
    for p in o.data.polygons: p.use_smooth = True
m_pl = bpy.data.materials.new('planta'); m_pl.use_nodes = True; nn = m_pl.node_tree; b_ = nn.nodes['Principled BSDF']
b_.inputs['Base Color'].default_value = (*lin((70, 150, 70)), 1); b_.inputs['Subsurface Weight'].default_value = 0.5; b_.inputs['Roughness'].default_value = 0.45
b_.inputs['Emission Color'].default_value = (*lin((200, 255, 160)), 1); nn.links.new(caustic(nn, 0.5), b_.inputs['Emission Strength'])
m_pl2 = m_pl.copy(); m_pl2.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*lin((110, 160, 60)), 1)
for i in range(46):                                                             # plantas: cintas que se mecen (a los costados y al fondo)
    side = -1 if i % 2 else 1; y = R.uniform(0.3, 6.5); x = side * R.uniform(1.0 + 0.3 * y, 1.6 + 0.5 * y) if i % 5 else R.uniform(-1.5, 1.5)
    if i % 5 == 0: y = R.uniform(3.5, 7.0)
    hgt = R.uniform(0.35, 1.0) * (1 + 0.1 * y); cu = bpy.data.curves.new(f'planta_{i}', 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = R.uniform(0.012, 0.02) * (1 + 0.1 * y); cu.bevel_resolution = 2; spl = cu.splines.new('BEZIER'); nseg = 5; spl.bezier_points.add(nseg - 1)
    for k in range(nseg):
        bp = spl.bezier_points[k]; t = k / (nseg - 1); bp.co = (0.06 * math.sin(t * 3 + i) * t, 0, hgt * t)
        bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.tilt = R.uniform(-0.6, 0.6); bp.radius = 1.0 - 0.7 * t
    o = bpy.data.objects.new(f'FONDO_planta_{i}', cu); sc.collection.objects.link(o); o.location = (x, y, FZ); o.rotation_euler.z = R.uniform(0, 3.14)
    o.data.materials.append(m_pl if i % 3 else m_pl2); ph_ = R.uniform(0, 6.3); o.scale = (2.6, 0.7, 1.0)
    for f in range(1, NF + 1, 4):
        o.rotation_euler.x = 0.12 * math.sin(f / FPS * 1.6 + ph_); o.rotation_euler.y = 0.06 * math.sin(f / FPS * 1.1 + ph_); o.keyframe_insert('rotation_euler', frame=f)
# rayos de sol suaves desde la superficie (cintas de luz que se mueven lento)
for i in range(7):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-1.4 + i * 0.75 + R.uniform(-0.2, 0.2), 1.2 + i * 0.55, 0.9), rotation=(math.radians(90), math.radians(-18 + R.uniform(-4, 4)), 0))
    o = bpy.context.object; o.name = f'RAYO_{i}'; o.scale = (R.uniform(0.35, 0.8), 5.0, 1)
    m = bpy.data.materials.new(f'rayo_{i}'); m.use_nodes = True; nn = m.node_tree; nn.nodes.clear()
    out = nn.nodes.new('ShaderNodeOutputMaterial'); em = nn.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*lin((225, 250, 245)), 1)
    tr = nn.nodes.new('ShaderNodeBsdfTransparent'); ad = nn.nodes.new('ShaderNodeAddShader'); nn.links.new(tr.outputs[0], ad.inputs[0]); nn.links.new(em.outputs[0], ad.inputs[1])
    tcn = nn.nodes.new('ShaderNodeTexCoord'); spn = nn.nodes.new('ShaderNodeSeparateXYZ'); nn.links.new(tcn.outputs['UV'], spn.inputs[0])
    gx = nn.nodes.new('ShaderNodeMath'); gx.operation = 'SINE'; mxx = nn.nodes.new('ShaderNodeMath'); mxx.operation = 'MULTIPLY'; mxx.inputs[1].default_value = math.pi
    nn.links.new(spn.outputs['X'], mxx.inputs[0]); nn.links.new(mxx.outputs[0], gx.inputs[0])
    gy = nn.nodes.new('ShaderNodeMath'); gy.operation = 'POWER'; gy.inputs[1].default_value = 1.6; nn.links.new(spn.outputs['Y'], gy.inputs[0])
    mm1 = nn.nodes.new('ShaderNodeMath'); mm1.operation = 'MULTIPLY'; nn.links.new(gx.outputs[0], mm1.inputs[0]); nn.links.new(gy.outputs[0], mm1.inputs[1])
    mm2 = nn.nodes.new('ShaderNodeMath'); mm2.operation = 'MULTIPLY'; mm2.inputs[1].default_value = R.uniform(1.2, 2.0); nn.links.new(mm1.outputs[0], mm2.inputs[0])
    nn.links.new(mm2.outputs[0], em.inputs['Strength']); nn.links.new(ad.outputs[0], out.inputs[0]); m.surface_render_method = 'BLENDED'
    o.data.materials.append(m); o.visible_shadow = False
    for f in (1, NF):
        o.location.x = -1.4 + i * 0.75 + 0.15 * math.sin(i + f / FPS * 0.5); o.keyframe_insert('location', index=0, frame=f)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (*TEAL, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 0.7
# 6) particulas en suspension (como MOTES): puntitos finos que derivan
R = random.Random(9)
m_part = emit_mat('particula', lin((235, 248, 250)), 0.6)
pm_ = bpy.data.meshes.new('motas'); pb = bmesh.new()
for i in range(900):
    c = Vector((R.uniform(-2.4, 2.4), R.uniform(-1.6, 2.6), R.uniform(-1.3, 1.4))); r = R.uniform(0.0015, 0.005)
    bmesh.ops.create_icosphere(pb, subdivisions=1, radius=r, matrix=Matrix.Translation(c))
pb.to_mesh(pm_); motes = bpy.data.objects.new('MOTAS', pm_); sc.collection.objects.link(motes); motes.data.materials.append(m_part)
motes.keyframe_insert('location', frame=1); motes.location = (0.08, 0.0, 0.10); motes.keyframe_insert('location', frame=NF)
# ------------------------------------------------------------------ burbujas de aire reales + burbuja de dialogo (aire que se infla, lista para texto)
# Se renderizan en una capa propia ('burbujas', con el fry como recorte) y se suman despues de la niebla: la niebla de
# profundidad no sabe de objetos transparentes y las borraba.
bpy.context.view_layer.update()
def air_mat(name, rim_em=1.1, method='BLENDED'):
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree; n.nodes.clear()
    out = n.nodes.new('ShaderNodeOutputMaterial'); lw = n.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.2
    pw = n.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; n.links.new(lw.outputs['Facing'], pw.inputs[0]); pw.inputs[1].default_value = 2.4
    gl = n.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.03; gl.inputs['Color'].default_value = (1, 1, 1, 1)
    emr = n.nodes.new('ShaderNodeEmission'); emr.inputs['Color'].default_value = (*lin((210, 248, 255)), 1); emr.inputs['Strength'].default_value = rim_em
    ad = n.nodes.new('ShaderNodeAddShader'); n.links.new(gl.outputs[0], ad.inputs[0]); n.links.new(emr.outputs[0], ad.inputs[1])
    tr = n.nodes.new('ShaderNodeBsdfTransparent'); mx = n.nodes.new('ShaderNodeMixShader')
    fac = n.nodes.new('ShaderNodeMath'); fac.operation = 'MULTIPLY_ADD'; n.links.new(pw.outputs[0], fac.inputs[0]); fac.inputs[1].default_value = 0.9; fac.inputs[2].default_value = 0.05
    n.links.new(fac.outputs[0], mx.inputs['Fac']); n.links.new(tr.outputs[0], mx.inputs[1]); n.links.new(ad.outputs[0], mx.inputs[2]); n.links.new(mx.outputs[0], out.inputs[0])
    m.surface_render_method = method; m.use_backface_culling = True; return m
m_air = air_mat('aire', 1.6); m_air_far = air_mat('aire_lejos', 0.6, 'DITHERED')
m_hlb = bpy.data.materials.new('brillo_burbuja'); m_hlb.use_nodes = True; n = m_hlb.node_tree; n.nodes.clear()
out = n.nodes.new('ShaderNodeOutputMaterial'); em = n.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 3.0
n.links.new(em.outputs[0], out.inputs[0]); m_hlb.surface_render_method = 'BLENDED'
def bubble(name, r, mat_=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=48, ring_count=24); o = bpy.context.object; o.name = name
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(mat_ or m_air); return o
def highlights(parent, k=1.0):                                                   # reflejo de "ventana" arriba a la izquierda + puntito abajo
    for nm, loc, sc_, rz in (('a', (-0.42, -0.86, 0.44), (0.2, 0.05, 0.07), 0.75), ('b', (0.47, -0.84, -0.42), (0.05, 0.03, 0.05), 0.0)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=24, ring_count=12); h = bpy.context.object; h.name = f'{parent.name}_brillo_{nm}'
        h.parent = parent; h.location = loc; h.scale = tuple(v * k for v in sc_); h.rotation_euler = (0, -rz, 0); h.data.materials.append(m_hlb)
        for p in h.data.polygons: p.use_smooth = True
def mouth_world(f):                                                              # boca en el mundo en ese frame (la cabeza casi no ondula)
    sc.frame_set(f); return rig.matrix_world @ Vector((MX + 0.02, 0, MZ))
def ez(t): t = min(max(t, 0.0), 1.0); return 1 - (1 - t) ** 3
for i, (f0, r) in enumerate(((60, 0.014), (64, 0.009), (67, 0.017), (71, 0.008), (74, 0.012))):   # burbujitas que suelta por la boca y suben
    p0 = mouth_world(f0); o = bubble(f'AIRE_{i}', r)
    o.scale = (0, 0, 0); o.location = p0; o.keyframe_insert('scale', frame=f0 - 1); o.keyframe_insert('location', frame=f0 - 1)
    for f in range(f0, NF + 1, 2):
        t = (f - f0) / FPS; o.location = p0 + Vector((0.025 * math.sin(t * 9 + i) + 0.05 * t, -0.02, 0.2 * t + 0.1 * t * t))
        s = min(1.0, (f - f0) / 3.0); w_ = 0.07 * math.sin(t * 22 + i); o.scale = (s * (1 + w_), s, s * (1 - w_))
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
for i in range(14):                                                             # hilo de burbujas lejano (queda en la capa con niebla)
    o = bubble(f'AIREFONDO_{i}', R.uniform(0.006, 0.016), m_air_far); x0 = 1.15 + R.uniform(-0.05, 0.05); y0 = 1.4; ph_ = R.uniform(0, 10)
    for f in range(1, NF + 1, 3):
        z = -1.3 + ((f / FPS * 0.45 + i / 14 * 2.6) % 2.6); o.location = (x0 + 0.02 * math.sin(f / FPS * 7 + ph_), y0, z); o.keyframe_insert('location', frame=f)
# burbuja de dialogo: sale de la boca como burbujita, se infla mientras sube y queda temblando arriba a la derecha.
# Por dentro un velo blanco suave (mas opaco en el centro) para que el texto se lea; borde y reflejos de burbuja real.
sc.frame_set(100); HEAD = rig.matrix_world @ Vector((0.40, 0, 0.085))              # arriba de la cabeza, en la pose final (mirando hacia arriba)
BIG = HEAD + Vector((0.42, -0.02, 0.17)); RBIG = 0.15                              # globo arriba a la derecha, en el plano de foco
_d = (BIG - HEAD); EDGE = BIG - _d.normalized() * RBIG * 1.12                      # borde del globo que mira a la cabeza
TRAIL = [(HEAD.lerp(EDGE, t), r) for t, r in ((0.16, 0.013), (0.44, 0.02), (0.74, 0.03))]   # de menor a mayor, en linea y sin tocarse
def head_world(f):
    sc.frame_set(f); return rig.matrix_world @ Vector((0.40, 0, 0.085))
def dialog(name, f0, f1, p_end, r_end, veil=True, wob=0.03):
    ctl = bpy.data.objects.new(name, None); sc.collection.objects.link(ctl)
    shell = bubble(f'{name}_cascara', 1.0); shell.parent = ctl; highlights(shell)
    if veil:                                                                     # velo para el texto: disco que mira a camara, detras del centro
        vm_ = bpy.data.meshes.new(f'{name}_velo'); vb_ = bmesh.new()
        bmesh.ops.create_circle(vb_, cap_ends=True, segments=64, radius=0.9); vb_.to_mesh(vm_)
        vo_ = bpy.data.objects.new(f'{name}_velo', vm_); sc.collection.objects.link(vo_); vo_.parent = ctl
        vo_.rotation_euler = (math.radians(90), 0, 0); vo_.location = (0, 0.12, 0)
        mv_ = bpy.data.materials.new(f'{name}_velo'); mv_.use_nodes = True; n = mv_.node_tree; n.nodes.clear()
        out = n.nodes.new('ShaderNodeOutputMaterial'); em = n.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*lin((236, 248, 252)), 1)
        em.inputs['Strength'].default_value = 0.9; tr = n.nodes.new('ShaderNodeBsdfTransparent'); mx = n.nodes.new('ShaderNodeMixShader')
        tc = n.nodes.new('ShaderNodeTexCoord'); vl = n.nodes.new('ShaderNodeVectorMath'); vl.operation = 'LENGTH'; n.links.new(tc.outputs['Object'], vl.inputs[0])
        mr = n.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; mr.inputs['From Min'].default_value = 0.45; mr.inputs['From Max'].default_value = 0.9
        mr.inputs['To Min'].default_value = 0.72; mr.inputs['To Max'].default_value = 0.0; n.links.new(vl.outputs['Value'], mr.inputs['Value'])
        n.links.new(mr.outputs[0], mx.inputs['Fac']); n.links.new(tr.outputs[0], mx.inputs[1]); n.links.new(em.outputs[0], mx.inputs[2]); n.links.new(mx.outputs[0], out.inputs[0])
        mv_.surface_render_method = 'BLENDED'; vo_.data.materials.append(mv_)
    p0 = head_world(f0); ctl.scale = (0, 0, 0); ctl.location = p0; ctl.keyframe_insert('scale', frame=f0 - 1); ctl.keyframe_insert('location', frame=f0 - 1)
    for f in range(f0, NF + 1):
        t = (f - f0) / max(1, f1 - f0); k = ez(t); tt = (f - f0) / FPS
        arc = Vector((0, 0, 0.06 * math.sin(math.pi * min(t, 1))))                # sube en arco
        loc = p0.lerp(p_end, k) + arc * (1 - k) + Vector((0.004 * math.sin(tt * 2.2), 0, 0.007 * math.sin(tt * 1.7)))
        r_ = 0.012 + (r_end - 0.012) * k + r_end * 0.08 * math.sin(math.pi * min(max((f - f1 + 4) / 8, 0), 1))   # pequeno rebote al llegar
        w_ = wob * math.sin(tt * 24) * math.exp(-max(0, f - f1) / 18) + 0.012 * math.sin(tt * 7)
        ctl.location = loc; ctl.scale = (r_ * (1 + w_), r_ * 0.94, r_ * (1 - w_))
        ctl.keyframe_insert('location', frame=f); ctl.keyframe_insert('scale', frame=f)
    return ctl
for i, (p_, r_) in enumerate(TRAIL): dialog(f'PENSAMIENTO_burbuja{i}', 78 + 4 * i, 88 + 4 * i, p_, r_, veil=False, wob=0.05)
dialog('PENSAMIENTO_globo', 88, 106, BIG, RBIG)
# ------------------------------------------------------------------ luz (sol nitido e inclinado, como en el film), camara, render
sun = bpy.data.objects.new('SOL', bpy.data.lights.new('SOL', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 5.0; sun.data.color = (1.0, 0.95, 0.85); sun.data.angle = math.radians(3)
sun.rotation_euler = (math.radians(22), math.radians(-16), 0)
rim = bpy.data.objects.new('CONTRALUZ', bpy.data.lights.new('CONTRALUZ', 'SUN')); sc.collection.objects.link(rim)   # luz de contorno desde atras
rim.data.energy = 3.5; rim.data.color = (0.8, 0.97, 1.0)
bnc = bpy.data.objects.new('REBOTE_ARENA', bpy.data.lights.new('REBOTE_ARENA', 'AREA')); sc.collection.objects.link(bnc)   # rebote calido de la arena en la panza
bnc.data.energy = 90; bnc.data.size = 5; bnc.data.color = (1.0, 0.9, 0.72); bnc.location = (0, 0.2, -0.55); bnc.rotation_euler = (math.radians(180), 0, 0)
rim.rotation_euler = (math.radians(-60), 0, math.radians(15)); rim.data.volume_factor = 0.0
try: sun.data.volume_factor = 1.0
except Exception: pass
fill = bpy.data.objects.new('UW_FILL', bpy.data.lights.new('UW_FILL', 'SUN')); sc.collection.objects.link(fill)
fill.data.energy = 1.6; fill.data.color = (0.75, 0.95, 0.95); fill.rotation_euler = (math.radians(110), 0, math.radians(-20)); fill.data.volume_factor = 0.0
cam = bpy.data.objects.new('CAM', bpy.data.cameras.new('CAM')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 50; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8
for f, y, x in ((1, -2.5, 0.0), (NF, -2.2, 0.04)):
    cam.location = (x, y, 0.2); cam.rotation_euler = (math.radians(86), 0, 0); cam.keyframe_insert('location', frame=f)
cam.data.dof.focus_distance = 2.22
sc.render.engine = 'BLENDER_EEVEE_NEXT'; ee = sc.eevee; ee.taa_render_samples = SPP
ee.use_volumetric_shadows = True; ee.volumetric_tile_size = '4'; ee.volumetric_samples = 64; ee.volumetric_end = 14.0; ee.volumetric_shadow_samples = 16
try: ee.use_shadows = True; ee.shadow_ray_count = 2; ee.shadow_step_count = 8
except Exception: pass
sc.render.resolution_x = RW; sc.render.resolution_y = int(RW * 9 / 16)
try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: sc.view_settings.view_transform = 'Standard'
sc.view_settings.exposure = 0.0
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
sc.render.image_settings.file_format = 'PNG'
# niebla de agua en composicion (reemplaza al volumen): cuanto mas lejos, mas color de agua; mas claro hacia arriba (luz de superficie)
# capas: 'escena' (todo menos las burbujas, con niebla de agua) + 'burbujas' (burbujas cercanas; el fry las tapa como recorte)
cols = {k: bpy.data.collections.new(k) for k in ('ENTORNO', 'FRY', 'BURBUJAS', 'LUCES')}
for c in cols.values(): sc.collection.children.link(c)
for o in list(sc.collection.objects):
    k = ('BURBUJAS' if o.name.startswith(('AIRE_', 'PENSAMIENTO')) else 'FRY' if o.name.startswith('FRY_') else
         'LUCES' if o.type in ('LIGHT', 'CAMERA') else 'ENTORNO')
    cols[k].objects.link(o); sc.collection.objects.unlink(o)
vl_esc = sc.view_layers[0]; vl_esc.name = 'escena'; vl_bub = sc.view_layers.new('burbujas')
vl_esc.layer_collection.children['BURBUJAS'].exclude = True
vl_bub.layer_collection.children['ENTORNO'].exclude = True; vl_bub.layer_collection.children['FRY'].holdout = True
sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGB'
if not VOLUMEN:
    vl_esc.use_pass_mist = True; w.mist_settings.start = 0.8; w.mist_settings.depth = 8.0; w.mist_settings.falloff = 'QUADRATIC'
    sc.use_nodes = True; cn = sc.node_tree; cn.nodes.clear()
    rl = cn.nodes.new('CompositorNodeRLayers'); rl.layer = 'escena'; rb = cn.nodes.new('CompositorNodeRLayers'); rb.layer = 'burbujas'
    co = cn.nodes.new('CompositorNodeComposite')
    mx = cn.nodes.new('CompositorNodeMixRGB'); mx.blend_type = 'MIX'; mx.inputs[2].default_value = (*lin((52, 165, 200)), 1)
    cn.links.new(rl.outputs['Mist'], mx.inputs[0]); cn.links.new(rl.outputs['Image'], mx.inputs[1])
    # brillo de la superficie arriba: mezcla aditiva de una franja clara (mascara de caja difusa)
    bx = cn.nodes.new('CompositorNodeBoxMask'); bx.x = 0.5; bx.y = 1.05; bx.width = 1.6; bx.height = 0.7
    bl = cn.nodes.new('CompositorNodeBlur'); bl.size_x = bl.size_y = int(RW * 0.12); bl.use_relative = False
    cn.links.new(bx.outputs[0], bl.inputs[0])
    sk = cn.nodes.new('CompositorNodeMixRGB'); sk.blend_type = 'SCREEN'; sk.inputs[2].default_value = (*lin((190, 240, 245)), 1)
    mk = cn.nodes.new('CompositorNodeMath'); mk.operation = 'MULTIPLY'; mk.inputs[1].default_value = 0.55
    cn.links.new(bl.outputs[0], mk.inputs[0]); cn.links.new(mk.outputs[0], sk.inputs[0]); cn.links.new(mx.outputs[0], sk.inputs[1])
    ao = cn.nodes.new('CompositorNodeAlphaOver'); cn.links.new(sk.outputs[0], ao.inputs[1]); cn.links.new(rb.outputs['Image'], ao.inputs[2])
    gl = cn.nodes.new('CompositorNodeGlare'); gl.glare_type = 'FOG_GLOW'; gl.threshold = 1.0; gl.size = 7; gl.mix = -0.75   # brillo suave
    cn.links.new(ao.outputs[0], gl.inputs[0]); cn.links.new(gl.outputs[0], co.inputs[0])
CLOSE = '--cerca' in argv                                                         # camara de primer plano a la cabeza (para revisar ojos/parpados)
if SAVE: bpy.ops.wm.save_as_mainfile(filepath=SAVE)
a, b = (int(v) for v in FR.split('-'))
for f in range(a, b + 1):
    sc.frame_set(f)
    if CLOSE:
        hp = rig.matrix_world @ Vector((0.36, 0, 0.0)); cam.animation_data_clear(); cam.location = hp + Vector((0.05, -0.75, 0.04))
        cam.rotation_euler = (math.radians(87), 0, 0); cam.data.dof.focus_distance = 0.72; cam.data.lens = 60
    sc.render.filepath = f'{OUT}/f_{f:04d}{"_cerca" if CLOSE else ""}.png'; bpy.ops.render.render(write_still=True)
print('FRY_DONE')
