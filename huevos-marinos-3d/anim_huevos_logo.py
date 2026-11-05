# Animacion: placa de lupa en campo oscuro con el logo LARVIVA BROODSTOCK en el fondo. Al principio hay 8 huevos
# (como en la foto); despues caen (se hunden en el agua hacia la placa) mas huevos desde arriba que van tapando el logo.
# Caida: gravedad reducida por el agua + arrastre (velocidad casi constante), giro lento mientras bajan, choques suaves
# entre huevos, rodadura sin deslizar al tocar la placa u otro huevo. Los huevos usan los materiales de huevos_campo_oscuro.py.
# blender -b --factory-startup -P anim_huevos_logo.py -- OUT_DIR [muestras] [ancho] [frames a-b] [paso]
import bpy, bmesh, math, random, sys, os, mathutils, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:]; OUTD = args[0]
SPP = int(args[1]) if len(args) > 1 else 32; RW = int(args[2]) if len(args) > 2 else 960
FR = args[3] if len(args) > 3 else '1-288'; STEP = int(args[4]) if len(args) > 4 else 1
LOGO = os.environ.get('LOGO', os.path.join(HERE, 'referencia', 'logo_larviva_broodstock.png'))
# materiales y utilidades del still (todo lo que esta antes de la disposicion de la foto)
src = open(os.path.join(HERE, 'huevos_campo_oscuro.py')).read()
pre = src[:src.index('# ---- disposicion trazada')]
pre = pre.replace("args = sys.argv[sys.argv.index('--') + 1:]; OUT = args[0]", "OUT = ''").replace("SPP = int(args[1]) if len(args) > 1 else 48; RW = int(args[2]) if len(args) > 2 else 1000", "")
os.environ.setdefault('CIOR', '1.015'); os.environ.setdefault('YT', '0.12'); os.environ.setdefault('CT', '0.6')   # el interior del huevo atenua lo que hay detras: los huevos tapan el logo                         # menos lente: los huevos ya no 'agrandan' el logo como bolas blancas
exec(pre)
FPS, NF = 24, int(os.environ.get('NF', '360'))                # 15 s
sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = NF
R = 1.28                                                       # radio del huevo (mismo que en la foto)
# ---------------------------------------------------------------- variantes de huevo (colecciones instanciables)
def build_variant(k, seed):
    R_ = random.Random(seed); before = set(sc.objects); c = mathutils.Vector((0, 0, 0))
    sphere('chorion', R, c, 96).data.materials.append(chor)
    off = mathutils.Vector((R_.uniform(-1, 1), R_.uniform(-1, 1), 0)).normalized() * R * 0.05
    sphere('yolk', R * 0.91, c + off, 64).data.materials.append(yolk)
    a = R_.uniform(0, 6.28); dv = mathutils.Vector((math.cos(a), math.sin(a), 0)); o2 = mathutils.Vector((R_.uniform(-.15, .15), R_.uniform(-.15, .15), 0)) * R
    h = dv * 0.6 * R + o2; t = -dv * 0.6 * R + o2
    ph1, ph2 = R_.uniform(0, 6.28), R_.uniform(0, 6.28); n = 40; side = mathutils.Vector((-dv.y, dv.x, 0)); bend = R_.uniform(-0.15, 0.15) * R
    pts = []
    for i in range(n):
        u = i / (n - 1); q = h.lerp(t, u) + side * bend * math.sin(math.pi * u); d = q.length
        q.z = math.sqrt(max((0.86 * R) ** 2 - d * d, 0)) * 0.45; pts.append(c + q)
    cu = bpy.data.curves.new('emb', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.12 * R; cu.bevel_resolution = 5; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(n - 1)
    for i, p in enumerate(pts):
        u = i / (n - 1); sp.points[i].co = (p.x, p.y, p.z, 1); base = 0.75 + 0.25 * math.sin(math.pi * min(u * 1.2, 1)) if u < 0.85 else 0.75 - 1.6 * (u - 0.85)
        sp.points[i].radius = base * (1 + 0.14 * math.sin(u * 9.0 + ph1) + 0.08 * math.sin(u * 23.0 + ph2))
    eo = bpy.data.objects.new('embryo', cu); sc.collection.objects.link(eo); cu.materials.append(emb)
    ax0 = (pts[0] - pts[4]).normalized(); hb = sphere('headb', 0.21 * R, pts[0] + ax0 * 0.05 * R, 40); hb.rotation_mode = 'QUATERNION'; hb.rotation_quaternion = ax0.to_track_quat('X', 'Z'); hb.scale = (1.15, 1.0, 0.75)
    ax1 = (pts[-1] - pts[-5]).normalized(); tb = sphere('tailb', 0.12 * R, pts[-1] - ax1 * 0.02 * R, 32); tb.rotation_mode = 'QUATERNION'; tb.rotation_quaternion = ax1.to_track_quat('X', 'Z'); tb.scale = (1.3, 1.0, 0.7)
    bpy.ops.object.select_all(action='DESELECT'); eo.select_set(True); bpy.context.view_layer.objects.active = eo; bpy.ops.object.convert(target='MESH')
    hb.select_set(True); tb.select_set(True); bpy.ops.object.join()
    rmh = eo.modifiers.new('r', 'REMESH'); rmh.mode = 'VOXEL'; rmh.voxel_size = 0.014 * R; rmh.use_smooth_shade = True
    eo.modifiers.new('s', 'SMOOTH').iterations = 3
    bpy.ops.object.select_all(action='DESELECT'); eo.select_set(True); bpy.context.view_layer.objects.active = eo
    for m_ in list(eo.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)
    # perlitas: una sola malla por variante (rapido para instanciar)
    pb = bmesh.new()
    def cluster(cc, nn, spread, rr=(0.018, 0.027), flat=0.35):
        for _ in range(nn):
            q = cc + mathutils.Vector((R_.gauss(0, spread), R_.gauss(0, spread), R_.gauss(0, spread * flat)))
            if (q - c).length > 0.88 * R: continue
            r_ = R * R_.uniform(*rr); g_ = bmesh.ops.create_uvsphere(pb, u_segments=12, v_segments=6, radius=r_)
            bmesh.ops.translate(pb, vec=q, verts=g_['verts'])
    for _ in range(R_.randint(2, 3)):
        p = R_.choice(pts[4:-4]); nn = R_.randint(15, 35); cluster(p + mathutils.Vector((0, 0, 0.1 * R)), nn, 0.016 * R * math.sqrt(nn))
    for _ in range(R_.randint(4, 7)):
        a = R_.uniform(0, 6.28); r_ = R * 0.75 * math.sqrt(R_.random())
        cc = mathutils.Vector((r_ * math.cos(a), r_ * math.sin(a), 0)); cc.z = math.sqrt(max((0.85 * R) ** 2 - r_ * r_, 0)) * R_.uniform(-0.6, 0.6)
        nn = R_.randint(15, 45); cluster(cc, nn, 0.015 * R * math.sqrt(nn))
    for _ in range(90):
        a = R_.uniform(0, 6.28); r_ = R * 0.86 * math.sqrt(R_.random())
        cluster(mathutils.Vector((r_ * math.cos(a), r_ * math.sin(a), R_.uniform(-0.5, 0.5) * R)), 1, 0.0, (0.005, 0.01))
    pm_ = bpy.data.meshes.new('pearls'); pb.to_mesh(pm_); pb.free()
    for p_ in pm_.polygons: p_.use_smooth = True
    po = bpy.data.objects.new('pearls', pm_); sc.collection.objects.link(po); pm_.materials.append(pearl)
    col = bpy.data.collections.new('egg%d' % k)
    for o in set(sc.objects) - before:
        for cl in list(o.users_collection): cl.objects.unlink(o)
        col.objects.link(o)
    return col
NV = int(os.environ.get('NV', '16'))
VARS = [build_variant(k, 100 + k) for k in range(NV)]
# ---------------------------------------------------------------- simulacion (numpy): caen desde arriba del cuadro
# Vista de la placa: la gravedad apunta hacia abajo de la pantalla (-y). Los huevos viven en una capa (z ~ R), entran
# por el borde superior (nunca aparecen de golpe), caen frenados por el agua, chocan suave, ruedan sobre los de abajo
# (giro en el plano: el embrion se sigue viendo de frente) y se apilan desde abajo hasta llenar todo el rectangulo.
rng = np.random.default_rng(7)
W_, H_ = 30.0, 30.0 * 9 / 16                                   # campo visible en el plano de la placa
LW, LH = 18.0, 18.0 * 584 / 2000                               # logo en el fondo, centrado
PHOTO = [(205, 492), (468, 355), (895, 212), (675, 508), (932, 518), (545, 830), (858, 800), (850, 1108)]   # los 8 de la foto (px)
start = [((x - 1000) / 100.0 - 1.5, -(y - 750) / 100.0) for x, y in PHOTO]
NS = len(start); NFALL = int(os.environ.get('NFALL', '96')); N_ = NS + NFALL
XW = W_ / 2 + 0.45 * R - R; YF = -H_ / 2 - 0.45 * R + R           # paredes y piso apenas fuera de cuadro: se llena de borde a borde
pos = np.zeros((N_, 3)); vel = np.zeros((N_, 3)); t0 = np.zeros(N_)
pos[:NS, :2] = start; pos[:, 2] = R + rng.uniform(-0.08, 0.08, N_) * R
for k_, i in enumerate(range(NS, N_)):                         # fila de espera arriba, fuera de cuadro; se sueltan escalonados
    pos[i, 0] = rng.uniform(-XW, XW); pos[i, 1] = H_ / 2 + R * 1.2 + rng.uniform(0, 1.5)
    t0[i] = 0.8 + 7.4 * (k_ / NFALL) ** 0.9 + rng.uniform(-0.15, 0.15)
zc = pos[:, 2].copy(); home = pos[:NS].copy()
wph = rng.uniform(0, 6.28, (NS, 2)); wfr = rng.uniform(0.18, 0.32, (NS, 2)); wspin = rng.uniform(-0.18, 0.18, NS)   # vaiven suave de los 8 iniciales
state = np.zeros(N_, int); state[:NS] = 1                      # 0 esperando, 1 pegado a la placa (los de la foto), 2 libre
quat = np.zeros((N_, 4)); w_ = np.zeros((N_, 3))
def qmul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1*w2 - x1*x2 - y1*y2 - z1*z2, w1*x2 + x1*w2 + y1*z2 - z1*y2, w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2])
def qax(ax, an): ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax); return np.array([math.cos(an / 2), *(math.sin(an / 2) * ax)])
for i in range(N_):                                            # embrion de frente a la camara, girado en el plano, leve inclinacion
    q = qax([0, 0, 1], rng.uniform(0, 6.28))
    if i >= NS: q = qmul(qax([rng.normal(), rng.normal(), 0], rng.uniform(0, 0.35)), q); w_[i] = [rng.normal(0, 0.12), rng.normal(0, 0.12), rng.normal(0, 0.7)]
    quat[i] = q
