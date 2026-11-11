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
FPS, NF = 25, 250                                                                # 10 s: globo ~2,6 s para leer, se expande hasta llenar la pantalla de blanco (titulo)
E0, E1 = 186, 214                                                               # expansion final del globo (frames reales); blanco total desde E1
TS = 1.2                                                                         # la actuacion se estira x1.2 (mas tiempo para la duda)
def FT(x): return int(round(1 + (x - 1) * TS))                                   # frame de diseno (5 s) -> frame real (6 s)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def lin(c): return tuple(((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in c)
BRAND = lin((186, 229, 242))                                                     # celeste del icono
NAVY = lin((18, 52, 96))
# ------------------------------------------------------------------ silueta del icono -> 3D (1 unidad = largo del fry)
shapes = json.load(open(SIL))
X0, X1 = shapes[4]['bbox'][0], shapes[4]['bbox'][2]; S = 1 / (X1 - X0); XC = (X0 + X1) / 2; YC = 566.0
outer = max(shapes[4]['subpaths'], key=len)
def section(x):                                                                  # arriba / abajo del contorno en esa x
    ys = []
    n = len(outer)
    for i in range(n):
        (xa, ya), (xb, yb) = outer[i], outer[(i + 1) % n]
        if (xa - x) * (xb - x) <= 0 and xa != xb: ys.append(ya + (yb - ya) * (x - xa) / (xb - xa))
    return (min(ys), max(ys)) if len(ys) >= 2 else None
# ---- forma 3D: perfil del icono suavizado y con menos contraste cabeza/cuerpo (huso redondeado, sin cabeza de bulbo)
NS, M = 200, 72                                                                  # mucha resolucion: sin anillos ni facetas
_us, _zc, _h = [], [], []
for k in range(NS + 1):
    u = k / NS; x = X0 + 1.2 + u * (X1 - X0 - 2.4); sct = section(x)
    if sct is None: continue
    zt, zb = -(sct[0] - YC) * S, -(sct[1] - YC) * S; _us.append(u); _zc.append((zt + zb) / 2); _h.append((zt - zb) / 2)
def _smooth(a, k=4):
    return [sum(a[max(0, i - k):i + k + 1]) / len(a[max(0, i - k):i + k + 1]) for i in range(len(a))]
_zcs = _smooth(_smooth(_zc, 10), 10); _hs = _smooth(_h, 4)                             # linea media muy suave
# perfil de alto disenado (media altura, unidades de modelo): pedunculo fino -> cuerpo lleno -> cabeza redondeada integrada
_HCP = [(0.0, 0.030), (0.10, 0.030), (0.16, 0.034), (0.30, 0.056), (0.48, 0.074), (0.64, 0.090), (0.78, 0.104), (0.88, 0.106), (0.94, 0.095), (0.985, 0.060), (1.0, 0.03)]
def _hprof(u):                                                                   # Catmull-Rom por los puntos de control: curva continua y suave
    P_ = [_HCP[0]] + _HCP + [_HCP[-1]]
    for i in range(1, len(P_) - 2):
        (u0, h0), (u1, h1), (u2, h2), (u3, h3) = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        if u1 <= u <= u2:
            t = (u - u1) / max(u2 - u1, 1e-6)
            m1 = (h2 - h0) / max(u2 - u0, 1e-6) * (u2 - u1); m2 = (h3 - h1) / max(u3 - u1, 1e-6) * (u2 - u1)
            return (2 * t ** 3 - 3 * t * t + 1) * h1 + (t ** 3 - 2 * t * t + t) * m1 + (-2 * t ** 3 + 3 * t * t) * h2 + (t ** 3 - t * t) * m2
    return _HCP[-1][1]
_h3 = [_hprof(u) for u in _us]
def _interp(arr, u):
    if u <= _us[0]: return arr[0]
    if u >= _us[-1]: return arr[-1]
    for i in range(len(_us) - 1):
        if _us[i] <= u <= _us[i + 1]:
            t = (u - _us[i]) / (_us[i + 1] - _us[i]); return arr[i] * (1 - t) + arr[i + 1] * t
def P(x, y):                                                                     # artboard -> (X, Z) con la misma deformacion que el cuerpo
    u = (x - X0) / (X1 - X0); Z0 = -(y - YC) * S
    zr, zs, hr, h3 = _interp(_zc, u), _interp(_zcs, u), _interp(_h, u), _interp(_h3, u)
    return ((x - XC) * S, zs + (Z0 - zr) * (h3 / max(hr, 1e-4)))
def thick(u):                                                                    # medio ancho / media altura (vista de arriba: huso)
    t = min(max((u - 0.1) / 0.75, 0), 1); return 0.55 + 0.13 * t * t * (3 - 2 * t)   # sin quiebres
rings = []; ring_u = []
UT = 0.105                                                                       # el cuerpo empieza en el pedunculo; la cola en abanico es una aleta
for u, zc, h in zip(_us, _zcs, _h3):
    if u < UT: continue
    X = (X0 + 1.2 + u * (X1 - X0 - 2.4) - XC) * S; w = h * thick(u)
    if u > 0.93: f_ = (u - 0.93) / 0.07; w *= math.sqrt(max(0.0, 1 - 0.75 * f_ * f_))   # nariz redondeada
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
sub = body.modifiers.new('sub', 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
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
    sb = o.modifiers.new('sub', 'SUBSURF'); sb.levels = sb.render_levels = 2
    return o
# ---- aletas nuevas: abanicos con radios, pegadas al cuerpo (la base entra en la piel). Malla en abanico: cada fila va de la
#      base al borde, con atributo 'aleta' (u base->borde, v a lo largo de la base, w = v * radios) para el shader.
def _cr(pts, n):                                                                 # Catmull-Rom por puntos 2D y re-muestreo por largo de arco
    P_ = [pts[0]] + list(pts) + [pts[-1]]; dense = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = (Vector(P_[k]) for k in (i - 1, i, i + 1, i + 2))
        for k in range(16):
            t = k / 16; t2, t3 = t * t, t * t * t
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense.append(Vector(pts[-1])); L = [0.0]
    for a_, b_ in zip(dense[:-1], dense[1:]): L.append(L[-1] + (b_ - a_).length)
    out, j = [], 0
    for i in range(n):
        s = L[-1] * i / (n - 1)
        while j < len(L) - 2 and L[j + 1] < s: j += 1
        t = (s - L[j]) / max(L[j + 1] - L[j], 1e-9); out.append(dense[j].lerp(dense[j + 1], t))
    return out
def fan_fin(name, b0, b1, edge, rays, xf=None, th=0.0032, NV=56, NU=12):
    E = _cr([b0] + list(edge) + [b1], NV); m = bpy.data.meshes.new(name); bm_ = bmesh.new(); grid = []
    for i in range(NV):
        v = i / (NV - 1); B = Vector(b0).lerp(Vector(b1), v); row = []
        for k in range(NU):
            u = k / (NU - 1); p = B.lerp(E[i], u); co = Vector((p.x, 0.0, p.y))
            if xf: co = xf(co, u)
            row.append(bm_.verts.new(co))
        grid.append(row)
    for i in range(NV - 1):
        for k in range(NU - 1): bm_.faces.new((grid[i][k], grid[i][k + 1], grid[i + 1][k + 1], grid[i + 1][k]))
    bm_.to_mesh(m); o = bpy.data.objects.new(name, m); sc.collection.objects.link(o)
    at_ = m.attributes.new('aleta', 'FLOAT_VECTOR', 'POINT')
    for i in range(NV):
        for k in range(NU): at_.data[i * NU + k].vector = (k / (NU - 1), i / (NV - 1), (i / (NV - 1)) * rays if rays else 0.5)
    for p in m.polygons: p.use_smooth = True
    sol = o.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = th; sol.offset = 0
    sb = o.modifiers.new('sub', 'SUBSURF'); sb.levels = sb.render_levels = 1
    return o
def top(X): zm, hh = z_mid(X); return zm + hh
def bot(X): zm, hh = z_mid(X); return zm - hh
# dorsal: vela alta adelante y baja atras, en la mitad del lomo
dorsal = fan_fin('FRY_aleta_dorsal', (0.135, top(0.135) - 0.014), (-0.035, top(-0.035) - 0.012),
                 [(0.12, top(0.12) + 0.032), (0.095, top(0.095) + 0.068), (0.062, top(0.062) + 0.08), (0.022, top(0.022) + 0.062), (-0.025, top(-0.025) + 0.025)], 11)
adipose = fan_fin('FRY_aleta_adiposa', (-0.205, top(-0.205) - 0.010), (-0.275, top(-0.275) - 0.008),
                  [(-0.215, top(-0.215) + 0.022), (-0.24, top(-0.24) + 0.032), (-0.265, top(-0.265) + 0.02)], 0)
anal = fan_fin('FRY_aleta_anal', (-0.075, bot(-0.075) + 0.012), (-0.17, bot(-0.17) + 0.010),
               [(-0.085, bot(-0.085) - 0.035), (-0.105, bot(-0.105) - 0.055), (-0.14, bot(-0.14) - 0.047), (-0.172, bot(-0.172) - 0.017)], 9)
fins = [dorsal, adipose, anal]
for sgn in (-1, 1):                                                              # ventrales: pares, bajo la panza, abiertas hacia afuera
    X_ = 0.03; zm_, hh_ = z_mid(X_); hw_ = half_w(X_); yb_ = sgn * hw_ * 0.42; zb2 = zm_ - hh_ * 0.88
    th_ = sgn * math.radians(32)
    def xf(co, u, yb_=yb_, zb2=zb2, th_=th_):
        x, z = co.x, co.z - zb2; return Vector((x, yb_ - z * math.sin(th_), zb2 + z * math.cos(th_)))
    fins.append(fan_fin(f'FRY_aleta_ventral_{sgn}', (0.0, zb2 + 0.006), (0.065, zb2 + 0.006),
                        [(-0.02, zb2 - 0.036), (-0.01, zb2 - 0.056), (0.026, zb2 - 0.048), (0.05, zb2 - 0.008)], 8, xf))
# caudal en horquilla (dos lobulos redondeados), la base entra en el pedunculo
cx_ = -0.352; zb_ = z_mid(-0.39)[0]
caudal = fan_fin('FRY_aleta_caudal', (cx_, zb_ - 0.024), (cx_, zb_ + 0.024),
                 [(-0.395, zb_ - 0.045), (-0.455, zb_ - 0.085), (-0.505, zb_ - 0.102), (-0.525, zb_ - 0.088), (-0.51, zb_ - 0.048), (-0.49, zb_ - 0.011),
                  (-0.485, zb_), (-0.49, zb_ + 0.011), (-0.51, zb_ + 0.048), (-0.525, zb_ + 0.088), (-0.505, zb_ + 0.102), (-0.455, zb_ + 0.085), (-0.395, zb_ + 0.045)], 20, th=0.0036, NV=80)
# pectorales: abanico redondeado detras del operculo; pivote en la base (eje vertical local), aletean siempre hacia afuera
GX = P(1238, 560)[0]; PX = GX - 0.02
pects = []
for sgn in (-1, 1):
    zm_, hh_ = z_mid(PX); pz = zm_ - hh_ * 0.38; py = sgn * half_w(PX) * 0.86
    pe = fan_fin(f'FRY_aleta_pect_{sgn}', (0.0, -0.024), (0.0, 0.024),
                 [(-0.025, -0.028), (-0.07, -0.032), (-0.11, -0.02), (-0.12, 0.006), (-0.09, 0.03), (-0.04, 0.032)], 13, th=0.003)
    pe.location = (PX, py, pz); pe.rotation_mode = 'XYZ'; pects.append(pe)
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
    wa = nt.nodes.new('ShaderNodeVectorMath'); wa.operation = 'SCALE'; wa.inputs['Scale'].default_value = 0.16; nt.links.new(wn.outputs['Color'], wa.inputs[0])
    wp = nt.nodes.new('ShaderNodeVectorMath'); wp.operation = 'ADD'; nt.links.new(geo.outputs['Position'], wp.inputs[0]); nt.links.new(wa.outputs[0], wp.inputs[1])
    nt.links.new(wp.outputs[0], vo.inputs['Vector'])
    for f in (1, NF):
        vo.inputs['W'].default_value = f * 0.03; vo.inputs['W'].keyframe_insert('default_value', frame=f)
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.1
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
rmp = nt.nodes.new('ShaderNodeValToRGB'); rmp.color_ramp.interpolation = 'EASE'
el = rmp.color_ramp.elements; el[0].position = 0.0; el[0].color = (*lin((240, 246, 248)), 1); el[1].position = 1.0; el[1].color = (*lin((34, 76, 122)), 1)
for pos, c in ((0.40, (230, 240, 244)), (0.52, (176, 208, 228)), (0.66, (98, 150, 192)), (0.84, (52, 102, 150))): e = el.new(pos); e.color = (*lin(c), 1)
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
col = mixc(nt, M(nt, 'MULTIPLY', parr, 0.78), col, lin((40, 98, 120)))   # azul petroleo (entre el real y la cartoon)
# pintitas oscuras en el lomo y la parte alta del flanco
vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 1.0; vor.inputs['Randomness'].default_value = 0.9
vm = nt.nodes.new('ShaderNodeVectorMath'); vm.operation = 'MULTIPLY'; vm.inputs[1].default_value = (36.0, 6.0, 6.0)
nt.links.new(at.outputs['Vector'], vm.inputs[0]); nt.links.new(vm.outputs[0], vor.inputs['Vector'])
spots = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, vor.outputs['Distance'], 0.15, 0.22)),
          M(nt, 'MULTIPLY', smooth(nt, C, -0.25, 0.1), M(nt, 'MULTIPLY', smooth(nt, U, 0.12, 0.2), M(nt, 'SUBTRACT', 1.0, smooth(nt, U, 0.86, 0.93)))))
