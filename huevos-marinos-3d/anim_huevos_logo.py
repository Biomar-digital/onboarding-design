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
os.environ.setdefault('CIOR', '1.03'); os.environ.setdefault('CROUGH', '0.07'); os.environ.setdefault('YT', '0.9'); os.environ.setdefault('CT', '0.92')   # el interior del huevo atenua lo que hay detras: los huevos tapan el logo                         # menos lente: los huevos ya no 'agrandan' el logo como bolas blancas
exec(pre)
FPS, NF = 24, int(os.environ.get('NF', '408'))                # 17 s
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
# ---------------------------------------------------------------- simulacion (numpy): huevos hundiendose en agua
# Fisica de una esfera apenas mas densa que el agua: arrastre viscoso (se acerca a su velocidad limite en ~0.5 s, cada
# huevo con la suya), una corriente suave que los lleva desde arriba del cuadro hacia donde se posan, vaiven lento
# por la turbulencia del agua, giro lento que se frena por el agua. Al tocar la placa se posan sin rebotar y casi no
# se deslizan; si caen sobre otro huevo ruedan despacio hacia un costado y algunos quedan montados (se solapan en la
# imagen). Se posan en todo el cuadro, pero con menos densidad sobre el logo, para que siga leyendose entre huevos.
rng = np.random.default_rng(11)
W_, H_ = 30.0, 30.0 * 9 / 16                                   # campo visible en el plano de la placa
LW, LH = 18.0, 18.0 * 584 / 2000                               # logo en el fondo, centrado
LCX, LCY = 0.0, 0.4
def in_logo(x, y, m=0.0): return abs(x - LCX) < LW / 2 + m and abs(y - LCY) < LH / 2 + m
# los 8 del principio: sobre la placa, en los bordes, sin tapar el logo
start = [(-12.8, 6.6), (-9.3, 7.2), (-13.2, 2.9), (12.6, 6.4), (10.2, -6.8), (13.3, -3.5), (-12.3, -6.3), (-8.6, -7.3)]
NS = len(start)
# destinos: panal con jitter en todo el cuadro (lleno), pero dentro del logo se deja ~1 de cada 2.5 lugares; y unos
# cuantos extra caen sobre los demas (quedan montados: solape en la imagen)
tg = [np.array(p) for p in start]
dx_ = 2 * R * 1.04; dy_ = dx_ * math.sqrt(3) / 2
for r_ in range(-6, 7):
    for c_ in range(-9, 10):
        x = c_ * dx_ + (dx_ / 2 if r_ % 2 else 0) + rng.normal(0, 0.03 * R); y = r_ * dy_ + rng.normal(0, 0.03 * R)
        if abs(x) > W_ / 2 + 0.5 * R or abs(y) > H_ / 2 + 0.5 * R: continue
        if min(np.linalg.norm(np.array([x, y]) - q) for q in tg[:NS]) < 2.15 * R: continue
        if in_logo(x, y, 0.3) and rng.random() > float(os.environ.get('LOGOFILL', '0.4')): continue
        tg.append(np.array([x, y]))
for _ in range(6000):                                          # rellenar huecos (bordes y alrededor de los 8 iniciales)
    p = np.array([rng.uniform(-W_ / 2 - 0.5 * R, W_ / 2 + 0.5 * R), rng.uniform(-H_ / 2 - 0.5 * R, H_ / 2 + 0.5 * R)])
    if in_logo(*p, 0.3): continue
    if min(np.linalg.norm(p - q) for q in tg) >= (2.2 * R if any(np.linalg.norm(p - np.array(q)) < 3.2 * R for q in start) else 2.03 * R): tg.append(p)
for _ in range(int(os.environ.get('NTOP', '16'))):              # montados sobre otros, fuera del logo
    while True:
        p = np.array([rng.uniform(-W_ / 2, W_ / 2), rng.uniform(-H_ / 2, H_ / 2)])
        if not in_logo(*p, 0.5): break
    tg.append(p)