G_, DRAG, SUB, IT = 9.0, 1.7, 10, 3                            # caida frenada por el agua (~5 u/s)
dt = 1.0 / FPS / SUB
P_ = np.zeros((NF, N_, 3)); Q_ = np.zeros((NF, N_, 4))
for f in range(NF):
    for s_ in range(SUB):
        t = (f + s_ / SUB) / FPS
        state[(state == 0) & (t >= t0)] = 2
        for i in np.where(state[:NS] == 1)[0]:                 # los 8 de la foto: flotan apenas (deriva lenta + giro lento en el plano)
            tgt = home[i] + np.array([0.22 * math.sin(6.283 * wfr[i, 0] * t + wph[i, 0]), 0.18 * math.sin(6.283 * wfr[i, 1] * t + wph[i, 1]), 0.0])
            vel[i] = (tgt - pos[i]) / dt * 0.5 if t > 0 else 0; pos[i] = tgt
            quat[i] = qmul(qax([0, 0, 1], wspin[i] * dt), quat[i])
        fr = state == 2
        vel[fr, 1] += (-G_) * dt; vel[fr] -= DRAG * vel[fr] * dt
        pos[fr] += vel[fr] * dt
        nsum = np.zeros((N_, 3)); touch = np.zeros(N_, bool)
        for _ in range(IT):                                    # contactos (varias pasadas: sin huevos encimados)
            d = pos[:, None, :] - pos[None, :, :]; dist = np.linalg.norm(d, axis=-1) + np.eye(N_) * 1e9
            ii, jj = np.where(np.triu(dist < 2 * R * 0.999))
            ii, jj = ii[(state[ii] > 0) & (state[jj] > 0)], jj[(state[ii] > 0) & (state[jj] > 0)]
            for i, j in zip(ii, jj):
                nrm = d[i, j] / dist[i, j]; pen = 2 * R - dist[i, j]
                if state[i] == 1 and state[j] == 2: state[i] = 2        # un huevo de la foto empujado: se suelta
                if state[j] == 1 and state[i] == 2: state[j] = 2
                mi = 1.0 if state[i] == 2 else 0.0; mj = 1.0 if state[j] == 2 else 0.0
                if mi + mj == 0: continue
                pos[i] += nrm * pen * mi / (mi + mj); pos[j] -= nrm * pen * mj / (mi + mj)
                rv = vel[i] - vel[j]; vn = rv @ nrm
                if vn < 0:
                    imp = -(1 + 0.05) * vn / (mi + mj); vel[i] += imp * mi * nrm; vel[j] -= imp * mj * nrm
                    vt = rv - vn * nrm; vel[i] -= vt * 0.05 * mi; vel[j] += vt * 0.05 * mj
                nsum[i] += nrm; nsum[j] -= nrm; touch[i] = touch[j] = True
        fl = pos[:, 1] < YF; pos[fl, 1] = YF; vel[fl, 1] = np.maximum(vel[fl, 1], 0) * 0.05; nsum[fl] += [0, 1, 0]; touch |= fl
        for sgn in (-1, 1):
            wl = sgn * pos[:, 0] > XW; pos[wl, 0] = sgn * XW; vel[wl, 0] = 0; nsum[wl] += [-sgn, 0, 0]; touch |= wl
        pos[:, 2] += (zc - pos[:, 2]) * 0.5; vel[:, 2] = 0          # todos en la capa de la placa
        vel[touch & fr] *= (1 - 3.0 * dt)                           # roce: al apoyarse se van quedando quietos
        slow = touch & (np.linalg.norm(vel, axis=1) < 0.06) & (t > t0 + 1.5); vel[slow] = 0
        # giro: rodadura sobre lo que lo sostiene (eje z: en el plano), si no, giro lento que se frena
        for i in np.where(fr)[0]:
            if touch[i] and np.linalg.norm(nsum[i]) > 1e-6:
                n_ = nsum[i] / np.linalg.norm(nsum[i]); w_[i] = np.cross(n_, vel[i]) / R
            else: w_[i] *= (1 - 0.2 * dt)
            om = np.linalg.norm(w_[i])
            if om > 1e-6: quat[i] = qmul(qax(w_[i], om * dt), quat[i]); quat[i] /= np.linalg.norm(quat[i])
    P_[f] = pos; Q_[f] = quat