col = mixc(nt, M(nt, 'MULTIPLY', spots, 0.85), col, lin((38, 48, 54)))
# rosado suave en el flanco (mas hacia la cola) y borde del operculo
pink = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, lat, 0.1, 0.4)), M(nt, 'SUBTRACT', 1.0, smooth(nt, U, 0.35, 0.8)))
col = mixc(nt, M(nt, 'MULTIPLY', pink, 0.32), col, lin((246, 176, 168)))            # rubor calido en el flanco (como el fry real)
oper = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, M(nt, 'ABSOLUTE', M(nt, 'SUBTRACT', M(nt, 'SUBTRACT', U, M(nt, 'MULTIPLY', M(nt, 'MULTIPLY', C, C), 0.025)), 0.80)), 0.003, 0.008)),
         M(nt, 'SUBTRACT', 1.0, smooth(nt, M(nt, 'ABSOLUTE', C), 0.6, 0.8)))
col = mixc(nt, M(nt, 'MULTIPLY', oper, 0.55), col, lin((60, 80, 88)))
nt.links.new(col, bs.inputs['Base Color'])
bs.inputs['Metallic'].default_value = 0.06; bs.inputs['Roughness'].default_value = 0.52; bs.inputs['Specular IOR Level'].default_value = 0.3
bs.inputs['Coat Weight'].default_value = 0.08; bs.inputs['Coat Roughness'].default_value = 0.35
bs.inputs['Thin Film Thickness'].default_value = 0.0; bs.inputs['Thin Film IOR'].default_value = 1.5
bs.inputs['Subsurface Weight'].default_value = 0.15; bs.inputs['Subsurface Radius'].default_value = (0.04, 0.06, 0.07)
bs.inputs['Emission Color'].default_value = (*lin((255, 236, 180)), 1); nt.links.new(caustic(nt, 0.28), bs.inputs['Emission Strength'])
# escamas finas (relieve) y plateado que destella en el flanco cuando gira (como el salmon)
vsc = nt.nodes.new('ShaderNodeTexVoronoi'); vsc.inputs['Scale'].default_value = 1.0; vmul = nt.nodes.new('ShaderNodeVectorMath'); vmul.operation = 'MULTIPLY'
vmul.inputs[1].default_value = (140.0, 22.0, 22.0); nt.links.new(at.outputs['Vector'], vmul.inputs[0]); nt.links.new(vmul.outputs[0], vsc.inputs['Vector'])
bsc = nt.nodes.new('ShaderNodeBump'); bsc.inputs['Strength'].default_value = 0.12; bsc.inputs['Distance'].default_value = 0.002
nt.links.new(vsc.outputs['Distance'], bsc.inputs['Height']); nt.links.new(bsc.outputs['Normal'], bs.inputs['Normal'])
nt.links.new(M(nt, 'MULTIPLY_ADD', M(nt, 'SUBTRACT', 1.0, smooth(nt, M(nt, 'ABSOLUTE', C), 0.3, 0.75)), 0.12), bs.inputs['Metallic']); nt.nodes[-1].inputs[2].default_value = 0.08
body.data.materials.append(m_body)
# aletas: abanico opaco (no parpadea) con radios marcados, de plateado en la base a ambar calido en el borde, borde claro;
#          algo de luz que las atraviesa (translucido) para que brillen a contraluz
m_fin = bpy.data.materials.new('aletas_fry'); m_fin.use_nodes = True; nt = m_fin.node_tree; bs = nt.nodes['Principled BSDF']
afa = nt.nodes.new('ShaderNodeAttribute'); afa.attribute_name = 'aleta'; asp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(afa.outputs['Vector'], asp.inputs[0])
FU, FW = asp.outputs[0], asp.outputs[2]
line = M(nt, 'SUBTRACT', 1.0, smooth(nt, M(nt, 'ABSOLUTE', M(nt, 'SINE', M(nt, 'MULTIPLY', FW, math.pi))), 0.06, 0.4))
fcol = mixc(nt, smooth(nt, FU, 0.05, 0.9), lin((170, 206, 230)), lin((214, 234, 246)))   # celeste translucido (cartoon / real)
fcol = mixc(nt, M(nt, 'MULTIPLY', line, M(nt, 'MULTIPLY', smooth(nt, FU, 0.06, 0.3), 0.6)), fcol, lin((96, 150, 194)))   # radios
fcol = mixc(nt, M(nt, 'MULTIPLY', smooth(nt, FU, 0.86, 1.0), 0.7), fcol, lin((246, 251, 255)))
nt.links.new(fcol, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.42
bs.inputs['Subsurface Weight'].default_value = 0.25; bs.inputs['Subsurface Radius'].default_value = (0.01, 0.006, 0.004)
bs.inputs['Coat Weight'].default_value = 0.3; bs.inputs['Coat Roughness'].default_value = 0.2
fb = nt.nodes.new('ShaderNodeBump'); fb.inputs['Strength'].default_value = 0.25; fb.inputs['Distance'].default_value = 0.001
nt.links.new(line, fb.inputs['Height']); nt.links.new(fb.outputs['Normal'], bs.inputs['Normal'])
trl = nt.nodes.new('ShaderNodeBsdfTranslucent'); nt.links.new(fcol, trl.inputs['Color'])
fmx = nt.nodes.new('ShaderNodeMixShader'); fmx.inputs['Fac'].default_value = 0.45
nt.links.new(bs.outputs[0], fmx.inputs[1]); nt.links.new(trl.outputs[0], fmx.inputs[2])
fal = M(nt, 'MAXIMUM', M(nt, 'SUBTRACT', 0.88, M(nt, 'MULTIPLY', smooth(nt, FU, 0.1, 0.95), 0.3)), M(nt, 'MULTIPLY', line, 0.92))   # translucida: 0.88 base -> 0.58 borde, radios mas solidos
ftr = nt.nodes.new('ShaderNodeBsdfTransparent'); fm2 = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(fal, fm2.inputs['Fac'])
nt.links.new(ftr.outputs[0], fm2.inputs[1]); nt.links.new(fmx.outputs[0], fm2.inputs[2])
nt.links.new(fm2.outputs[0], nt.nodes['Material Output'].inputs['Surface']); m_fin.surface_render_method = 'DITHERED'
for f in fins + [caudal] + pects: f.data.materials.append(m_fin)
# ojo real: iris plateado-dorado con estrias, pupila negra grande y brillante, brillo puntual
m_white = bpy.data.materials.new('iris'); m_white.use_nodes = True; nt = m_white.node_tree; bs = nt.nodes['Principled BSDF']
noi = N(nt, 'ShaderNodeTexNoise', Scale=40.0, Detail=2.0)
bs.inputs['Metallic'].default_value = 0.25; bs.inputs['Roughness'].default_value = 0.3
nt.links.new(mixc(nt, noi.outputs['Fac'], lin((236, 240, 244)), lin((252, 253, 255))), bs.inputs['Base Color'])   # blanco del ojo (cartoon)
bs.inputs['Coat Weight'].default_value = 1.0; bs.inputs['Coat Roughness'].default_value = 0.02
m_navy = mat('pupila', (0.004, 0.005, 0.006), 0.05); m_navy.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 1.0
m_hl = mat('brillo', (1, 1, 1), 0.1, emit=6)
m_iris = mat('iris_azul', lin((26, 58, 112)), 0.15); m_iris.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 1.0
m_brow = mat('ceja', lin((44, 58, 62)), 0.4)
m_lid = bpy.data.materials.new('parpado'); m_lid.use_nodes = True; nt = m_lid.node_tree; bs = nt.nodes['Principled BSDF']   # piel mate (no vidrio)
ltc = nt.nodes.new('ShaderNodeTexCoord'); lsp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(ltc.outputs['Object'], lsp.inputs[0])
lz = M(nt, 'ABSOLUTE', lsp.outputs['Z'])                                        # borde del parpado (z local ~ 0): linea de pestanas oscura
cl2 = nt.nodes.new('ShaderNodeMix'); cl2.data_type = 'RGBA'; nt.links.new(smooth(nt, lz, 0.004, 0.012), cl2.inputs[0])
cl2.inputs[6].default_value = (*lin((22, 40, 70)), 1); cl2.inputs[7].default_value = (*lin((150, 186, 210)), 1); nt.links.new(cl2.outputs[2], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.62; bs.inputs['Specular IOR Level'].default_value = 0.25
# ------------------------------------------------------------------ cara: ojos, ceja, boca (sobre el ojo y la boca del icono)
EX, EZ = P(1292, 552); ER = 0.054
eyes = []
for sgn in (-1, 1):
    yb = sgn * half_w(EX) * 0.58                                                  # ojo mas metido en la cabeza (no de insecto)
    piv = bpy.data.objects.new(f'FRY_ojo_piv_{sgn}', None); sc.collection.objects.link(piv); piv.location = (EX, yb, EZ)
    ctl = bpy.data.objects.new(f'FRY_ojo_ctl_{sgn}', None); sc.collection.objects.link(ctl); ctl.parent = piv   # mirada + parpadeo
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER, location=(0, 0, 0), segments=64, ring_count=32); ball = bpy.context.object
    ball.name = f'FRY_ojo_{sgn}'; ball.data.materials.append(m_white); ball.parent = ctl
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.6, location=(0.004, sgn * ER * 0.74, 0.004), segments=48, ring_count=24); iri = bpy.context.object
    iri.scale.y = 0.5; iri.data.materials.append(m_iris); iri.parent = ctl; iri.name = f'FRY_iris_{sgn}'                # iris azul marino grande
    for p in iri.data.polygons: p.use_smooth = True
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.33, location=(0.004, sgn * ER * 0.89, 0.004), segments=32, ring_count=16); pup = bpy.context.object
    pup.scale.y = 0.5; pup.data.materials.append(m_navy); pup.parent = ctl; pup.name = f'FRY_pupila_{sgn}'
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.14, location=(0.016, sgn * ER * 1.06, 0.022)); hl = bpy.context.object
    hl.data.materials.append(m_hl); hl.parent = ctl; hl.name = f'FRY_brillo_{sgn}'
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ER * 0.065, location=(-0.012, sgn * ER * 1.05, -0.014)); hl2 = bpy.context.object
    hl2.data.materials.append(m_hl); hl2.parent = ctl; hl2.name = f'FRY_brillo2_{sgn}'
    # parpado superior: media cascara del color del cuerpo; girando en X baja/sube (expresion)
    lm = bpy.data.meshes.new(f'parpado_{sgn}'); lb = bmesh.new()
    bmesh.ops.create_uvsphere(lb, u_segments=64, v_segments=32, radius=ER * 1.08)
    bmesh.ops.delete(lb, geom=[v for v in lb.verts if v.co.z < -0.001], context='VERTS'); lb.to_mesh(lm)
    lid = bpy.data.objects.new(f'FRY_parpado_{sgn}', lm); sc.collection.objects.link(lid); lid.parent = piv; lid.data.materials.append(m_lid)
    so_ = lid.modifiers.new('grosor', 'SOLIDIFY'); so_.thickness = ER * 0.12; so_.offset = 1; lid.modifiers.new('suave', 'SUBSURF').render_levels = 2
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
    lm2 = bpy.data.meshes.new(f'parpado_inf_{sgn}'); lb2 = bmesh.new()               # parpado de abajo (sube en la duda / al sonreir con los ojos)
    bmesh.ops.create_uvsphere(lb2, u_segments=64, v_segments=32, radius=ER * 1.07)
    bmesh.ops.delete(lb2, geom=[v for v in lb2.verts if v.co.z > 0.001], context='VERTS'); lb2.to_mesh(lm2)
    lid2 = bpy.data.objects.new(f'FRY_parpado_inf_{sgn}', lm2); sc.collection.objects.link(lid2); lid2.parent = piv; lid2.data.materials.append(m_lid)
    so2 = lid2.modifiers.new('grosor', 'SOLIDIFY'); so2.thickness = ER * 0.1; so2.offset = 1; lid2.rotation_mode = 'XYZ'; lid2.modifiers.new('suave', 'SUBSURF').render_levels = 2
    for p in lm2.polygons: p.use_smooth = True
    eyes.append((piv, brow, ctl, lid, lid2))
