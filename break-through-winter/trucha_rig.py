# Trucha arcoiris 3D realista, rigueada (columna de huesos como el salmon del video RAS 360).
# Parte del modelo generado (Higgsfield / Meshy 7) ya limpio de las aletas en paleta, y le agrega:
#   piel corregida (lomo oliva, banda rosa, pintas negras, brillo mojado), ojos nuevos, aletas pectorales y pelvicas
#   con radios y membrana translucida, y un rig de 9 huesos (cabeza -> cola) con pesos suaves.
#   blender -b -P trucha_rig.py -- trucha_sin_aletas.glb salida.blend [vistas_prefijo]
import bpy, sys, math, bmesh
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index('--') + 1:]
GLB, OUT = A[0], A[1]; PREV = A[2] if len(A) > 2 else None
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def lin(c): return tuple(((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in c)
bpy.ops.import_scene.gltf(filepath=GLB)
body = [o for o in bpy.data.objects if o.type == 'MESH'][0]; body.name = 'TRUCHA_cuerpo'
for p in body.data.polygons: p.use_smooth = True
# modelo: largo en Y (cabeza en -Y, cola en +Y), alto en Z, ancho en X; 1,9 unidades de largo
YH, YT = -0.951, 0.952
# cortes de las aletas viejas (pectorales y pelvicas de Meshy): la piel alrededor se reconstruye.
# Por cada rebanada en Y se toma el contorno sano (radio segun el angulo alrededor del eje) y los vertices
# de la zona del corte se llevan a ese contorno: desaparecen tapas, pliegues y escalones.
from mathutils.kdtree import KDTree
bm = bmesh.new(); bm.from_mesh(body.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
med = sorted(f.calc_area() for f in bm.faces)[len(bm.faces) // 2]
def in_cut(c): return (-0.66 < c.y < -0.46 and c.z < 0.0) or (-0.08 < c.y < 0.28 and c.z < -0.12)
caps = [f for f in bm.faces if f.calc_area() > 6 * med and in_cut(f.calc_center_median())]
cut_pts = [v.co.copy() for f in caps for v in f.verts]
bmesh.ops.poke(bm, faces=caps)
kd = KDTree(len(cut_pts))
for i, c in enumerate(cut_pts): kd.insert(c, i)
kd.balance()
R0, R1 = 0.030, 0.060
wt = {}
for v in bm.verts:
    if not cut_pts: break
    d = kd.find(v.co)[2]
    if d < R1: wt[v.index] = 1.0 if d < R0 else 1.0 - (d - R0) / (R1 - R0)
bm.verts.ensure_lookup_table()
co = np.array([v.co[:] for v in bm.verts]); n_fix = 0
for vi, w in wt.items():
    v = bm.verts[vi]; y = v.co.y
    sl = np.where(np.abs(co[:, 1] - y) < 0.006)[0]
    sl = [i for i in sl if wt.get(i, 0.0) == 0.0]
    if len(sl) < 12: continue
    P = co[sl]; zc = 0.5 * (P[:, 2].max() + P[:, 2].min())
    th = np.arctan2(P[:, 2] - zc, P[:, 0]); r = np.hypot(P[:, 0], P[:, 2] - zc)
    o = np.argsort(th); th, r = th[o], r[o]
    t0 = math.atan2(v.co.z - zc, v.co.x)
    rt = np.interp(t0, np.concatenate([th - 2 * math.pi, th, th + 2 * math.pi]), np.concatenate([r, r, r]))
    rv = math.hypot(v.co.x, v.co.z - zc); rn = rv + (rt - rv) * (w * w * (3 - 2 * w))
    v.co.x = math.cos(t0) * rn; v.co.z = zc + math.sin(t0) * rn; n_fix += 1
lay = bm.verts.layers.float.new('parche'); bm.verts.ensure_lookup_table()
zone = [bm.verts[i] for i in wt]
for vi, w in wt.items(): bm.verts[vi][lay] = w
for it in range(8): bmesh.ops.smooth_vert(bm, verts=zone, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
zs = set(zone)
bmesh.ops.dissolve_degenerate(bm, dist=0.0015, edges=[e for e in bm.edges if e.verts[0] in zs or e.verts[1] in zs])
zone = [v for v in bm.verts if v.is_valid and v in zs]
for it in range(6): bmesh.ops.smooth_vert(bm, verts=zone, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
# triangulitos dados vuelta que quedan del abanico de la tapa: se borran, se cierra y se alisa
def outward(f):
    c = f.calc_center_median(); return Vector((c.x, 0.0, c.z - (-0.02))).normalized()
bad = [f for f in bm.faces if any(v in zs for v in f.verts) and f.normal.dot(outward(f)) < 0.15]
print('volteados', len(bad))
if bad:
    bmesh.ops.delete(bm, geom=bad, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bnd = [e for e in bm.edges if e.is_boundary]
    bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
    nf = [f for f in bm.faces if len(f.verts) > 3]
    if nf: bmesh.ops.triangulate(bm, faces=nf)
    zone = [v for v in bm.verts if v.is_valid and (v in zs or any(e.is_boundary for e in v.link_edges))]
    for it in range(6): bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if v[lay] > 0.0], factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
print('CORTES', len(caps), 'vertices rehechos', n_fix)
bm.to_mesh(body.data); bm.free()
for p in body.data.polygons: p.use_smooth = True
bpy.context.view_layer.objects.active = body; body.select_set(True)
try: bpy.ops.mesh.customdata_custom_splitnormals_clear()                         # normales del glTF partidas en las costuras UV
except Exception as e: print('normales', e)
dg = bpy.context.evaluated_depsgraph_get(); bvh = BVHTree.FromObject(body, dg)
def skin_x(y, z, side=1):                                                         # punto de la piel del lado +x / -x
    h = bvh.ray_cast(Vector((side * 1.0, y, z)), Vector((-side, 0, 0)))
    return h[0], (h[1] if h[1].dot(Vector((side, 0, 0))) > 0 else -h[1])
def skin_z(y, x):                                                                 # piel de abajo (panza)
    h = bvh.ray_cast(Vector((x, y, -1.0)), Vector((0, 0, 1)))
    return h[0], (h[1] if h[1].z < 0 else -h[1])

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
        if isinstance(x, tuple): n.inputs[idx].default_value = (*x, 1)
        else: nt.links.new(x, n.inputs[idx])
    return n.outputs[2]

# ------------------------------------------------------------------ piel: corrige la textura generada
mat = body.data.materials[0]; nt = mat.node_tree; bs = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
src = bs.inputs['Base Color'].links[0].from_socket                                # color de la textura original
tc = N(nt, 'ShaderNodeTexCoord'); sp = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs[0])
X, Y, Z = sp.outputs[0], sp.outputs[1], sp.outputs[2]
hsv = N(nt, 'ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 1.12; hsv.inputs['Value'].default_value = 1.0
nt.links.new(src, hsv.inputs['Color']); col = hsv.outputs[0]
u = M(nt, 'DIVIDE', M(nt, 'SUBTRACT', Y, YH), YT - YH)                           # 0 nariz -> 1 cola
# linea media del cuerpo (z del centro del flanco) segun el largo, y semialto
zc = M(nt, 'MULTIPLY_ADD', u, 0.0, -0.005)
zn = M(nt, 'DIVIDE', M(nt, 'SUBTRACT', Z, zc), 0.21)                              # -1 panza .. +1 lomo
# 1) lomo oliva-bronce (no gris azulado), flancos plateados apenas calidos, panza blanca
back = smooth(nt, zn, 0.05, 0.75)
col = mix(nt, M(nt, 'MULTIPLY', back, 0.70), col, lin((110, 112, 58)), 'COLOR')      # lomo oliva-bronce, mantiene escamas
flank = M(nt, 'SUBTRACT', 1.0, back)
col = mix(nt, M(nt, 'MULTIPLY', flank, 0.92), col, lin((200, 200, 200)), 'SATURATION')   # flanco y panza plata (saca el azul)
col = mix(nt, M(nt, 'MULTIPLY', flank, 0.22), col, lin((236, 232, 222)), 'MIX')
belly = smooth(nt, zn, -0.15, -0.70)
col = mix(nt, M(nt, 'MULTIPLY', belly, 0.62), col, lin((238, 236, 230)), 'MIX')             # panza blanca
# 2) banda rosa-roja de la agalla a la cola (la marca de la arcoiris), mas ancha al centro
zb = M(nt, 'MULTIPLY_ADD', u, 0.03, -0.005)
db = M(nt, 'DIVIDE', M(nt, 'SUBTRACT', Z, zb), M(nt, 'MULTIPLY_ADD', M(nt, 'SINE', M(nt, 'MULTIPLY', u, math.pi)), 0.022, 0.016))
band = M(nt, 'EXPONENT', M(nt, 'MULTIPLY', M(nt, 'MULTIPLY', db, db), -1.0))
band = M(nt, 'MULTIPLY', band, M(nt, 'MULTIPLY', smooth(nt, u, 0.10, 0.20), M(nt, 'SUBTRACT', 1.0, smooth(nt, u, 0.86, 0.95))))
col = mix(nt, M(nt, 'MULTIPLY', band, 0.75), col, lin((200, 90, 120)), 'COLOR')      # banda: tono rosa, conserva escamas
col = mix(nt, M(nt, 'MULTIPLY', band, 0.10), col, lin((190, 80, 105)), 'MULTIPLY')
cheek = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, smooth(nt, u, 0.10, 0.17)), M(nt, 'MULTIPLY', smooth(nt, u, 0.03, 0.08), smooth(nt, zn, 0.35, -0.2)))
col = mix(nt, M(nt, 'MULTIPLY', cheek, 0.55), col, lin((214, 108, 130)), 'COLOR')   # opérculo rosado
# 3) pintas negras: chicas y redondas, densas en el lomo y sobre la banda; tambien en la aleta dorsal y la cola
vo = N(nt, 'ShaderNodeTexVoronoi'); vo.feature = 'F1'; vo.inputs['Scale'].default_value = 88.0; vo.inputs['Randomness'].default_value = 1.0
mp = N(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 0.85, 1.0); nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], vo.inputs['Vector'])
rad = M(nt, 'MULTIPLY_ADD', vo.outputs['Color'], 0.0, 0.0)                         # placeholder
sep = N(nt, 'ShaderNodeSeparateColor'); nt.links.new(vo.outputs['Color'], sep.inputs[0])
rad = M(nt, 'MULTIPLY_ADD', sep.outputs[0], 0.16, 0.12)                            # radio por celda (variado)
keep = smooth(nt, sep.outputs[1], 0.18, 0.23)                                      # ~70% de las celdas con pinta
dot = M(nt, 'MULTIPLY', smooth(nt, M(nt, 'SUBTRACT', rad, vo.outputs['Distance']), 0.0, 0.035), keep)
tail = smooth(nt, u, 0.84, 0.88); fintop = smooth(nt, zn, 0.95, 1.10)
where = M(nt, 'MAXIMUM', M(nt, 'MULTIPLY', smooth(nt, zn, -0.05, 0.25), smooth(nt, u, 0.12, 0.2)), M(nt, 'MAXIMUM', tail, fintop))
col = mix(nt, M(nt, 'MULTIPLY', tail, 0.55), col, lin((104, 102, 80)), 'MIX')     # la cola no negra lisa: gris oliva con pintas
col = mix(nt, M(nt, 'MULTIPLY', M(nt, 'MULTIPLY', dot, where), 0.92), col, lin((16, 15, 13)), 'MIX')
anal = M(nt, 'MULTIPLY', smooth(nt, zn, -0.72, -0.86), M(nt, 'MULTIPLY', smooth(nt, u, 0.62, 0.66), M(nt, 'SUBTRACT', 1.0, smooth(nt, u, 0.82, 0.86))))
col = mix(nt, M(nt, 'MULTIPLY', anal, 0.85), col, lin((150, 140, 112)), 'MIX')
col = mix(nt, M(nt, 'MULTIPLY', anal, M(nt, 'MULTIPLY', smooth(nt, zn, -0.95, -1.12), 0.8)), col, lin((236, 234, 226)), 'MIX')
# piel rehecha en los cortes: sin el relieve de Meshy (que ahi quedaria estirado); relieve general mas suave
pat = N(nt, 'ShaderNodeAttribute'); pat.attribute_name = 'parche'; patch = pat.outputs['Fac']
nmap = [n for n in nt.nodes if n.type == 'NORMAL_MAP'][0]
col = mix(nt, M(nt, 'MULTIPLY', smooth(nt, patch, 0.35, 0.9), 0.95), col, lin((202, 202, 198)), 'MIX')   # tapa la linea pintada del corte
nt.links.new(col, bs.inputs['Base Color'])
nt.links.new(M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, patch), 0.6), nmap.inputs['Strength'])
# en la piel rehecha, escamas procedurales (bump) para que no quede un parche liso
vs = N(nt, 'ShaderNodeTexVoronoi'); vs.inputs['Scale'].default_value = 210.0; vs.feature = 'SMOOTH_F1'
nt.links.new(tc.outputs['Object'], vs.inputs['Vector'])
bump = N(nt, 'ShaderNodeBump'); bump.inputs['Distance'].default_value = 0.002
nt.links.new(M(nt, 'MULTIPLY', patch, 0.10), bump.inputs['Strength']); nt.links.new(vs.outputs['Distance'], bump.inputs['Height'])
nt.links.new(nmap.outputs[0], bump.inputs['Normal']); nt.links.new(bump.outputs[0], bs.inputs['Normal'])
nt.links.new(col, bs.inputs['Base Color'])
# 4) piel mojada: capa brillante, plata con algo de iridiscencia en el flanco
bs.inputs['Coat Weight'].default_value = 0.55; bs.inputs['Coat Roughness'].default_value = 0.06
bs.inputs['Specular IOR Level'].default_value = 0.6
try: bs.inputs['Thin Film Thickness'].default_value = 260.0; bs.inputs['Thin Film IOR'].default_value = 1.4
except KeyError: pass