np.savez(os.path.join(OUTD, 'sim.npz'), P=P_, Q=Q_)
inside = (np.abs(P_[-1, :, 0]) < W_ / 2) & (np.abs(P_[-1, :, 1]) < H_ / 2)
d = np.linalg.norm(P_[-1][:, None] - P_[-1][None], axis=-1) + np.eye(N_) * 9
print('SIM ok: huevos %d, en cuadro al final %d, solape max %.3f R, vel final max %.3f, y max %.2f (borde %.2f)' % (
    N_, inside.sum(), max(0, (2 * R - d.min()) / R), np.abs(P_[-1] - P_[-2]).max() * FPS, P_[-1, :, 1].max(), H_ / 2))
if os.environ.get('SIMONLY'): raise SystemExit
# ---------------------------------------------------------------- instancias animadas
for i in range(N_):
    e = bpy.data.objects.new('egg%d' % i, None); e.instance_type = 'COLLECTION'; e.instance_collection = VARS[i % NV]; sc.collection.objects.link(e)
    e.rotation_mode = 'QUATERNION'
    for f in range(NF):
        e.location = P_[f, i]; e.rotation_quaternion = Q_[f, i]; e.keyframe_insert('location', frame=f + 1); e.keyframe_insert('rotation_quaternion', frame=f + 1)
    for fc in e.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# ---------------------------------------------------------------- logo en el fondo de la placa (bajo los huevos)