# ---- boca 3D: labios con volumen (dos tubos que se separan) y el interior oscuro con lengua, apoyados sobre la punta del hocico.
#      Formas (shape keys): 'abre' (habla), 'o' (redonda: sopla burbujas), 'sonrie' (comisuras arriba), 'duda' (torcida a un lado).
from mathutils.bvhtree import BVHTree
_xn = rings[-1][0][0]; MX = _xn - 0.03; _zm, _hm = z_mid(MX - 0.02); MZ = _zm - 0.42 * _hm   # boca adelante y abajo del hocico
bpy.context.view_layer.update(); _dg = bpy.context.evaluated_depsgraph_get(); _bvh = BVHTree.FromObject(body, _dg)
def on_skin(phi, z):                                                             # la boca envuelve la punta del hocico: rayo radial hacia el eje
    d_ = Vector((math.cos(phi), math.sin(phi), 0.0)); o_ = Vector((MX - 0.06, 0.0, z)) + d_ * 1.0
    hit = _bvh.ray_cast(o_, -d_)
    if not hit[0]: return Vector((MX, 0, z)), Vector((1, 0, 0))
    n_ = hit[1].normalized(); return hit[0], (n_ if n_.dot(d_) > 0 else -n_)          # normal siempre hacia afuera
MW, MCZ, NS_, NR_ = math.radians(66), MZ + 0.0, 48, 9
def mouth_pts(op=0.0, sm=0.0, sk=0.0, rnd=0.0):
    w_ = MW * (1 - 0.45 * rnd); inner, up_, lo_ = [], [], []
    for i in range(NS_):
        s = -1 + 2 * i / (NS_ - 1); y = s * w_; env = (1 - s * s) ** 0.6
        zc = MCZ + 0.010 * sm * s * s - 0.004 * sm + 0.010 * sk * s - 0.006 * s * s * (1 - sm)   # curva de la boca (algo triste por defecto -> neutra)
        h = (0.0016 + op * 0.05 + rnd * 0.034) * (env if rnd < 0.5 else (1 - s * s) ** 0.45)
        col_ = []
        for r in range(NR_):
            rr = -1 + 2 * r / (NR_ - 1); p_, n_ = on_skin(y, zc + rr * h * 0.5); col_.append(p_ + n_ * 0.005)
        inner.append(col_)
        pu, nu = on_skin(y, zc + h * 0.5); pl, nl = on_skin(y, zc - h * 0.5); up_.append((pu, nu, s)); lo_.append((pl, nl, s))
    return inner, up_, lo_
def lips_geo(edge, rad=0.0034, nr=10):
    rings_ = []
    for i, (p_, n_, s) in enumerate(edge):
        a_ = edge[max(i - 1, 0)][0]; b_ = edge[min(i + 1, len(edge) - 1)][0]; T = (b_ - a_).normalized(); Bn = T.cross(n_).normalized()
        r_ = rad * (0.35 + 0.65 * (1 - abs(s) ** 3)); c_ = p_ + n_ * r_ * 0.45
        rings_.append([c_ + (n_ * math.cos(2 * math.pi * k / nr) + Bn * math.sin(2 * math.pi * k / nr)) * r_ for k in range(nr)])
    return rings_