# ------------------------------------------------------------------ ojos nuevos: cupula con iris dorado-plata y pupila negra
m_eye = bpy.data.materials.new('trucha_ojo'); m_eye.use_nodes = True; en = m_eye.node_tree; eb = en.nodes['Principled BSDF']
etc = N(en, 'ShaderNodeTexCoord'); esp = N(en, 'ShaderNodeSeparateXYZ'); en.links.new(etc.outputs['Object'], esp.inputs[0])
rr = M(en, 'SQRT', M(en, 'ADD', M(en, 'MULTIPLY', esp.outputs[1], esp.outputs[1]), M(en, 'MULTIPLY', esp.outputs[2], esp.outputs[2])))   # radio desde el eje del ojo
ec = mix(en, smooth(en, rr, 0.42, 0.50), (0.004, 0.004, 0.005), lin((196, 168, 92)))   # pupila -> iris dorado
ec = mix(en, smooth(en, rr, 0.70, 0.86), ec, lin((206, 206, 196)))                    # iris -> anillo plateado
en.links.new(ec, eb.inputs['Base Color']); eb.inputs['Roughness'].default_value = 0.25; eb.inputs['Metallic'].default_value = 0.35
eb.inputs['Coat Weight'].default_value = 1.0; eb.inputs['Coat Roughness'].default_value = 0.02
EYE = (0.050, -0.862, 0.020); ER = 0.0205
eyes = []
for side in (1, -1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=48, ring_count=24); e = bpy.context.object
    e.name = f'TRUCHA_ojo_{"I" if side > 0 else "D"}'; e.scale = (ER, ER, ER); e.location = (side * EYE[0], EYE[1], EYE[2])
    e.rotation_euler = (0, 0, 0 if side > 0 else math.pi)                         # el eje +X local mira hacia afuera
    for p in e.data.polygons: p.use_smooth = True
    e.data.materials.append(m_eye); eyes.append(e)