img = bpy.data.images.load(LOGO)
lo = bpy.data.objects.new('logo', bpy.data.meshes.new('logo')); sc.collection.objects.link(lo)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5); bm.to_mesh(lo.data); bm.free()
lo.data.uv_layers.new();
for poly in lo.data.polygons:
    for li in poly.loop_indices:
        v = lo.data.vertices[lo.data.loops[li].vertex_index].co; lo.data.uv_layers[0].data[li].uv = (v.x + 0.5, v.y + 0.5)
lo.scale = (LW, LH, 1); lo.location = (0, 0.4, -0.05)
lm, N, Lk = mat('logo'); tx = N.new('ShaderNodeTexImage'); tx.image = img
le = N.new('ShaderNodeEmission'); le.inputs['Color'].default_value = (0.95, 0.95, 0.97, 1); lt = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader')
sm = N.new('ShaderNodeMath'); sm.operation = 'MULTIPLY'; sm.inputs[1].default_value = float(os.environ.get('LOGOB', '0.85')); amr = N.new('ShaderNodeMapRange'); Lk.new(tx.outputs['Alpha'], amr.inputs[0]); amr.inputs[1].default_value = 0.15; amr.inputs[2].default_value = 0.6   # sin velo en los bordes del png
Lk.new(amr.outputs[0], sm.inputs[0])
Lk.new(amr.outputs[0], mx.inputs[0]); Lk.new(lt.outputs[0], mx.inputs[1]); Lk.new(le.outputs[0], mx.inputs[2]); Lk.new(sm.outputs[0], le.inputs['Strength'])
Lk.new(mx.outputs[0], N['Material Output'].inputs['Surface']); lo.data.materials.append(lm)
if os.environ.get('NOLOGO'): lo.hide_render = True
# ---------------------------------------------------------------- fondo de la placa (velo, aro de luz, fibras, polvo)
pl = bpy.data.objects.new('plate', bpy.data.meshes.new('plate')); sc.collection.objects.link(pl)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30); bm.to_mesh(pl.data); bm.free(); pl.location = (0, 0, -14)
pm, N, Lk = mat('plate'); g = G(N, Lk); tc = N.new('ShaderNodeTexCoord'); sx = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Object'], sx.inputs[0])
veil = g.rng(sx.outputs['X'], 6.0, -22.0, 0.0, 0.1); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.15; Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (0.8, 0.8, 0.72, 1)
Lk.new(g.m('MULTIPLY', veil, g.m('ADD', 0.6, g.m('MULTIPLY', nz.outputs['Fac'], 0.8))), e.inputs['Strength']); Lk.new(e.outputs[0], N['Material Output'].inputs['Surface']); pl.data.materials.append(pm)
# Fondo como en la foto real: todo esta muy fuera de foco, asi que se arma ya "desenfocado" (perfiles suaves en el
# shader) en vez de depender solo del foco de la camara: el aro de luz es una franja ancha de luz con nucleo blanco
# y bordes lila que se desvanecen; las fibras son cintas suaves con tramos brillantes; el polvo son manchas redondas
# difusas de varios tamanos (bokeh), algunas con el borde un poco mas marcado.
def strip_mesh(name, pts, width, z):
    me = bpy.data.meshes.new(name); vs = []; fs = []; uv = []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]; tg = (b - a).normalized(); nn = mathutils.Vector((-tg.y, tg.x, 0))
        vs += [(p + nn * width / 2).to_tuple(), (p - nn * width / 2).to_tuple()]
        if i: fs.append((2 * i - 2, 2 * i, 2 * i + 1, 2 * i - 1))
    me.from_pydata([(x, y, z) for x, y, _ in vs], [], fs); lay = me.uv_layers.new()
    L = sum((pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)); acc = [0.0]
    for i in range(len(pts) - 1): acc.append(acc[-1] + (pts[i + 1] - pts[i]).length)
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index; lay.data[li].uv = (acc[vi // 2] / L, vi % 2)
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); return o
def across(N, Lk, g):                                         # 0 en los bordes de la cinta, 1 en el centro
    tc = N.new('ShaderNodeTexCoord'); sx = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['UV'], sx.inputs[0])
    return g.m('SUBTRACT', 1.0, g.m('ABSOLUTE', g.m('SUBTRACT', g.m('MULTIPLY', sx.outputs['Y'], 2.0), 1.0))), sx.outputs['X']