def build_mouth(name, poses, mat_, kind):
    geo = [mouth_pts(**kw) for kw in poses.values()]
    def flat(g):
        inner, up_, lo_ = g
        if kind == 'interior': return [p for col_ in inner for p in col_]
        return [p for r in lips_geo(up_) + lips_geo(lo_) for p in r]
    m = bpy.data.meshes.new(name); bm_ = bmesh.new(); vs = [bm_.verts.new(p) for p in flat(geo[0])]
    if kind == 'interior':
        for i in range(NS_ - 1):
            for r in range(NR_ - 1): bm_.faces.new((vs[i * NR_ + r], vs[(i + 1) * NR_ + r], vs[(i + 1) * NR_ + r + 1], vs[i * NR_ + r + 1]))
    else:
        nr = 10
        for half in (0, 1):
            off = half * NS_ * nr
            for i in range(NS_ - 1):
                for k in range(nr): bm_.faces.new((vs[off + i * nr + k], vs[off + i * nr + (k + 1) % nr], vs[off + (i + 1) * nr + (k + 1) % nr], vs[off + (i + 1) * nr + k]))
    bm_.normal_update(); bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces[:]); bm_.to_mesh(m)
    o = bpy.data.objects.new(name, m); sc.collection.objects.link(o); o.data.materials.append(mat_)
    for p in m.polygons: p.use_smooth = True
    o.shape_key_add(name='Basis')
    for (kn, kw), g in list(zip(poses.items(), geo))[1:]:
        kb = o.shape_key_add(name=kn); kb.slider_max = 1.0
        for i, p in enumerate(flat(g)): kb.data[i].co = p
    if kind == 'interior':
        at_ = m.attributes.new('bocauv', 'FLOAT_VECTOR', 'POINT')
        for i in range(NS_):
            for r in range(NR_): at_.data[i * NR_ + r].vector = (-1 + 2 * i / (NS_ - 1), -1 + 2 * r / (NR_ - 1), 0)
    sb = o.modifiers.new('sub', 'SUBSURF'); sb.levels = sb.render_levels = 1
    return o