# ------------------------------------------------------------------ aletas en abanico con radios (pectorales y pelvicas)
m_fin = bpy.data.materials.new('trucha_aleta'); m_fin.use_nodes = True; fn = m_fin.node_tree; fb = fn.nodes['Principled BSDF']
at = N(fn, 'ShaderNodeAttribute'); at.attribute_name = 'aleta'; asp = N(fn, 'ShaderNodeSeparateXYZ'); fn.links.new(at.outputs['Vector'], asp.inputs[0])
FU, FV, FW = asp.outputs[0], asp.outputs[1], asp.outputs[2]                       # u base->borde, v a lo largo de la base, w = v*radios
ray = M(fn, 'POWER', M(fn, 'ABSOLUTE', M(fn, 'SINE', M(fn, 'MULTIPLY', FW, math.pi))), 6.0)   # radios finos
ray = M(fn, 'MULTIPLY', ray, M(fn, 'SUBTRACT', 1.0, M(fn, 'MULTIPLY', smooth(fn, FU, 0.75, 1.0), 0.6)))
lead = smooth(fn, FV, 0.10, 0.0)                                                   # borde de ataque blanco (como la arcoiris)
fc = mix(fn, smooth(fn, FU, 0.0, 0.9), lin((150, 138, 108)), lin((200, 140, 100)))  # membrana oliva -> ambar en el borde
fc = mix(fn, M(fn, 'MULTIPLY', ray, 0.75), fc, lin((96, 74, 50)))
fc = mix(fn, M(fn, 'MULTIPLY', lead, 0.8), fc, lin((240, 238, 230)))
fn.links.new(fc, fb.inputs['Base Color']); fb.inputs['Roughness'].default_value = 0.4; fb.inputs['Coat Weight'].default_value = 0.25
fb.inputs['Subsurface Weight'].default_value = 0.15; fb.inputs['Subsurface Radius'].default_value = (0.02, 0.012, 0.008)
alpha = M(fn, 'MAXIMUM', M(fn, 'SUBTRACT', 0.55, M(fn, 'MULTIPLY', smooth(fn, FU, 0.15, 1.0), 0.30)), M(fn, 'MULTIPLY', ray, 0.92))
fn.links.new(alpha, fb.inputs['Alpha'])
try: m_fin.surface_render_method = 'DITHERED'
except Exception: pass
def fan_fin(name, base0, base1, tipdir, outdir, length, spread, rays, NU=14, NV=48, cup=0.06, th=0.002, sv=None):
    """aleta: base de base0 a base1 (pegada a la piel), se abre hacia tipdir; contorno redondeado; ondulada en radios"""
    b0, b1 = Vector(base0), Vector(base1); td = Vector(tipdir).normalized(); od = Vector(outdir).normalized()
    sd = (b1 - b0).normalized(); sd = (Vector(sv) - td * Vector(sv).dot(td)).normalized() if sv else sd; m = bpy.data.meshes.new(name); bm = bmesh.new(); grid = []
    for i in range(NV + 1):
        v = i / (NV - 1 + 1e-9) if NV > 1 else 0; v = i / NV
        base = b0.lerp(b1, v)
        L = length * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 0.25 + v * 0.95)))   # mas larga en los radios del medio-adelante
        d = (td + sd * (v - 0.30) * spread).normalized()
        row = []
        for j in range(NU + 1):
            uu = j / NU; p = base + d * L * uu + od * (cup * L * math.sin(math.pi * uu) * 0.5)
            p += od * (0.004 * L * math.sin(v * rays * math.pi) * uu)              # pliegue apenas entre radios
            row.append(bm.verts.new(p))
        grid.append(row)
    for i in range(NV):
        for j in range(NU): bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bm.to_mesh(m); bm.free()
    at_ = m.attributes.new('aleta', 'FLOAT_VECTOR', 'POINT')
    for i in range(NV + 1):
        for j in range(NU + 1): at_.data[i * (NU + 1) + j].vector = (j / NU, i / NV, i / NV * rays)
    o = bpy.data.objects.new(name, m); sc.collection.objects.link(o); m.materials.append(m_fin)
    for p in m.polygons: p.use_smooth = True
    so = o.modifiers.new('grosor', 'SOLIDIFY'); so.thickness = th; so.offset = 0
    o.modifiers.new('suave', 'SUBSURF').levels = 1
    return o