# aro de luz: franja ancha (borde iluminado de la placa), arco que entra abajo y sube por la derecha
RC, RCX, RCY, RW_ = 25.0, -6.0, 8.0, 4.5
arc = [mathutils.Vector((RCX + RC * math.cos(a), RCY + RC * math.sin(a), 0)) for a in np.linspace(-2.25, 0.45, 200)]
ring = strip_mesh('ring', arc, RW_, -11.0)
rm, N, Lk = mat('ring'); g = G(N, Lk); xw, xu = across(N, Lk, g)
core = g.rng(xw, 0.3, 0.9); halo = g.rng(xw, 0.0, 0.6)
col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'; Lk.new(core, col.inputs['Factor']); col.inputs[6].default_value = (0.66, 0.62, 0.95, 1); col.inputs[7].default_value = (1.0, 0.98, 1.0, 1)
re_ = N.new('ShaderNodeEmission'); Lk.new(col.outputs[2], re_.inputs['Color'])
Lk.new(g.m('ADD', g.m('MULTIPLY', core, K('RINGC', '0.85')), g.m('MULTIPLY', halo, K('RINGH', '0.4'))), re_.inputs['Strength'])
rt = N.new('ShaderNodeBsdfTransparent'); ra = N.new('ShaderNodeAddShader'); Lk.new(rt.outputs[0], ra.inputs[0]); Lk.new(re_.outputs[0], ra.inputs[1]); Lk.new(ra.outputs[0], N['Material Output'].inputs['Surface'])
ring.data.materials.append(rm)
Rr = random.Random(5)
# fibras: cintas suaves, con tramos mas brillantes (nudos) a lo largo
fib, N, Lk = mat('fiber'); g = G(N, Lk); xw, xu = across(N, Lk, g)
bn = N.new('ShaderNodeTexNoise'); bn.inputs['Scale'].default_value = 9.0; bn.inputs['Detail'].default_value = 2
cm = N.new('ShaderNodeCombineXYZ'); Lk.new(xu, cm.inputs['X']); Lk.new(cm.outputs[0], bn.inputs['Vector'])
fe = N.new('ShaderNodeEmission'); fe.inputs['Color'].default_value = (0.9, 0.9, 0.85, 1)
Lk.new(g.m('MULTIPLY', g.rng(xw, 0.0, 1.0), g.m('ADD', 0.06, g.rng(bn.outputs['Fac'], 0.5, 0.72, 0.0, 0.35))), fe.inputs['Strength'])
ft = N.new('ShaderNodeBsdfTransparent'); fa = N.new('ShaderNodeAddShader'); Lk.new(ft.outputs[0], fa.inputs[0]); Lk.new(fe.outputs[0], fa.inputs[1]); Lk.new(fa.outputs[0], N['Material Output'].inputs['Surface'])
for (a, b_, w) in (((-19, -10), (-5, 11), 0.7), ((5, 10), (12, 2.5), 0.9), ((-15, -11), (-8, -3), 0.55)):
    A = mathutils.Vector((*a, 0)); B = mathutils.Vector((*b_, 0)); side = mathutils.Vector((-(B - A).y, (B - A).x, 0)).normalized()
    ph_ = Rr.uniform(0, 3); pts = [A.lerp(B, float(u)) + side * 0.35 * math.sin(float(u) * 2.0 + ph_) for u in np.linspace(0, 1, 40)]
    strip_mesh('fiber', pts, w, -9.0).data.materials.append(fib)