POSES = {'Basis': {}, 'abre': {'op': 1.0}, 'o': {'rnd': 1.0}, 'sonrie': {'sm': 1.0}, 'duda': {'sk': 1.0}}
m_mint = bpy.data.materials.new('boca_interior'); m_mint.use_nodes = True; nt = m_mint.node_tree; bs = nt.nodes['Principled BSDF']
bat = nt.nodes.new('ShaderNodeAttribute'); bat.attribute_name = 'bocauv'; bsp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(bat.outputs['Vector'], bsp.inputs[0])
ins = M(nt, 'SUBTRACT', 1.0, M(nt, 'SQRT', M(nt, 'ADD', M(nt, 'POWER', bsp.outputs[0], 2.0), M(nt, 'POWER', bsp.outputs[1], 2.0))))
mcol = mixc(nt, smooth(nt, ins, 0.0, 0.6), lin((92, 34, 44)), lin((26, 8, 14)))     # garganta oscura en el centro
tong = M(nt, 'MULTIPLY', smooth(nt, M(nt, 'MULTIPLY', bsp.outputs[1], -1.0), 0.25, 0.75), M(nt, 'SUBTRACT', 1.0, smooth(nt, M(nt, 'ABSOLUTE', bsp.outputs[0]), 0.35, 0.7)))
mcol = mixc(nt, M(nt, 'MULTIPLY', tong, 0.85), mcol, lin((214, 104, 112)))          # lengua rosada abajo
nt.links.new(mcol, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.65; bs.inputs['Specular IOR Level'].default_value = 0.15
m_lip = bpy.data.materials.new('labios'); m_lip.use_nodes = True; bs = m_lip.node_tree.nodes['Principled BSDF']
bs.inputs['Base Color'].default_value = (*lin((118, 132, 156)), 1); bs.inputs['Roughness'].default_value = 0.5   # labio discreto, apenas mas oscuro que la piel
bs.inputs['Subsurface Weight'].default_value = 0.3; bs.inputs['Subsurface Radius'].default_value = (0.01, 0.005, 0.004); bs.inputs['Coat Weight'].default_value = 0.4
mouth_in = build_mouth('FRY_boca_interior', POSES, m_mint, 'interior')
mouth = build_mouth('FRY_boca_labios', POSES, m_lip, 'labios')
mouth_o = [mouth_in]
def mouth_keys(o_, F_, **vals):
    for k_, v_ in vals.items():
        kb = o_.data.shape_keys.key_blocks[k_]; kb.value = v_; kb.keyframe_insert('value', frame=F_)
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
bpy.context.view_layer.update()
for o in [body, mouth] + mouth_o + fins + [caudal] + pects:
    if o in (mouth, *mouth_o):
        o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'b0'; o.matrix_parent_inverse = bone_tail_inv(); continue
    if o in pects:
        bl1 = rig.data.bones['b1']; o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'b1'
        o.matrix_parent_inverse = (rig.matrix_world @ bl1.matrix_local @ Matrix.Translation((0, bl1.length, 0))).inverted(); continue
    weigh(o); am = o.modifiers.new('arm', 'ARMATURE'); am.object = rig
    o.modifiers.move(len(o.modifiers) - 1, 0); o.parent = rig
for piv, brow, ctl, lid, lid2 in eyes:
    piv.parent = rig; piv.parent_type = 'BONE'; piv.parent_bone = 'b0'
    piv.matrix_parent_inverse = bone_tail_inv()
# ------------------------------------------------------------------ animacion: nada, frena (curva en C + aletas abiertas), mira a camara,
# duda (entrecierra el ojo y sube la cabeza), y se ilumina de curiosidad cuando aparece la burbuja
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
def ease(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)
def bump(f, a, b): return math.sin(math.pi * min(max((f - a) / (b - a), 0), 1))
ENV = [0.10 + 0.9 * (i / (NB - 1)) ** 1.6 for i in range(NB)]                    # amplitud crece hacia la cola
for o in pects:                                                                  # pectorales que se curvan (no solo giran)
    bd = o.modifiers.new('curva', 'SIMPLE_DEFORM'); bd.deform_method = 'BEND'; bd.deform_axis = 'Z'; o['bend'] = bd.name
phase = 0.0
PUFF = [60, 64, 67, 71, 74]                                                      # cuando suelta burbujitas por la boca (frames de diseno)
for F_ in range(1, NF + 1):
    t = (F_ - 1) / FPS; f = 1 + (F_ - 1) / TS                                   # f = tiempo de diseno (la actuacion), t = tiempo real (el nado)
    cruise = 1 - ease((f - 40) / 12); hover = ease((f - 56) / 12)
    freq = 3.0 * cruise + 0.7 * hover + 1.4 * (1 - cruise) * (1 - hover); phase += 2 * math.pi * freq / FPS
    amp = 0.21 * cruise + 0.05 * hover + 0.12 * (1 - cruise) * (1 - hover)
    cbend = 0.11 * bump(f, 42, 60)                                                # frenada: curva en C
    for i, b in enumerate(rig.pose.bones):
        b.rotation_mode = 'XYZ'
        ang = amp * ENV[i] * math.sin(phase - 0.75 * i) * (1.6 if i else 1) - (0.06 * amp * math.sin(phase + 0.6) if i == 0 else 0)
        b.rotation_euler = (0, 0, ang + cbend * (0.4 if i == 0 else 1.0) * (1 if i < NB - 3 else 0.6))
        b.keyframe_insert('rotation_euler', frame=F_)
    xs = -2.45 + 2.2 * (1 - (1 - min(1, (f - 1) / 58)) ** 2.2) + 0.03 * hover * math.sin(t * 1.3)
    zs = -0.07 + 0.015 * math.sin(t * 2.0) + 0.06 * ease((f - 64) / 26)
    po = ease((F_ - E0) / (E1 - 6 - E0)); xs -= 1.1 * po * po; zs -= 0.45 * po * po   # el globo que crece lo empuja fuera de cuadro
    rig.location = (xs, 0, zs); rig.keyframe_insert('location', frame=F_)
    turn = ease((f - 54) / 10) * (1 - 0.5 * ease((f - 70) / 14))                   # gira hacia camara
    up_ = ease((f - 66) / 20)                                                    # sube la cabeza (duda) hacia la burbuja
    tilt = math.radians(7) * bump(f, 62, 104)                                    # inclina la cabeza (gesto de pregunta)
    rig.rotation_euler = (tilt, -math.radians(17) * up_ + math.radians(1.2) * math.sin(t * 1.7), -math.radians(14) * turn)
    rig.keyframe_insert('rotation_euler', frame=F_)
    # aletas pares: remo rapido al nadar, se abren para frenar, remo suave (y se curvan) para quedarse quieto
    brake = bump(f, 40, 62)
    for k, o in enumerate(pects):
        sg = 1 if o.name.endswith('_1') else -1; fq = 3.2 * cruise + 1.6 * hover + 1.2
        flap = math.sin(t * 2 * math.pi * fq + k * 0.5)
        swing = math.radians(28 + 10 * (0.5 + 0.5 * flap) * (0.4 + 0.6 * hover) + 34 * brake)   # siempre hacia afuera: 28..72 grados
        o.rotation_euler = (sg * math.radians(8) * flap, math.radians(-14 - 8 * brake), -sg * swing)
        o.keyframe_insert('rotation_euler', frame=F_)
        bd = o.modifiers[o['bend']]; bd.angle = -sg * math.radians(40) * math.sin(t * 2 * math.pi * fq + k * 0.5 - 1.3)
        bd.keyframe_insert('angle', frame=F_)
    # ojos: miradas rapidas a los costados (busca), mira a camara, mira hacia arriba; parpados: duda (entrecierra) y curiosidad
    sacc = 0.22 * (1 if (f // 4) % 2 else -1) * bump(f, 46, 56)
    look_cam = ease((f - 56) / 5) * (1 - ease((f - 70) / 8)); look_up = ease((f - 70) / 10)
    squint = ease((f - 62) / 6) * (1 - ease((f - 94) / 6)); wide = ease((f - 94) / 5)
    blink = max(bump(f, 124, 127.5), bump(f, 150, 153.5), bump(f, 176, 179.5))
    look_cam = max(look_cam, ease((f - 132) / 5) * (1 - ease((f - 160) / 6))); look_up = look_up * (1 - 0.8 * ease((f - 132) / 5) * (1 - ease((f - 160) / 6)))
    for (piv, brow, ctl, lid, lid2), sgn in zip(eyes, (-1, 1)):
        cover = 0.16 + 0.24 * squint * (1 if sgn == -1 else 0.35) - 0.12 * wide
        cover = cover + (0.62 - cover) * blink                                   # parpadeo: los dos parpados se juntan en el medio
        cover2 = 0.06 + 0.2 * squint * (1 if sgn == -1 else 0.4) + 0.1 * wide * (1 - ease((f - 112) / 10))   # el de abajo sube: duda / sonrisa con los ojos
        cover2 = cover2 + (0.58 - cover2) * blink
        lid.rotation_euler = (sgn * math.radians(90 - 180 * cover), 0, 0); lid.keyframe_insert('rotation_euler', frame=F_)
        lid2.rotation_euler = (-sgn * math.radians(90 - 180 * cover2), 0, 0); lid2.keyframe_insert('rotation_euler', frame=F_)
        ctl.rotation_euler = (sgn * 0.28 * look_up, 0, -sgn * (0.22 * look_up - 0.35 * look_cam + sacc)); ctl.keyframe_insert('rotation_euler', frame=F_)
        s_ = 1 + 0.06 * wide; ctl.scale = (s_, s_, s_); ctl.keyframe_insert('scale', frame=F_)
        for hn in (f'FRY_brillo_{sgn}', f'FRY_brillo2_{sgn}'):                   # el brillo se apaga con el ojo cerrado (no atraviesa el parpado)
            h_ = bpy.data.objects[hn]; hs = 1 - ease((blink - 0.45) / 0.3); h_.scale = (hs, hs, hs); h_.keyframe_insert('scale', frame=F_)
    # boca 3D: "o" al soplar burbujitas, torcida en la duda, habla en silabas mientras aparece el globo, media sonrisa al final
    puff = max([bump(f, p_ - 2, p_ + 3) for p_ in PUFF] + [0])
    hmm = squint * (1 - wide)
    SYL = [(92, 95.5, 0.85, 0.0), (95.5, 98.5, 0.45, 0.6), (98.5, 102.5, 1.0, 0.0), (102.5, 105.5, 0.5, 0.5), (105.5, 110, 0.8, 0.2)]
    talk = sum(a_ * bump(f, s0, s1) for s0, s1, a_, _ in SYL); rnd_ = sum(r_ * bump(f, s0, s1) for s0, s1, _, r_ in SYL)
    breath = 0.06 * (0.5 + 0.5 * math.sin(t * 2 * math.pi * 0.9)) * hover * (1 - bump(f, 90, 112))
    smile = 0.7 * ease((f - 112) / 10)
    for o_ in (mouth, mouth_in):
        mouth_keys(o_, F_, abre=min(1.0, 0.75 * talk + breath + 0.15 * puff), o=min(1.0, 0.9 * puff + 0.6 * rnd_), sonrie=smile, duda=0.8 * hmm)
for fc in (rig.animation_data.action.fcurves if rig.animation_data else []):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
for j, (y0, z0, x0, x1, sc_, ph0) in enumerate(()):                              # cardumen de fondo desactivado (sin ojos y en la niebla se leia como fantasmas)
    r2 = rig.copy(); r2.data = rig.data; r2.animation_data_clear(); sc.collection.objects.link(r2); r2.name = f'CARDUMEN_rig_{j}'
    b2 = body.copy(); sc.collection.objects.link(b2); b2.name = f'CARDUMEN_{j}'; b2.parent = r2
    for md in b2.modifiers:
        if md.type == 'ARMATURE': md.object = r2
    d2 = bpy.data.objects.new(f'CARDUMEN_dorsal_{j}', dorsal.data); sc.collection.objects.link(d2); d2.parent = r2
    for md in dorsal.modifiers:
        m2 = d2.modifiers.new(md.name, md.type)
        if md.type == 'ARMATURE': m2.object = r2
        if md.type == 'SOLIDIFY': m2.thickness = md.thickness; m2.offset = md.offset
        if md.type == 'SUBSURF': m2.levels = m2.render_levels = 1
    r2.scale = (sc_, sc_, sc_); r2.rotation_euler = (0, 0, 0 if x1 > x0 else math.pi); ph2 = ph0
    for F_ in range(1, NF + 1):
        t = (F_ - 1) / FPS; ph2 += 2 * math.pi * 2.4 / FPS
        for i, b in enumerate(r2.pose.bones):
            b.rotation_mode = 'XYZ'; b.rotation_euler = (0, 0, 0.17 * ENV[i] * math.sin(ph2 - 0.75 * i) * (1.6 if i else 1)); b.keyframe_insert('rotation_euler', frame=F_)
        r2.location = (x0 + (x1 - x0) * (F_ - 1) / (NF - 1), y0, z0 + 0.04 * math.sin(t * 1.5 + j)); r2.keyframe_insert('location', frame=F_)
# ------------------------------------------------------------------ agua: el mismo sistema del film del camaron (escala de este set: 1 u = largo del fry)
WT = 2.6                                                                        # superficie del agua
TEAL = lin((50, 120, 190))                                                       # turquesa claro y saturado (look animacion)
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
# 4) fondo como el brief: lomas suaves azules en capas y algas anchas onduladas en azul oscuro, a los costados
FZ = -0.62
bpy.ops.mesh.primitive_grid_add(x_subdivisions=160, y_subdivisions=140, size=1, location=(0, 6.0, FZ)); bot = bpy.context.object; bot.name = 'FONDO_lecho'; bot.scale = (40, 30, 1)
tx_ = bpy.data.textures.new('lomas', 'CLOUDS'); tx_.noise_scale = 0.09; tx_.noise_depth = 1
dp_ = bot.modifiers.new('lomas', 'DISPLACE'); dp_.texture = tx_; dp_.strength = 0.012; dp_.texture_coords = 'LOCAL'; dp_.mid_level = 0.5
for p in bot.data.polygons: p.use_smooth = True
mb = bpy.data.materials.new('lecho'); mb.use_nodes = True; n = mb.node_tree; bs = n.nodes['Principled BSDF']
tc = n.nodes.new('ShaderNodeTexCoord'); nb = n.nodes.new('ShaderNodeTexNoise'); nb.inputs['Scale'].default_value = 25.0; n.links.new(tc.outputs['Generated'], nb.inputs['Vector'])
cb = n.nodes.new('ShaderNodeValToRGB'); cb.color_ramp.elements[0].color = (*lin((150, 170, 168)), 1); cb.color_ramp.elements[1].color = (*lin((186, 196, 182)), 1)   # arena clara (look Nemo)
n.links.new(nb.outputs['Fac'], cb.inputs['Fac']); n.links.new(cb.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.85
bs.inputs['Emission Color'].default_value = (*lin((230, 248, 255)), 1); n.links.new(caustic(n, 0.16), bs.inputs['Emission Strength'])
bot.data.materials.append(mb)
import random; R = random.Random(4)
for i, (x, y, sx, sz, c) in enumerate(((-3.2, 6.8, 4.5, 0.55, None), (3.4, 7.8, 4.0, 0.7, None))):   # dunas lejanas muy suaves
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24, location=(x, y, FZ - 0.05)); o = bpy.context.object; o.name = f'FONDO_loma_{i}'
    o.scale = (sx, sx * 0.6, sz); o.data.materials.append(mb)                       # lomas redondeadas en capas, como en la ilustracion
    for p in o.data.polygons: p.use_smooth = True
m_alga = bpy.data.materials.new('alga'); m_alga.use_nodes = True; nn = m_alga.node_tree; b_ = nn.nodes['Principled BSDF']
b_.inputs['Base Color'].default_value = (*lin((22, 62, 118)), 1); b_.inputs['Subsurface Weight'].default_value = 0.3; b_.inputs['Roughness'].default_value = 0.5
b_.inputs['Emission Color'].default_value = (*lin((150, 200, 255)), 1); nn.links.new(caustic(nn, 0.25), b_.inputs['Emission Strength'])
def alga(name, x, y, hgt, wid, ph_, lean):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = wid; cu.bevel_resolution = 3
    spl = cu.splines.new('BEZIER'); nseg = 7; spl.bezier_points.add(nseg - 1)
    for k in range(nseg):
        bp = spl.bezier_points[k]; t = k / (nseg - 1)
        bp.co = (lean * t * t * 0.4 + 0.07 * math.sin(t * 7 + ph_) * t, 0, hgt * t); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        bp.radius = (0.55 + 0.45 * math.sin(math.pi * min(1, t * 1.25))) * (1 - 0.85 * t ** 3)   # hoja ancha que termina en punta
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); o.location = (x, y, FZ); o.scale = (3.2, 0.35, 1.0); o.data.materials.append(m_alga)
    for f in range(1, NF + 1, 3):
        o.rotation_euler.y = 0.1 * math.sin(f / FPS * 1.3 + ph_) + 0.04 * math.sin(f / FPS * 2.9 + ph_); o.keyframe_insert('rotation_euler', index=1, frame=f)
    return o
# (sin algas: fondo limpio de agua abierta, como Nemo)
# rayos de sol: pocos, anchos y muy suaves, todos con la misma inclinacion que el sol, lejos detras del pez (se funden con la niebla)
for i in range(5):
    x_ = -2.2 + i * 1.15 + R.uniform(-0.25, 0.25); y_ = 2.6 + R.uniform(-0.3, 0.6)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x_, y_, 0.6), rotation=(math.radians(90), math.radians(-16), 0))
    o = bpy.context.object; o.name = f'RAYO_{i}'; o.scale = (R.uniform(0.6, 1.2), 5.0, 1)
    m = bpy.data.materials.new(f'rayo_{i}'); m.use_nodes = True; nn = m.node_tree; nn.nodes.clear()
    out = nn.nodes.new('ShaderNodeOutputMaterial'); em = nn.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*lin((215, 245, 250)), 1)
    tr = nn.nodes.new('ShaderNodeBsdfTransparent'); ad = nn.nodes.new('ShaderNodeAddShader'); nn.links.new(tr.outputs[0], ad.inputs[0]); nn.links.new(em.outputs[0], ad.inputs[1])
    tcn = nn.nodes.new('ShaderNodeTexCoord'); spn = nn.nodes.new('ShaderNodeSeparateXYZ'); nn.links.new(tcn.outputs['UV'], spn.inputs[0])
    gx = nn.nodes.new('ShaderNodeMath'); gx.operation = 'SINE'; mxx = nn.nodes.new('ShaderNodeMath'); mxx.operation = 'MULTIPLY'; mxx.inputs[1].default_value = math.pi
    nn.links.new(spn.outputs['X'], mxx.inputs[0]); nn.links.new(mxx.outputs[0], gx.inputs[0])
    gx2 = nn.nodes.new('ShaderNodeMath'); gx2.operation = 'POWER'; gx2.inputs[1].default_value = 3.0; nn.links.new(gx.outputs[0], gx2.inputs[0])   # bordes muy difusos
    gy = nn.nodes.new('ShaderNodeMath'); gy.operation = 'POWER'; gy.inputs[1].default_value = 2.2; nn.links.new(spn.outputs['Y'], gy.inputs[0])     # se apaga hacia abajo
    mm1 = nn.nodes.new('ShaderNodeMath'); mm1.operation = 'MULTIPLY'; nn.links.new(gx2.outputs[0], mm1.inputs[0]); nn.links.new(gy.outputs[0], mm1.inputs[1])
    mm2 = nn.nodes.new('ShaderNodeMath'); mm2.operation = 'MULTIPLY'; mm2.inputs[1].default_value = R.uniform(0.35, 0.6); nn.links.new(mm1.outputs[0], mm2.inputs[0])
    nn.links.new(mm2.outputs[0], em.inputs['Strength']); nn.links.new(ad.outputs[0], out.inputs[0]); m.surface_render_method = 'BLENDED'
    o.data.materials.append(m); o.visible_shadow = False
    for f in (1, NF):
        o.location.x = x_ + 0.12 * math.sin(i * 1.7 + f / FPS * 0.35); o.keyframe_insert('location', index=0, frame=f)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (*TEAL, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 0.85
_wn = w.node_tree; _tc = _wn.nodes.new('ShaderNodeTexCoord'); _sp = _wn.nodes.new('ShaderNodeSeparateXYZ'); _wn.links.new(_tc.outputs['Generated'], _sp.inputs[0])
_rp = _wn.nodes.new('ShaderNodeValToRGB'); _rp.color_ramp.elements[0].position = 0.35; _rp.color_ramp.elements[0].color = (*lin((14, 70, 118)), 1)
_rp.color_ramp.elements[1].position = 0.75; _rp.color_ramp.elements[1].color = (*lin((120, 210, 232)), 1)   # agua: oscura abajo, clara arriba (modela al pez)
_mr = _wn.nodes.new('ShaderNodeMapRange'); _mr.inputs['From Min'].default_value = -1.0; _wn.links.new(_sp.outputs['Z'], _mr.inputs['Value']); _wn.links.new(_mr.outputs[0], _rp.inputs['Fac'])
_wn.links.new(_rp.outputs['Color'], _wn.nodes['Background'].inputs[0])
# 6) particulas en suspension (como MOTES): puntitos finos que derivan
R = random.Random(9)
m_part = emit_mat('particula', lin((225, 248, 250)), 0.3)
pm_ = bpy.data.meshes.new('motas'); pb = bmesh.new()
for i in range(260):
    c = Vector((R.uniform(-2.4, 2.4), R.uniform(-1.6, 2.6), R.uniform(-1.3, 1.4))); r = R.uniform(0.0012, 0.0035)
    bmesh.ops.create_icosphere(pb, subdivisions=2, radius=r, matrix=Matrix.Translation(c))
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
    emr = n.nodes.new('ShaderNodeEmission'); emr.inputs['Color'].default_value = (*BRAND, 1); emr.inputs['Strength'].default_value = rim_em   # borde celeste de marca
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
for i, (f0, r) in enumerate(((FT(60), 0.014), (FT(64), 0.009), (FT(67), 0.017), (FT(71), 0.008), (FT(74), 0.012))):   # burbujitas que suelta por la boca y suben
    p0 = mouth_world(f0); o = bubble(f'AIRE_{i}', r)
    o.scale = (0, 0, 0); o.location = p0; o.keyframe_insert('scale', frame=f0 - 1); o.keyframe_insert('location', frame=f0 - 1)
    for f in range(f0, NF + 1, 2):
        t = (f - f0) / FPS; o.location = p0 + Vector((0.025 * math.sin(t * 9 + i) + 0.05 * t, -0.02, 0.2 * t + 0.1 * t * t))
        s = min(1.0, (f - f0) / 3.0); w_ = 0.07 * math.sin(t * 22 + i); o.scale = (s * (1 + w_), s, s * (1 - w_))
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
for i in range(0):                                                              # (sin hilo de burbujas lejano) (queda en la capa con niebla)
    o = bubble(f'AIREFONDO_{i}', R.uniform(0.006, 0.016), m_air_far); x0 = 1.15 + R.uniform(-0.05, 0.05); y0 = 1.4; ph_ = R.uniform(0, 10)
    for f in range(1, NF + 1, 3):
        z = -1.3 + ((f / FPS * 0.45 + i / 14 * 2.6) % 2.6); o.location = (x0 + 0.02 * math.sin(f / FPS * 7 + ph_), y0, z); o.keyframe_insert('location', frame=f)
# burbuja de dialogo: sale de la boca como burbujita, se infla mientras sube y queda temblando arriba a la derecha.
# Globo grande (~1/3 del ancho) y casi solido por dentro para el texto, con borde y reflejos de burbuja real; las burbujitas tambien llenas.
sc.frame_set(FT(100)); HEAD = rig.matrix_world @ Vector((0.33, 0, 0.15))              # arriba de la cabeza, en la pose final (mirando hacia arriba)
BIG = HEAD + Vector((0.52, -0.02, 0.16)); RBIG = 0.22; ASP = 1.35                 # ovalado (mas ancho que alto), como el brief                              # globo arriba a la derecha, en el plano de foco
_d = (BIG - HEAD); _dn = _d.normalized(); EDGE = BIG - Vector((_dn.x * RBIG * ASP, 0, _dn.z * RBIG)) * 1.08                      # borde del globo que mira a la cabeza
TRAIL = [(HEAD.lerp(EDGE, t), r) for t, r in ((0.06, 0.024), (0.34, 0.037), (0.68, 0.054))]   # de menor a mayor, en linea y sin tocarse
def head_world(f):
    sc.frame_set(f); return rig.matrix_world @ Vector((0.33, 0, 0.15))
def dialog(name, f0, f1, p_end, r_end, veil=True, wob=0.03, asp=1.0):
    ctl = bpy.data.objects.new(name, None); sc.collection.objects.link(ctl)
    shell = bubble(f'{name}_cascara', 1.0); shell.parent = ctl; highlights(shell)
    if veil:                                                                     # velo para el texto: disco que mira a camara, detras del centro
        vm_ = bpy.data.meshes.new(f'{name}_velo'); vb_ = bmesh.new()
        bmesh.ops.create_circle(vb_, cap_ends=True, segments=64, radius=0.97); vb_.to_mesh(vm_)
        vo_ = bpy.data.objects.new(f'{name}_velo', vm_); sc.collection.objects.link(vo_); vo_.parent = ctl
        vo_.rotation_euler = (math.radians(90), 0, 0); vo_.location = (0, 0.12, 0)
        mv_ = bpy.data.materials.new(f'{name}_velo'); mv_.use_nodes = True; n = mv_.node_tree; n.nodes.clear()
        out = n.nodes.new('ShaderNodeOutputMaterial'); em = n.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*lin((250, 253, 255)), 1)
        em.inputs['Strength'].default_value = 1.15; tr = n.nodes.new('ShaderNodeBsdfTransparent'); mx = n.nodes.new('ShaderNodeMixShader')
        tc = n.nodes.new('ShaderNodeTexCoord'); vl = n.nodes.new('ShaderNodeVectorMath'); vl.operation = 'LENGTH'; n.links.new(tc.outputs['Object'], vl.inputs[0])
        mr = n.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; mr.inputs['From Min'].default_value = 0.9; mr.inputs['From Max'].default_value = 0.99
        mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0; n.links.new(vl.outputs['Value'], mr.inputs['Value'])
        n.links.new(mr.outputs[0], mx.inputs['Fac']); n.links.new(tr.outputs[0], mx.inputs[1]); n.links.new(em.outputs[0], mx.inputs[2]); n.links.new(mx.outputs[0], out.inputs[0])
        mv_.surface_render_method = 'BLENDED'; vo_.data.materials.append(mv_)
    p0 = head_world(f0); ctl.scale = (0, 0, 0); ctl.location = p0; ctl.keyframe_insert('scale', frame=f0 - 1); ctl.keyframe_insert('location', frame=f0 - 1)
    for f in range(f0, NF + 1):
        t = (f - f0) / max(1, f1 - f0); k = ez(t); tt = (f - f0) / FPS
        arc = Vector((0, 0, 0.06 * math.sin(math.pi * min(t, 1))))                # sube en arco
        loc = p0.lerp(p_end, k) + arc * (1 - k) + Vector((0.004 * math.sin(tt * 2.2), 0, 0.007 * math.sin(tt * 1.7)))
        r_ = 0.012 + (r_end - 0.012) * k + r_end * 0.08 * math.sin(math.pi * min(max((f - f1 + 4) / 8, 0), 1))   # pequeno rebote al llegar
        w_ = wob * math.sin(tt * 24) * math.exp(-max(0, f - f1) / 18) + 0.012 * math.sin(tt * 7)
        ctl.location = loc; ctl.scale = (r_ * asp * (1 + w_), r_ * 0.94, r_ * (1 - w_))
        ctl.keyframe_insert('location', frame=f); ctl.keyframe_insert('scale', frame=f)
    return ctl