fins = []
for side in (1, -1):
    p0, _ = skin_x(-0.592, -0.078, side); p1, _ = skin_x(-0.515, -0.124, side)   # pectoral: detras del opérculo, baja
    fins.append(('pect', side, fan_fin(f'TRUCHA_pectoral_{side}', p0 - Vector((side * 0.004, 0, 0)), p1 - Vector((side * 0.004, 0, 0)),
                (side * 0.22, 1.0, -0.30), (side * 1, 0, 0), 0.20, 1.0, 16, sv=(side * 0.25, 0, -1))))
    q0, _ = skin_z(0.035, side * 0.050); q1, _ = skin_z(0.095, side * 0.040)        # pelvica: bajo la panza, hacia atras
    fins.append(('pelv', side, fan_fin(f'TRUCHA_pelvica_{side}', q0 + Vector((0, 0, 0.004)), q1 + Vector((0, 0, 0.004)),
                (side * 0.18, 1.0, -0.40), (side * 1, 0, -0.2), 0.15, 0.95, 9, sv=(side * 0.35, 0, -1))))

# ------------------------------------------------------------------ rig: 9 huesos de la nariz a la cola (como el salmon del video)
NB = 9; JY = [YH + (YT - YH) * (i / NB) ** 1.0 for i in range(NB + 1)]
JY = [YH, -0.62, -0.42, -0.22, -0.02, 0.18, 0.38, 0.56, 0.74, YT]                  # cabeza rigida larga, mas huesos hacia la cola
arm = bpy.data.armatures.new('trucha_rig'); rig = bpy.data.objects.new('TRUCHA_rig', arm); sc.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT'); prev = None
for i in range(NB):
    b = arm.edit_bones.new(f'Spine{i}' if i else 'Head'); b.head = (0, JY[i], 0.0); b.tail = (0, JY[i + 1], 0.0)
    if prev: b.parent = prev; b.use_connect = True
    prev = b