# polvo: manchas redondas difusas (bokeh) de varios tamanos
dmat, N, Lk = mat('bokeh'); g = G(N, Lk); tc = N.new('ShaderNodeTexCoord'); sx = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Generated'], sx.inputs[0])
dx = g.m('SUBTRACT', sx.outputs['X'], 0.5); dy = g.m('SUBTRACT', sx.outputs['Y'], 0.5); rr_ = g.m('MULTIPLY', g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dy, dy))), 2.0)
at_ = N.new('ShaderNodeAttribute'); at_.attribute_type = 'OBJECT'; at_.attribute_name = 'b'
disc = g.m('ADD', g.rng(rr_, 1.0, 0.55), g.m('MULTIPLY', g.rng(g.m('ABSOLUTE', g.m('SUBTRACT', rr_, 0.85)), 0.15, 0.0), 0.35))
de = N.new('ShaderNodeEmission'); de.inputs['Color'].default_value = (0.88, 0.88, 0.86, 1); Lk.new(g.m('MULTIPLY', disc, at_.outputs['Fac']), de.inputs['Strength'])
dt_ = N.new('ShaderNodeBsdfTransparent'); da = N.new('ShaderNodeAddShader'); Lk.new(dt_.outputs[0], da.inputs[0]); Lk.new(de.outputs[0], da.inputs[1]); Lk.new(da.outputs[0], N['Material Output'].inputs['Surface'])
dme = bpy.data.meshes.new('bokeh'); bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=1.0); bm.to_mesh(dme); bm.free(); dme.materials.append(dmat)
for _ in range(220):
    big = Rr.random() < 0.18; r_ = Rr.uniform(0.15, 0.45) if big else Rr.uniform(0.025, 0.09)
    o = bpy.data.objects.new('dust', dme); sc.collection.objects.link(o); o.location = (Rr.uniform(-18, 18), Rr.uniform(-11, 11), -8.5); o.scale = (r_, r_, 1)
    o['b'] = Rr.uniform(0.04, 0.12) if big else Rr.uniform(0.25, 0.9)