keep = []
for k_, p in enumerate(tg):                                    # nunca dos lugares en la placa a menos de un huevo
    if k_ < NS or k_ >= len(tg) - int(os.environ.get('NTOP', '16')) or all(np.linalg.norm(p - tg[q]) >= 2.0 * R for q in keep): keep.append(k_)
tg = np.array([tg[k_] for k_ in keep]); N_ = len(tg)
# Trayectorias planificadas (sin choques en el aire ni saltos): cada huevo arranca arriba del cuadro y cerca del lente,
# acelera en ~0.5 s hasta su velocidad limite de hundimiento (cada uno la suya), deriva en lo alto hacia su lugar con un
# vaiven suave que se apaga al bajar, frena los ultimos milimetros y se posa sin rebotar. Gira lento y el agua le va
# frenando el giro; al posarse rueda apenas en la direccion en que venia. Los "montados" se posan sobre dos vecinos.
NTOPN = int(os.environ.get('NTOP', '16')); base = tg[:N_ - NTOPN]; tops = []
for p in tg[N_ - NTOPN:]:                                      # lugar de apoyo sobre dos huevos posados
    d2 = np.linalg.norm(base - p, axis=1); a, b = np.argsort(d2)[:2]; A, B = base[a], base[b]; dd = np.linalg.norm(A - B)
    if dd > 2 * R * 1.9 or dd < 2 * R * 0.9: continue
    m = (A + B) / 2; z = R + math.sqrt(max((2 * R) ** 2 - (dd / 2) ** 2, 0))
    q = np.array([m[0], m[1], z])
    if all(np.linalg.norm(q - np.array([*o, R])) >= 2 * R * 0.995 for o in base) and all(np.linalg.norm(q - o) >= 2 * R for o in tops): tops.append(q)
TG = np.vstack([np.c_[base, np.full(len(base), R)], np.array(tops).reshape(-1, 3)]); N_ = len(TG)
DCAM = 72 * W_ / 36 + R
VS = rng.uniform(1.6, 2.4, N_); TAU = 0.45
t0 = np.zeros(N_); S0 = np.zeros((N_, 3))
order = list(np.argsort(TG[NS:len(base), 1] + rng.normal(0, 1.2, len(base) - NS)) + NS) + list(range(len(base), N_))
for k_, i in enumerate(order):
    z0 = rng.uniform(7.0, 10.0) * R; vis = (DCAM - z0) / DCAM * H_ / 2
    S0[i] = [TG[i, 0] + rng.normal(0, 0.3), vis + 1.6 * R + rng.uniform(0, 1.0), z0]   # cae en su columna: no se cruza con otros
    t0[i] = 0.4 + 5.6 * k_ / max(len(order) - 1, 1) + rng.uniform(-0.15, 0.15)
wob_f = rng.uniform(0.2, 0.4, (N_, 2)); wob_p = rng.uniform(0, 6.28, (N_, 2))
def path(i, t):
    """posicion del huevo i en el tiempo t (despues de soltarse)"""
    T = t - t0[i]; z0 = S0[i, 2]; zt = TG[i, 2]; H0 = z0 - zt
    fall = VS[i] * (T - TAU * (1 - math.exp(-T / TAU))) if T > 0 else 0.0   # arrastre: llega a velocidad limite en ~0.5 s
    land = 0.35 * R                                                         # ultimo tramo: frena (se posa sin rebote)
    if fall < H0 - land: z = z0 - fall
    else:
        T1 = None; z = zt + land * math.exp(-(fall - (H0 - land)) / land)
    u = min(max((z0 - z) / H0, 0), 1); hu = 1 - (1 - u) ** 2.2             # lo horizontal se hace en lo alto
    xy = S0[i, :2] + (TG[i, :2] - S0[i, :2]) * hu
    w = 0.22 * R * (1 - u) ** 1.5
    xy = xy + w * np.array([math.sin(6.283 * wob_f[i, 0] * T + wob_p[i, 0]), math.sin(6.283 * wob_f[i, 1] * T + wob_p[i, 1])])
    return np.array([xy[0], xy[1], z])