jb = arm.edit_bones.new('Jaw'); jb.head = (0, -0.80, -0.05); jb.tail = (0, -0.93, -0.07); jb.parent = arm.edit_bones['Head']
bpy.ops.object.mode_set(mode='OBJECT')
names = ['Head'] + [f'Spine{i}' for i in range(1, NB)]
V = np.array([v.co[:] for v in body.data.vertices]); cen = np.array([(JY[i] + JY[i + 1]) / 2 for i in range(NB)])
groups = {n: body.vertex_groups.new(name=n) for n in names}
W = np.zeros((len(V), NB))
for i in range(NB):
    half = (JY[i + 1] - JY[i]) * 0.85
    W[:, i] = np.clip(1 - np.abs(V[:, 1] - cen[i]) / (half * 1.6), 0, None) ** 1.5
W[V[:, 1] < -0.66, :] = 0; W[V[:, 1] < -0.66, 0] = 1                                # cabeza rigida (no se deforma el craneo)
W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
for i, n in enumerate(names):
    idx = np.nonzero(W[:, i] > 1e-3)[0]
    for k in idx: groups[n].add([int(k)], float(W[k, i]), 'REPLACE')
md = body.modifiers.new('rig', 'ARMATURE'); md.object = rig; body.parent = rig
def parent_bone(o, bone):
    mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = bone
    bpy.context.view_layer.update(); o.matrix_world = mw