# globo de dialogo 3D (mismo mundo que el pez): almohadon blanco inflado con la forma de la referencia (ovalo + colita curva
# hacia la boca), cara de adelante plana para el texto, contorno azul oscuro por casco invertido (se ve como linea de historieta
# pero con volumen y luz real), se infla con rebote.
from mathutils.geometry import delaunay_2d_cdt
def _inside(pt, poly):
    x, y = pt; c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def _dseg(p, a, b):
    ab = (b[0] - a[0], b[1] - a[1]); ap = (p[0] - a[0], p[1] - a[1]); L2 = ab[0] ** 2 + ab[1] ** 2 or 1e-12
    t = max(0.0, min(1.0, (ap[0] * ab[0] + ap[1] * ab[1]) / L2)); return math.hypot(ap[0] - t * ab[0], ap[1] - t * ab[1])
def pillow_mesh(name, poly, T=0.05, D=0.07, step=0.011):
    xs = [p[0] for p in poly]; zs = [p[1] for p in poly]; pts = list(poly)
    x = min(xs) + step / 2
    while x < max(xs):
        z = min(zs) + step / 2
        while z < max(zs):
            q = (x + 0.37 * step * ((round(z / step)) % 2), z)
            if _inside(q, poly) and min(_dseg(q, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))) > step * 0.55: pts.append(q)
            z += step
        x += step
    n = len(poly); vo, eo, fo, *_ = delaunay_2d_cdt([Vector(p) for p in pts], [(i, (i + 1) % n) for i in range(n)], [], 0, 1e-7)
    def prof(p):
        d = min(_dseg((p.x, p.y), poly[i], poly[(i + 1) % n]) for i in range(n)); k = min(d / D, 1.0); return T * math.sqrt(max(0.0, 1 - (1 - k) ** 2))
    bm_ = bmesh.new(); front, back = {}, {}
    for i, p in enumerate(vo):
        h = prof(p)
        if h < 1e-6: front[i] = back[i] = bm_.verts.new((p.x, 0.0, p.y))
        else: front[i] = bm_.verts.new((p.x, -h, p.y)); back[i] = bm_.verts.new((p.x, h * 0.7, p.y))
    for f in fo:
        c = sum((vo[i] for i in f), Vector((0, 0))) / len(f)
        if not _inside((c.x, c.y), poly): continue
        try: bm_.faces.new([front[i] for i in f])
        except ValueError: pass
        try: bm_.faces.new([back[i] for i in reversed(f)])
        except ValueError: pass
    bmesh.ops.remove_doubles(bm_, verts=bm_.verts[:], dist=1e-7); bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces[:])
    m = bpy.data.meshes.new(name); bm_.to_mesh(m)
    for p in m.polygons: p.use_smooth = True
    return m