quat = np.zeros((N_, 4)); w_ = np.zeros((N_, 3))
def qmul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1*w2 - x1*x2 - y1*y2 - z1*z2, w1*x2 + x1*w2 + y1*z2 - z1*y2, w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2])
def qax(ax, an): ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax); return np.array([math.cos(an / 2), *(math.sin(an / 2) * ax)])
for i in range(N_):
    q = qax([0, 0, 1], rng.uniform(0, 6.28))
    if i >= NS: q = qmul(qax([rng.normal(), rng.normal(), 0], rng.uniform(0, 0.3)), q); w_[i] = [rng.normal(0, 0.12), rng.normal(0, 0.12), rng.normal(0, 0.45)]
    quat[i] = q
home = TG[:NS].copy(); wph = rng.uniform(0, 6.28, (NS, 2)); wfr = rng.uniform(0.15, 0.3, (NS, 2)); wspin = rng.uniform(-0.15, 0.15, NS)
def positions(t):
    pos = np.zeros((N_, 3))
    for i in range(N_):
        if i < NS: pos[i] = home[i] + np.array([0.1 * math.sin(6.283 * wfr[i, 0] * t + wph[i, 0]), 0.08 * math.sin(6.283 * wfr[i, 1] * t + wph[i, 1]), 0.0])
        elif t < t0[i]: pos[i] = S0[i]
        else: pos[i] = path(i, t)
    return pos
for it in range(80):                                           # si dos huevos se cruzan en el aire, el que sale despues espera
    bad = set()
    for f in range(0, NF, 2):
        t = f / FPS; pos = positions(t); act = np.array([i < NS or t >= t0[i] for i in range(N_)])
        vy = (DCAM - pos[:, 2]) / DCAM * H_ / 2 + R; act &= np.abs(pos[:, 1]) < vy   # fuera de cuadro no importa
        d = np.linalg.norm(pos[:, None] - pos[None], axis=-1) + np.eye(N_) * 99
        ii, jj = np.where(np.triu(d < 2 * R * 0.99) & act[:, None] & act[None])
        for a_, b_ in zip(ii, jj):
            late = a_ if t0[a_] >= t0[b_] else b_
            if late >= NS: bad.add(late)
    if not bad: break
    for i in bad: t0[i] += 0.1; VS[i] = min(VS[i], np.min(VS[[j for j in range(NS, N_) if t0[j] < t0[i]] or [i]]) + 0.05) if it > 40 else VS[i]
print('ajuste de salidas: %d pasadas' % (it + 1))
for i in bad: t0[i] = 1e9                                    # si alguno no encuentra hueco, no cae
print('conflictos que quedan:', sorted(bad)[:10], [(round(t0[i],2), np.round(TG[i],1).tolist()) for i in sorted(bad)[:4]])
P_ = np.zeros((NF, N_, 3)); Q_ = np.zeros((NF, N_, 4)); prev = None
for f in range(NF):
    t = f / FPS; pos = positions(t)
    if prev is not None:
        for i in range(N_):
            if i < NS: quat[i] = qmul(qax([0, 0, 1], wspin[i] / FPS), quat[i]); continue
            if t < t0[i]: continue
            v = (pos[i] - prev[i]) * FPS
            if pos[i, 2] < TG[i, 2] + 0.05 * R: w = np.cross([0, 0, 1.0], v) / R   # posado: rueda lo que le queda de movimiento
            else: w = w_[i] * math.exp(-(t - t0[i]) / 3.0) + np.cross([0, 0, 1.0], v) / R * 0.3
            om = np.linalg.norm(w)
            if om > 1e-6: quat[i] = qmul(qax(w, om / FPS), quat[i]); quat[i] /= np.linalg.norm(quat[i])
    P_[f] = pos; Q_[f] = quat; prev = pos