for e in eyes: parent_bone(e, 'Head')
for kind, side, f in fins: parent_bone(f, 'Spine1' if kind == 'pect' else 'Spine4')
for n in names: rig.pose.bones[n].rotation_mode = 'XYZ'
rig['nota'] = 'Huesos Head..Spine8 de la nariz a la cola: rotar en Z (lateral) para nadar, en X para arquear'

# ------------------------------------------------------------------ vistas de control (opcional)
if PREV:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.render.resolution_x = 1400; sc.render.resolution_y = 700
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.57, 0.6, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.7
    for rot, en_ in (((0.7, 0, 0.9), 3.5), ((2.3, 0, 3.8), 1.5), ((-0.6, 0, -1.2), 1.0)):
        l = bpy.data.objects.new('L', bpy.data.lights.new('L', 'SUN')); l.data.energy = en_; l.rotation_euler = rot; sc.collection.objects.link(l)
    cam = bpy.data.objects.new('C', bpy.data.cameras.new('C')); sc.collection.objects.link(cam); sc.camera = cam
    def shot(nm, loc, tg, lens):
        cam.data.lens = lens; cam.location = Vector(loc); d = Vector(tg) - cam.location
        cam.rotation_euler = d.to_track_quat('-Z', 'Y' if abs(d.normalized().z) < 0.9 else 'X').to_euler()
        sc.render.filepath = f'{PREV}_{nm}.png'; bpy.ops.render.render(write_still=True)
    shot('lado', (4.2, 0, 0), (0, 0, 0), 40); shot('abajo', (0, 0, -4.2), (0, 0, 0), 40)
    shot('cabeza', (1.0, -0.70, 0.05), (0, -0.70, 0), 50); shot('34', (2.6, -2.4, 1.2), (0, 0, 0), 45)
    shot('aleta', (0.9, -0.40, -0.35), (0.1, -0.45, -0.12), 55); shot('cola', (1.3, 0.65, 0), (0, 0.70, 0), 50)
    for i, n in enumerate(names[1:], 1): rig.pose.bones[n].rotation_euler = (0, 0, 0.16 * math.sin(i * 0.8))   # pose de nado (curva en S)
    shot('pose_arriba', (0, 0, 4.2), (0, 0, 0), 40); shot('pose_34', (2.6, -2.4, 1.2), (0, 0, 0), 45)
    for n in names: rig.pose.bones[n].rotation_euler = (0, 0, 0)
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print('TRUCHA_OK', OUT)