def speech(name, C, A, B, tip, f0, f1):
    ctl = bpy.data.objects.new(name, None); sc.collection.objects.link(ctl); ctl.location = C
    a1, a2 = math.radians(205), math.radians(238)                                # la colita sale entre estos angulos del ovalo (abajo a la izquierda)
    pts = []
    for i in range(110):
        a_ = a2 + (2 * math.pi - (a2 - a1)) * i / 109; pts.append((A * math.cos(a_), B * math.sin(a_)))
    e1 = (A * math.cos(a1), B * math.sin(a1)); e2 = (A * math.cos(a2), B * math.sin(a2))
    for i in range(1, 22):
        t = i / 22; c_ = (e1[0] * 0.55 + tip[0] * 0.45, e1[1] * 0.2 + tip[1] * 0.8)
        pts.append(((1 - t) ** 2 * e1[0] + 2 * (1 - t) * t * c_[0] + t * t * tip[0], (1 - t) ** 2 * e1[1] + 2 * (1 - t) * t * c_[1] + t * t * tip[1]))
    pts.append(tip)
    for i in range(1, 22):
        t = i / 22; c_ = (e2[0] * 0.3 + tip[0] * 0.7, e2[1] * 0.75 + tip[1] * 0.25)
        pts.append(((1 - t) ** 2 * tip[0] + 2 * (1 - t) * t * c_[0] + t * t * e2[0], (1 - t) ** 2 * tip[1] + 2 * (1 - t) * t * c_[1] + t * t * e2[1]))
    o_ = bpy.data.objects.new(f'{name}_globo', pillow_mesh(f'{name}_globo', pts)); sc.collection.objects.link(o_); o_.parent = ctl
    mw_ = bpy.data.materials.new(f'{name}_blanco'); mw_.use_nodes = True; bs_ = mw_.node_tree.nodes['Principled BSDF']
    bs_.inputs['Base Color'].default_value = (0.97, 0.975, 0.98, 1); bs_.inputs['Roughness'].default_value = 0.42
    bs_.inputs['Subsurface Weight'].default_value = 0.2; bs_.inputs['Subsurface Radius'].default_value = (0.03, 0.03, 0.035)
    bs_.inputs['Coat Weight'].default_value = 0.35; bs_.inputs['Coat Roughness'].default_value = 0.12   # globo 3D brillante (version aprobada)
    bs_.inputs['Emission Color'].default_value = (1, 1, 1, 1); bs_.inputs['Emission Strength'].default_value = 0.5   # que lea blanco bajo el agua
    mo_ = bpy.data.materials.new(f'{name}_contorno'); mo_.use_nodes = True; nn_ = mo_.node_tree; nn_.nodes.clear()
    oo_ = nn_.nodes.new('ShaderNodeOutputMaterial'); eo_ = nn_.nodes.new('ShaderNodeEmission'); eo_.inputs['Color'].default_value = (*lin((16, 44, 92)), 1)
    nn_.links.new(eo_.outputs[0], oo_.inputs[0]); mo_.use_backface_culling = True
    o_.data.materials.append(mw_); o_.data.materials.append(mo_)
    sb_ = o_.modifiers.new('sub', 'SUBSURF'); sb_.levels = sb_.render_levels = 1
    so_ = o_.modifiers.new('contorno', 'SOLIDIFY'); so_.show_render = False;   # sin contorno: el globo 3D aprobado no lo tenia
    so_.thickness = 0.009; so_.offset = 1; so_.use_flip_normals = True; so_.material_offset = 1; so_.use_rim = False
    for F_ in range(f0 - 1, NF + 1):
        t = (F_ - f0) / max(1, f1 - f0); tt = (F_ - f0) / FPS
        if F_ < f0: s_ = 0.0
        elif t < 0.6: s_ = ease(t / 0.6) * 1.08
        elif t < 1.0: s_ = 1.08 - 0.08 * ease((t - 0.6) / 0.4)
        else: s_ = 1.0 + 0.012 * math.sin(tt * 3.1)
        sq = 0.04 * math.sin(tt * 9) * math.exp(-max(0.0, F_ - f1) / 10) if F_ >= f0 else 0.0   # se sacude un poco al inflarse
        ctl.scale = (s_ * (1 + sq), s_, s_ * (1 - sq)); ctl.location = C + Vector((0, 0, 0.006 * math.sin(tt * 2.0))) * (1 if F_ >= f1 else 0)
        ctl.keyframe_insert('scale', frame=F_); ctl.keyframe_insert('location', frame=F_)
    return ctl