# control: que nunca se crucen (en el aire o al posarse)
def _md(f):
    t = f / FPS; act = np.array([i < NS or t >= t0[i] for i in range(N_)]); act &= np.abs(P_[f][:, 1]) < (DCAM - P_[f][:, 2]) / DCAM * H_ / 2 + R; X = P_[f][act]
    return (np.linalg.norm(X[:, None] - X[None], axis=-1) + np.eye(len(X)) * 99).min()
mind = min(_md(f) for f in range(0, NF, 2))
print('distancia minima entre huevos en toda la animacion: %.3f (2R = %.3f)' % (mind, 2 * R))
tg = TG[:, :2]
np.savez(os.path.join(OUTD, 'sim.npz'), P=P_, Q=Q_, T=tg)
fin = P_[-1]; d = np.linalg.norm(fin[:, None] - fin[None], axis=-1) + np.eye(N_) * 9
onlogo = sum(in_logo(x, y) for x, y, _ in fin)
print('SIM ok: huevos %d, sobre el logo %d, solape 3D max %.3f R, montados %d, vel final max %.3f, en placa final %d' % (
    N_, onlogo, max(0, (2 * R - d.min()) / R), int((fin[:, 2] > 1.3 * R).sum()), np.abs(P_[-1] - P_[-2]).max() * FPS, int((fin[:, 2] < 1.05 * R).sum())))
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
lo.scale = (LW, LH, 1); lo.location = (0, 0.4, -0.35)   # debajo de la base de los huevos (antes los cortaba y se veia por delante)
lm, N, Lk = mat('logo'); tx = N.new('ShaderNodeTexImage'); tx.image = img
le = N.new('ShaderNodeEmission'); le.inputs['Color'].default_value = (0.95, 0.95, 0.97, 1); lt = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader')
sm = N.new('ShaderNodeMath'); sm.operation = 'MULTIPLY'; sm.inputs[1].default_value = float(os.environ.get('LOGOB', '0.85')); amr = N.new('ShaderNodeMapRange'); Lk.new(tx.outputs['Alpha'], amr.inputs[0]); amr.inputs[1].default_value = 0.15; amr.inputs[2].default_value = 0.6   # sin velo en los bordes del png
lp_ = N.new('ShaderNodeLightPath'); dep = N.new('ShaderNodeMath'); dep.operation = 'ADD'; Lk.new(lp_.outputs['Transparent Depth'], dep.inputs[0]); Lk.new(lp_.outputs['Transmission Depth'], dep.inputs[1])
hd_ = N.new('ShaderNodeMath'); hd_.operation = 'MULTIPLY'; Lk.new(dep.outputs[0], hd_.inputs[0]); hd_.inputs[1].default_value = 0.25   # ~4 superficies por huevo
vis_ = N.new('ShaderNodeMath'); vis_.operation = 'POWER'; vis_.inputs[0].default_value = float(os.environ.get('THRU', '0.45')); Lk.new(hd_.outputs[0], vis_.inputs[1])   # cada huevo que hay delante deja pasar ~35%: se ve atenuado, no recortado   # visto a traves de un huevo: no se ve (los huevos lo tapan)
fac_ = N.new('ShaderNodeMath'); fac_.operation = 'MULTIPLY'; Lk.new(amr.outputs[0], fac_.inputs[0]); Lk.new(vis_.outputs[0], fac_.inputs[1])
Lk.new(fac_.outputs[0], sm.inputs[0])
Lk.new(fac_.outputs[0], mx.inputs[0]); Lk.new(lt.outputs[0], mx.inputs[1]); Lk.new(le.outputs[0], mx.inputs[2]); Lk.new(sm.outputs[0], le.inputs['Strength'])
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