# ---------------------------------------------------------------- camara: lupa mirando hacia abajo, foco en la placa
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.005, 0.005, 1)
cd = bpy.data.cameras.new('cam'); cd.lens = 72; cd.sensor_width = 36
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); cam.location = (0, 0, 72 * W_ / 36 + R); sc.camera = cam
cd.dof.use_dof = True; cd.dof.focus_distance = cam.location.z - R; cd.dof.aperture_fstop = float(os.environ.get('FSTOP', '1.0'))
cd.clip_end = 500
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SPP; sc.cycles.use_denoising = SPP < 64
sc.cycles.max_bounces = 16; sc.cycles.transparent_max_bounces = 48
sc.render.resolution_x = RW; sc.render.resolution_y = RW * 9 // 16
sc.view_settings.view_transform = 'Standard'
sc.use_nodes = True; ct = sc.node_tree; ct.nodes.clear(); rl = ct.nodes.new('CompositorNodeRLayers')
gl = ct.nodes.new('CompositorNodeGlare'); gl.glare_type = 'FOG_GLOW'; gl.quality = 'MEDIUM'; gl.size = 7; gl.threshold = 0.6; gl.mix = -0.6
co = ct.nodes.new('CompositorNodeComposite'); ct.links.new(rl.outputs['Image'], gl.inputs['Image']); ct.links.new(gl.outputs['Image'], co.inputs['Image'])
sc.render.image_settings.file_format = 'JPEG' if os.environ.get('JPG') else 'PNG'
a, b = [int(x) for x in FR.split('-')]
for f in range(a, b + 1, STEP):
    out = os.path.join(OUTD, 'f_%04d' % f)
    if os.path.exists(out + ('.jpg' if os.environ.get('JPG') else '.png')): continue
    sc.frame_set(f); sc.render.filepath = out; bpy.ops.render.render(write_still=True); print('FRAME', f, flush=True)
print('DONE')