MOUTH = mouth_world(FT(108)); SPC = Vector((MOUTH.x + 0.37, -0.04, MOUTH.z + 0.25))
TIP = MOUTH + Vector((0.035, -0.04, 0.02)) - SPC                                  # la punta queda cerca de la boca
GLOBO = speech('PENSAMIENTO_globo', SPC, 0.27, 0.18, (TIP.x, TIP.z), FT(90), FT(100))
# ------------------------------------------------------------------ luz (sol nitido e inclinado, como en el film), camara, render
sun = bpy.data.objects.new('SOL', bpy.data.lights.new('SOL', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 4.2; sun.data.color = (1.0, 0.97, 0.9); sun.data.angle = math.radians(14)   # sol suave: brillos anchos, no rayas duras
sun.rotation_euler = (math.radians(22), math.radians(-16), 0)
rim = bpy.data.objects.new('CONTRALUZ', bpy.data.lights.new('CONTRALUZ', 'SUN')); sc.collection.objects.link(rim)   # luz de contorno desde atras
rim.data.energy = 3.2; rim.data.color = (0.82, 0.93, 1.0)                         # contraluz calido: separa al fry del fondo
bnc = bpy.data.objects.new('REBOTE_ARENA', bpy.data.lights.new('REBOTE_ARENA', 'AREA')); sc.collection.objects.link(bnc)   # rebote calido de la arena en la panza
bnc.data.energy = 26; bnc.data.size = 5; bnc.data.color = (0.85, 0.93, 0.95); bnc.location = (0, 0.2, -0.55); bnc.rotation_euler = (math.radians(180), 0, 0)
rim.rotation_euler = (math.radians(-60), 0, math.radians(15)); rim.data.volume_factor = 0.0
try: sun.data.volume_factor = 1.0
except Exception: pass
fill = bpy.data.objects.new('UW_FILL', bpy.data.lights.new('UW_FILL', 'SUN')); sc.collection.objects.link(fill)
fill.data.energy = 0.9; fill.data.color = (0.75, 0.95, 0.95); fill.rotation_euler = (math.radians(110), 0, math.radians(-20)); fill.data.volume_factor = 0.0
cam = bpy.data.objects.new('CAM', bpy.data.cameras.new('CAM')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 50; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8
for F_ in range(1, NF + 1):
    f = 1 + (F_ - 1) / TS; t = (F_ - 1) / FPS; push = 0.12 * ease((f - 1) / 60) + 0.2 * ease((f - 62) / 50)
    cam.location = (0.08 * ease((f - 1) / 80) + 0.006 * math.sin(t * 1.9) + 0.004 * math.sin(t * 3.1 + 1), -2.78 + push, 0.32 + 0.005 * math.sin(t * 2.3 + 2))
    cam.rotation_euler = (math.radians(86 + 0.25 * math.sin(t * 1.3)), math.radians(0.3 * math.sin(t * 0.9)), math.radians(0.25 * math.sin(t * 1.6 + 1)))
    cam.keyframe_insert('location', frame=F_); cam.keyframe_insert('rotation_euler', frame=F_)
    cam.data.dof.focus_distance = 2.78 - push; cam.data.dof.keyframe_insert('focus_distance', frame=F_)
# final: el globo se sigue inflando y viene hacia camara hasta tapar todo; se enciende a blanco puro para el titulo
_mw = bpy.data.materials['PENSAMIENTO_globo_blanco'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
_mw.keyframe_insert('default_value', frame=E0)
for F_ in range(E0, NF + 1):
    sc.frame_set(F_); k = ease((F_ - E0) / (E1 - E0)); k2 = k * k
    cpos = cam.matrix_world.translation; fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    tgt = cpos + fwd * 1.05 + Vector((0.0, 0, -0.02))
    base_ = SPC + Vector((0, 0, 0.006 * math.sin((F_ - FT(90)) / FPS * 2.0)))
    GLOBO.location = base_.lerp(tgt, k); s_ = 1.0 + 2.2 * k2 + 0.6 * k
    GLOBO.scale = (s_, s_, s_); GLOBO.keyframe_insert('location', frame=F_); GLOBO.keyframe_insert('scale', frame=F_)
    _mw.default_value = 0.5 + 3.0 * ease((F_ - E0 - 12) / (E1 - E0 - 12)); _mw.keyframe_insert('default_value', frame=F_)
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
    gi = bpy.data.images.new('agua_gradiente', 256, 256, float_buffer=True)  # grande: al estirar, el borde no se mezcla con negro       # color de agua: azul profundo abajo -> turquesa claro arriba
    lo_, hi_ = lin((18, 92, 140)), lin((128, 214, 232)); px = []                 # azul profundo -> celeste (como el brief)
    for yy in range(256):
        t_ = (yy / 255) ** 1.3; c_ = [lo_[k] + (hi_[k] - lo_[k]) * t_ for k in range(3)]; px += (c_ + [1.0]) * 256
    gi.pixels = px
    gn_ = cn.nodes.new('CompositorNodeImage'); gn_.image = gi
    gsz = cn.nodes.new('CompositorNodeScale'); gsz.space = 'RENDER_SIZE'; gsz.frame_method = 'STRETCH'; cn.links.new(gn_.outputs['Image'], gsz.inputs[0])
    pre = cn.nodes.new('CompositorNodeAlphaOver'); cn.links.new(gsz.outputs[0], pre.inputs[1]); cn.links.new(rl.outputs['Image'], pre.inputs[2])   # fondo vacio = agua
    mx = cn.nodes.new('CompositorNodeMixRGB'); mx.blend_type = 'MIX'; cn.links.new(gsz.outputs[0], mx.inputs[2])
    cn.links.new(rl.outputs['Mist'], mx.inputs[0]); cn.links.new(pre.outputs[0], mx.inputs[1])
    # brillo de la superficie arriba: mezcla aditiva de una franja clara (mascara de caja difusa)
    bx = cn.nodes.new('CompositorNodeBoxMask'); bx.x = 0.5; bx.y = 1.05; bx.width = 1.6; bx.height = 0.7
    bl = cn.nodes.new('CompositorNodeBlur'); bl.size_x = bl.size_y = int(RW * 0.12); bl.use_relative = False
    cn.links.new(bx.outputs[0], bl.inputs[0])
    sk = cn.nodes.new('CompositorNodeMixRGB'); sk.blend_type = 'SCREEN'; sk.inputs[2].default_value = (*lin((190, 240, 245)), 1)
    mk = cn.nodes.new('CompositorNodeMath'); mk.operation = 'MULTIPLY'; mk.inputs[1].default_value = 0.55
    cn.links.new(bl.outputs[0], mk.inputs[0]); cn.links.new(mk.outputs[0], sk.inputs[0]); cn.links.new(mx.outputs[0], sk.inputs[1])
    ao = cn.nodes.new('CompositorNodeAlphaOver'); cn.links.new(sk.outputs[0], ao.inputs[1]); cn.links.new(rb.outputs['Image'], ao.inputs[2])
    gl = cn.nodes.new('CompositorNodeGlare'); gl.glare_type = 'FOG_GLOW'; gl.threshold = 1.4; gl.size = 7; gl.mix = -0.75   # brillo suave
    cn.links.new(ao.outputs[0], gl.inputs[0])
    cb_ = cn.nodes.new('CompositorNodeColorBalance'); cb_.correction_method = 'LIFT_GAMMA_GAIN'   # sombras azul profundo, luces calidas
    cb_.lift = (0.98, 0.99, 1.03); cb_.gamma = (1.0, 1.0, 1.0); cb_.gain = (1.0, 1.0, 1.02); cn.links.new(gl.outputs[0], cb_.inputs[1])
    bc = cn.nodes.new('CompositorNodeBrightContrast'); bc.inputs['Contrast'].default_value = 16.0; cn.links.new(cb_.outputs[0], bc.inputs[0])
    vgi = bpy.data.images.new('vineta', 256, 144, float_buffer=True); px = []      # vineta suave: imagen radial escalada al cuadro
    for yy in range(144):
        for xx in range(256):
            d_ = math.hypot((xx + 0.5) / 256 - 0.5, ((yy + 0.5) / 144 - 0.5) * 0.75) / 0.62; v_ = 1 - 0.32 * min(1, max(0, (d_ - 0.55) / 0.45)) ** 1.6
            px += [v_, v_ * 1.0, v_ * 1.01, 1.0]
    vgi.pixels = px
    vgn = cn.nodes.new('CompositorNodeImage'); vgn.image = vgi
    vgs = cn.nodes.new('CompositorNodeScale'); vgs.space = 'RENDER_SIZE'; vgs.frame_method = 'STRETCH'; cn.links.new(vgn.outputs['Image'], vgs.inputs[0])
    vm = cn.nodes.new('CompositorNodeMixRGB'); vm.blend_type = 'MULTIPLY'; vm.inputs[0].default_value = 1.0
    cn.links.new(bc.outputs[0], vm.inputs[1]); cn.links.new(vgs.outputs[0], vm.inputs[2])
    wh = cn.nodes.new('CompositorNodeMixRGB'); wh.blend_type = 'MIX'; wh.inputs[2].default_value = (40, 40, 40, 1)   # AgX lleva 1.0 a gris: hace falta un valor alto para blanco puro   # placa blanca final (para el titulo)
    cn.links.new(vm.outputs[0], wh.inputs[1]); cn.links.new(wh.outputs[0], co.inputs[0])
    for F_, v_ in ((1, 0.0), (E1 - 8, 0.0), (E1 + 2, 1.0), (NF, 1.0)):
        wh.inputs[0].default_value = v_; wh.inputs[0].keyframe_insert('default_value', frame=F_)
CLOSE = '--cerca' in argv                                                         # camara de primer plano a la cabeza (para revisar ojos/parpados)
if SAVE: bpy.ops.wm.save_as_mainfile(filepath=SAVE)
a, b = (int(v) for v in FR.split('-'))
for f in range(a, b + 1):
    sc.frame_set(f)
    if CLOSE:
        hp = rig.matrix_world @ Vector((0.36, 0, 0.0)); cam.animation_data_clear(); cam.location = hp + Vector((0.05, -0.75, 0.04))
        cam.data.animation_data_clear(); cam.rotation_euler = (math.radians(87), 0, 0); cam.data.dof.focus_distance = 0.72; cam.data.lens = 60
    sc.render.filepath = f'{OUT}/f_{f:04d}{"_cerca" if CLOSE else ""}.png'; bpy.ops.render.render(write_still=True)
print('FRY_DONE')
