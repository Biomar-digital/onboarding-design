# BREAK THROUGH WINTER - estanque congelado de una granja en Dinamarca, hora azul (version hiperrealista, Cycles).
# Una trucha arcoiris rompe el hielo desde abajo y sube vertical en camara lenta.
#   blender -b -P escena_hielo.py -- trucha_rig.blend escena_hielo.blend CARPETA_RECURSOS
# CARPETA_RECURSOS (Poly Haven, CC0; ver descargar_recursos.sh):
#   winter_lake_01_4k.hdr, snow_02_{diff,nor_gl,rough}_2k.jpg, fir_tree_01_1k.blend (+ textures/)
# Render:  blender -b escena_hielo.blend -a          (animacion 8 s, 25 fps, 1080x1350, Cycles)
#          blender -b escena_hielo.blend -f 150      (foto: cuadro del apice)
# Unidades: la trucha mide 1,9 (unos 50 cm reales -> 1 unidad ~ 0,26 m). Hielo arriba en z = 0.
import bpy, sys, os, math, random, bmesh
import numpy as np
from mathutils import Vector, Euler, Matrix, Quaternion, noise as mnoise
A = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT, RES = A[0], A[1], A[2]
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type in ('CAMERA', 'LIGHT'): bpy.data.objects.remove(o)
rng = random.Random(11)
FPS, F0, F1 = 25, 1, 300                                                          # 12 s: nado bajo el hielo, subida y estallido en camara lenta
FB = 150                                                                          # cuadro en que revienta el hielo
sc.render.fps = FPS; sc.frame_start = F0; sc.frame_end = F1
G = 37.0; sc.gravity = (0, 0, -G)                                                 # 9,8 m/s2 en unidades
TH = 0.05                                                                         # espesor medio del hielo (~1,3 cm de hielo nuevo)
RF = 1.55                                                                         # radio de la zona fracturada
def lin(c): return tuple(((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in c)
def coll(name):
    c = bpy.data.collections.new(name); sc.collection.children.link(c); return c
C_ICE, C_ENV, C_FX = coll('HIELO'), coll('ENTORNO'), coll('AGUA_FX')

# ------------------------------------------------------------------ tiempo: rompe rapido y entra en camara lenta extrema
# salto a 45 grados: el centro del pez sale de (X0, Z0) bajo el hielo y llega al apice en ZAP
X0, Z0, ZAP, ANG = -0.95, -0.95, 0.72, math.radians(45)
VZ = math.sqrt(2 * G * (ZAP - Z0)); VX = VZ / math.tan(ANG); TAP = VZ / G
KF = [FB, FB + 10, FB + 95, F1 + 10]; KT = [0.0, 0.20, TAP, TAP + 0.045]
def ts(f):
    if f <= FB: return 0.0
    for i in range(len(KF) - 1):
        if f <= KF[i + 1]:
            u = (f - KF[i]) / (KF[i + 1] - KF[i])
            if i == 0: return KT[0] + (KT[1] - KT[0]) * (1 - (1 - u) ** 1.6)
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
def obj(name, me, mat=None, c=None):
    o = bpy.data.objects.new(name, me); (c or sc.collection).objects.link(o)
    if mat is not None: me.materials.append(mat)
    return o
def img(name, colorspace='sRGB'):
    i = bpy.data.images.load(os.path.join(RES, name), check_existing=True); i.colorspace_settings.name = colorspace; return i

# ------------------------------------------------------------------ cielo: HDRI real de lago congelado al atardecer, llevado a hora azul
hdr = img('winter_lake_01_4k.hdr', 'Linear Rec.709')
px = np.array(hdr.pixels[:], dtype=np.float32).reshape(hdr.size[1], hdr.size[0], 4)
lum = px[..., :3].sum(-1); iy, ix = np.unravel_index(np.argmax(lum), lum.shape); del px
u_sun = (ix + 0.5) / hdr.size[0]; a_sun = 2 * math.pi * (u_sun - 0.5)          # azimut del sol en el HDRI (atan2(y, -x))
TARGET = math.atan2(1.0, 0.55) - math.radians(50)                                                   # resplandor detras, a la izquierda del pez
w = bpy.data.worlds.new('cielo_hora_azul'); sc.world = w; w.use_nodes = True; wn = w.node_tree; wn.nodes.clear()
wo = N(wn, 'ShaderNodeOutputWorld'); bg = N(wn, 'ShaderNodeBackground'); wn.links.new(bg.outputs[0], wo.inputs[0])
wtc = N(wn, 'ShaderNodeTexCoord'); wmp = N(wn, 'ShaderNodeMapping'); wn.links.new(wtc.outputs['Generated'], wmp.inputs['Vector'])
wmp.inputs['Rotation'].default_value = (0, 0, a_sun - TARGET)                 # deja de fondo la linea de arboles del HDRI (sin edificios)
env = N(wn, 'ShaderNodeTexEnvironment'); env.image = hdr; wn.links.new(wmp.outputs[0], env.inputs['Vector'])
hs = N(wn, 'ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = 0.85; wn.links.new(env.outputs[0], hs.inputs['Color'])
blue = mix(wn, 0.78, hs.outputs[0], lin((70, 112, 210)), 'MULTIPLY')             # hora azul: el atardecer pasa a azul profundo
wsep = N(wn, 'ShaderNodeSeparateXYZ'); wn.links.new(wtc.outputs['Generated'], wsep.inputs[0])
zen = smooth(wn, wsep.outputs[2], 0.02, 0.6)                                     # cielo alto mas oscuro
dark = mix(wn, M(wn, 'MULTIPLY', zen, 0.55), blue, lin((4, 10, 30)), 'MULTIPLY')
wn.links.new(dark, bg.inputs['Color']); bg.inputs['Strength'].default_value = 0.52

# ------------------------------------------------------------------ hielo: material fisico (hielo transparente sobre agua negra) con nieve, burbujas y grietas
ice_c, ice_n, ice_r = img('Ice003_2K-JPG_Color.jpg'), img('Ice003_2K-JPG_NormalGL.jpg', 'Non-Color'), img('Ice003_2K-JPG_Roughness.jpg', 'Non-Color')
snow_d, snow_n, snow_r = img('snow_02_diff_2k.jpg'), img('snow_02_nor_gl_2k.jpg', 'Non-Color'), img('snow_02_rough_2k.jpg', 'Non-Color')
crack_val = []
def ice_material(name, sides=False, frost=0.0, trans=0.35, snow_top=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = N(nt, 'ShaderNodeOutputMaterial')
    at = N(nt, 'ShaderNodeAttribute'); at.attribute_name = 'pos0'; P = at.outputs['Vector']   # posicion original (viaja con las esquirlas)
    sp = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(P, sp.inputs[0]); X, Y = sp.outputs[0], sp.outputs[1]
    R = M(nt, 'SQRT', M(nt, 'ADD', M(nt, 'MULTIPLY', X, X), M(nt, 'MULTIPLY', Y, Y)))
    n1 = N(nt, 'ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.09; n1.inputs['Detail'].default_value = 10.0; n1.inputs['Roughness'].default_value = 0.6; nt.links.new(P, n1.inputs['Vector'])
    n2 = N(nt, 'ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 2.5; n2.inputs['Detail'].default_value = 12.0; nt.links.new(P, n2.inputs['Vector'])
    # hielo: agua congelada transparente, apenas azulada; abajo hay agua negra -> "hielo negro" con reflejos del cielo
    # superficie: foto real de hielo negro de lago (ambientCG Ice003), en dos escalas para que no se note la repeticion
    ice = N(nt, 'ShaderNodeBsdfPrincipled'); ice.inputs['IOR'].default_value = 1.31; ice.inputs['Transmission Weight'].default_value = trans
    ims = []
    for sc_, rot_ in ((1 / 5.5, 0.0), (1 / 13.0, 1.1)):
        mp_ = N(nt, 'ShaderNodeMapping'); mp_.inputs['Scale'].default_value = (sc_, sc_, sc_); mp_.inputs['Rotation'].default_value = (0, 0, rot_); nt.links.new(P, mp_.inputs['Vector'])
        tt = {}
        for key, im_ in (('c', ice_c), ('r', ice_r), ('n', ice_n)):
            t_ = N(nt, 'ShaderNodeTexImage'); t_.image = im_; nt.links.new(mp_.outputs[0], t_.inputs['Vector']); tt[key] = t_.outputs[0]
        ims.append(tt)
    sel = smooth(nt, n1.outputs['Fac'], 0.42, 0.58)
    icol = mix(nt, sel, ims[0]['c'], ims[1]['c'])
    ihs = N(nt, 'ShaderNodeHueSaturation'); ihs.inputs['Saturation'].default_value = 0.30; ihs.inputs['Value'].default_value = 1.15; nt.links.new(icol, ihs.inputs['Color'])
    nt.links.new(mix(nt, 0.85, ihs.outputs[0], lin((150, 186, 230)), 'MULTIPLY'), ice.inputs['Base Color'])
    irough = mix(nt, sel, ims[0]['r'], ims[1]['r'])
    nt.links.new(M(nt, 'ADD', 0.02, M(nt, 'MULTIPLY', irough, 0.55)), ice.inputs['Roughness'])
    inorm = N(nt, 'ShaderNodeNormalMap'); inorm.inputs['Strength'].default_value = 0.6; nt.links.new(mix(nt, sel, ims[0]['n'], ims[1]['n']), inorm.inputs['Color'])
    ice.inputs['Coat Weight'].default_value = 0.5; ice.inputs['Coat Roughness'].default_value = 0.04
    wv = N(nt, 'ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 3.0; wv.inputs['Distortion'].default_value = 18.0; wv.inputs['Detail'].default_value = 6.0; nt.links.new(P, wv.inputs['Vector'])
    # grietas viejas de presion: planos blancos dentro del hielo
    vo = N(nt, 'ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 0.16
    pw = N(nt, 'ShaderNodeVectorMath'); pw.operation = 'ADD'; nt.links.new(P, pw.inputs[0]); nt.links.new(n1.outputs['Color'], pw.inputs[1]); nt.links.new(pw.outputs[0], vo.inputs['Vector'])
    old = M(nt, 'MULTIPLY', smooth(nt, vo.outputs['Distance'], 0.006, 0.0), smooth(nt, n2.outputs['Fac'], 0.35, 0.6))
    # grietas nuevas radiales desde el agujero (crecen con 'radio_grietas')
    rv = N(nt, 'ShaderNodeValue'); rv.name = 'radio_grietas'; crack_val.append(rv)
    ang = M(nt, 'ARCTAN2', Y, X)
    pol = N(nt, 'ShaderNodeCombineXYZ'); nt.links.new(M(nt, 'MULTIPLY', ang, 2.4), pol.inputs[0]); nt.links.new(M(nt, 'MULTIPLY', M(nt, 'LOGARITHM', M(nt, 'ADD', R, 0.1), 2.718), 2.8), pol.inputs[1])
    n3 = N(nt, 'ShaderNodeTexNoise'); n3.inputs['Scale'].default_value = 1.4; n3.inputs['Detail'].default_value = 5.0; nt.links.new(P, n3.inputs['Vector'])
    pw2 = N(nt, 'ShaderNodeVectorMath'); pw2.operation = 'MULTIPLY_ADD'; nt.links.new(n3.outputs['Color'], pw2.inputs[0]); pw2.inputs[1].default_value = (0.5, 0.5, 0.5); nt.links.new(pol.outputs[0], pw2.inputs[2])
    vr = N(nt, 'ShaderNodeTexVoronoi'); vr.feature = 'DISTANCE_TO_EDGE'; vr.inputs['Scale'].default_value = 1.3; nt.links.new(pw2.outputs[0], vr.inputs['Vector'])
    cw = M(nt, 'MULTIPLY', 0.005, M(nt, 'ADD', 1.0, M(nt, 'MULTIPLY', R, -0.12)))
    new = M(nt, 'MAXIMUM', smooth(nt, M(nt, 'SUBTRACT', vr.outputs['Distance'], cw), 0.0, -0.003),
            M(nt, 'MULTIPLY', smooth(nt, M(nt, 'SUBTRACT', vr.outputs['Distance'], M(nt, 'MULTIPLY', cw, 5.0)), 0.0, -0.012), 0.25))
    new = M(nt, 'MULTIPLY', new, M(nt, 'MULTIPLY', smooth(nt, M(nt, 'SUBTRACT', R, rv.outputs[0]), 0.0, -0.4), smooth(nt, R, RF - 0.1, RF + 0.1)))
    crack = M(nt, 'MINIMUM', M(nt, 'ADD', M(nt, 'MULTIPLY', old, 0.0), M(nt, 'MULTIPLY', new, 0.65)), 1.0)
    if frost: crack = M(nt, 'MAXIMUM', crack, M(nt, 'MULTIPLY', smooth(nt, n2.outputs['Fac'], 0.3, 0.7), frost))   # hielo roto: lechoso
    frac = N(nt, 'ShaderNodeBsdfPrincipled'); frac.inputs['Base Color'].default_value = (*lin((228, 238, 246)), 1); frac.inputs['Roughness'].default_value = 0.45
    frac.inputs['Subsurface Weight'].default_value = 0.6; frac.inputs['Subsurface Radius'].default_value = (0.05, 0.07, 0.09)
    # burbujas de aire atrapadas: puntitos blancos lechosos en racimos
    vb = N(nt, 'ShaderNodeTexVoronoi'); vb.inputs['Scale'].default_value = 26.0; vb.inputs['Randomness'].default_value = 1.0; nt.links.new(P, vb.inputs['Vector'])
    bsep = N(nt, 'ShaderNodeSeparateColor'); nt.links.new(vb.outputs['Color'], bsep.inputs[0])
    bub = M(nt, 'MULTIPLY', smooth(nt, vb.outputs['Distance'], 0.06, 0.02), smooth(nt, bsep.outputs[1], 0.55, 0.6))
    bub = M(nt, 'MULTIPLY', bub, smooth(nt, n1.outputs['Fac'], 0.42, 0.62))
    # nieve soplada en vetas y parches (textura real de Poly Haven), mas nieve lejos
    mp = N(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.17, 0.17, 0.17); nt.links.new(P, mp.inputs['Vector'])
    td = N(nt, 'ShaderNodeTexImage'); td.image = snow_d; tn = N(nt, 'ShaderNodeTexImage'); tn.image = snow_n; tr = N(nt, 'ShaderNodeTexImage'); tr.image = snow_r
    for t in (td, tn, tr): nt.links.new(mp.outputs[0], t.inputs['Vector'])
    snow = N(nt, 'ShaderNodeBsdfPrincipled'); nt.links.new(td.outputs[0], snow.inputs['Base Color']); nt.links.new(tr.outputs[0], snow.inputs['Roughness'])
    snow.inputs['Subsurface Weight'].default_value = 0.35; snow.inputs['Subsurface Radius'].default_value = (0.1, 0.12, 0.15)
    nm = N(nt, 'ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.8; nt.links.new(tn.outputs[0], nm.inputs['Color']); nt.links.new(nm.outputs[0], snow.inputs['Normal'])
    streak = N(nt, 'ShaderNodeTexNoise'); streak.inputs['Scale'].default_value = 0.6; streak.inputs['Detail'].default_value = 8.0
    smp = N(nt, 'ShaderNodeMapping'); smp.inputs['Scale'].default_value = (1.0, 0.18, 1.0); smp.inputs['Rotation'].default_value = (0, 0, 0.5); nt.links.new(P, smp.inputs['Vector']); nt.links.new(smp.outputs[0], streak.inputs['Vector'])
    snow_m = smooth(nt, M(nt, 'ADD', M(nt, 'MULTIPLY', streak.outputs['Fac'], 0.75), M(nt, 'MULTIPLY', n1.outputs['Fac'], 0.45)), 0.64, 0.76)
    far = smooth(nt, R, 25.0, 220.0)
    snow_m = M(nt, 'MAXIMUM', snow_m, M(nt, 'MULTIPLY', far, smooth(nt, streak.outputs['Fac'], 0.45, 0.62)))
    snow_m = M(nt, 'MULTIPLY', snow_m, smooth(nt, R, 0.9, 2.2))                    # junto al agujero no hay nieve (la barrio el agua)
    if snow_top:                                                                      # placas rotas: capa de nieve arriba (normal en espacio objeto)
        tcn = N(nt, 'ShaderNodeTexCoord'); nsz = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(tcn.outputs['Normal'], nsz.inputs[0])
        snow_m = M(nt, 'MAXIMUM', snow_m, M(nt, 'MULTIPLY', smooth(nt, nsz.outputs[2], 0.6, 0.85), M(nt, 'MULTIPLY', smooth(nt, n2.outputs['Fac'], 0.30, 0.55), snow_top)))
    sh = N(nt, 'ShaderNodeMixShader'); nt.links.new(crack, sh.inputs[0]); nt.links.new(ice.outputs[0], sh.inputs[1]); nt.links.new(frac.outputs[0], sh.inputs[2])
    sh2 = N(nt, 'ShaderNodeMixShader'); nt.links.new(bub, sh2.inputs[0]); nt.links.new(sh.outputs[0], sh2.inputs[1]); nt.links.new(frac.outputs[0], sh2.inputs[2])
    sh3 = N(nt, 'ShaderNodeMixShader'); nt.links.new(snow_m, sh3.inputs[0]); nt.links.new(sh2.outputs[0], sh3.inputs[1]); nt.links.new(snow.outputs[0], sh3.inputs[2])
    bump = N(nt, 'ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.12; bump.inputs['Distance'].default_value = 0.01
    nt.links.new(M(nt, 'ADD', M(nt, 'MULTIPLY', wv.outputs['Fac'], 0.25), M(nt, 'MULTIPLY', n2.outputs['Fac'], 0.6)), bump.inputs['Height'])
    nt.links.new(inorm.outputs[0], bump.inputs['Normal'])
    for b in (ice, frac): nt.links.new(bump.outputs[0], b.inputs['Normal'])
    res = sh3.outputs[0]
    if sides:                                                                        # caras de fractura: blanco-azuladas, esmeriladas
        geo = N(nt, 'ShaderNodeNewGeometry'); gz = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'], gz.inputs[0])
        side = smooth(nt, M(nt, 'ABSOLUTE', gz.outputs[2]), 0.7, 0.3)
        fr2 = N(nt, 'ShaderNodeBsdfPrincipled'); fr2.inputs['Base Color'].default_value = (*lin((240, 246, 250)), 1); fr2.inputs['Roughness'].default_value = 0.5
        fr2.inputs['Transmission Weight'].default_value = 0.0; fr2.inputs['IOR'].default_value = 1.31
        fr2.inputs['Subsurface Weight'].default_value = 1.0; fr2.inputs['Subsurface Radius'].default_value = (0.03, 0.045, 0.06)
        nb = N(nt, 'ShaderNodeBump'); nb.inputs['Strength'].default_value = 0.5; nb.inputs['Distance'].default_value = 0.02; nt.links.new(n2.outputs['Fac'], nb.inputs['Height']); nt.links.new(nb.outputs[0], fr2.inputs['Normal'])
        sh4 = N(nt, 'ShaderNodeMixShader'); nt.links.new(side, sh4.inputs[0]); nt.links.new(res, sh4.inputs[1]); nt.links.new(fr2.outputs[0], sh4.inputs[2])
        res = sh4.outputs[0]
    # cara de abajo (vista desde el agua): hielo claro con burbujas plateadas; la nieve de arriba tapa la luz
    tcb = N(nt, 'ShaderNodeTexCoord'); nbz = N(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(tcb.outputs['Normal'], nbz.inputs[0])
    under = smooth(nt, nbz.outputs[2], -0.5, -0.8)
    bot = N(nt, 'ShaderNodeBsdfPrincipled'); bot.inputs['Base Color'].default_value = (*lin((200, 225, 235)), 1); bot.inputs['Roughness'].default_value = 0.06
    bot.inputs['Transmission Weight'].default_value = 1.0; bot.inputs['IOR'].default_value = 1.31
    nt.links.new(inorm.outputs[0], bot.inputs['Normal'])
    silver = N(nt, 'ShaderNodeBsdfPrincipled'); silver.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 1); silver.inputs['Metallic'].default_value = 0.6; silver.inputs['Roughness'].default_value = 0.15
    bmx = N(nt, 'ShaderNodeMixShader'); nt.links.new(M(nt, 'MINIMUM', M(nt, 'MULTIPLY', bub, 2.0), 1.0), bmx.inputs[0]); nt.links.new(bot.outputs[0], bmx.inputs[1]); nt.links.new(silver.outputs[0], bmx.inputs[2])
    # el techo de hielo brilla con la luz del cielo que lo atraviesa; la nieve encima lo oscurece; grietas y burbujas se recortan claras
    glow = M(nt, 'MULTIPLY', M(nt, 'SUBTRACT', 1.0, M(nt, 'MULTIPLY', snow_m, 0.9)), M(nt, 'ADD', 1.0, M(nt, 'ADD', M(nt, 'MULTIPLY', crack, 3.0), M(nt, 'MULTIPLY', bub, 1.5))))
    glow = M(nt, 'MULTIPLY', glow, M(nt, 'ADD', 0.75, M(nt, 'MULTIPLY', ims[0]['r'], 0.5)))   # variacion de la textura real del hielo
    em_ = N(nt, 'ShaderNodeEmission'); em_.inputs['Color'].default_value = (*lin((120, 168, 182)), 1); nt.links.new(M(nt, 'MULTIPLY', glow, 0.32), em_.inputs['Strength'])
    bmx2 = N(nt, 'ShaderNodeAddShader'); nt.links.new(bmx.outputs[0], bmx2.inputs[0]); nt.links.new(em_.outputs[0], bmx2.inputs[1])
    fin = N(nt, 'ShaderNodeMixShader'); nt.links.new(under, fin.inputs[0]); nt.links.new(res, fin.inputs[1]); nt.links.new(bmx2.outputs[0], fin.inputs[2])
    nt.links.new(fin.outputs[0], out.inputs[0])
    return m
m_ice = ice_material('hielo'); m_cell = ice_material('hielo_placas', sides=True, frost=0.08, trans=1.0, snow_top=0.35)
def add_pos0(me, off=(0, 0, 0)):
    a = me.attributes.new('pos0', 'FLOAT_VECTOR', 'POINT')
    a.data.foreach_set('vector', (np.array([v.co[:] for v in me.vertices], dtype=np.float32) + np.array(off, dtype=np.float32)).ravel())

# losa grande del estanque con un hueco poligonal donde van las placas fracturadas
NPOLY = 48; A0 = math.radians(225)
ring = [(RF * math.cos(A0 + 2 * math.pi * i / NPOLY), RF * math.sin(A0 + 2 * math.pi * i / NPOLY)) for i in range(NPOLY)]
PS = 1500.0
me = bpy.data.meshes.new('hielo'); bm = bmesh.new()
outer = [bm.verts.new((x, y, 0)) for x, y in ((-PS, -PS), (PS, -PS), (PS, PS), (-PS, PS))]
inner = [bm.verts.new((x, y, 0)) for x, y in ring]
for q in range(4):
    a0, a1 = q * NPOLY // 4, (q + 1) * NPOLY // 4
    bm.faces.new([outer[(q + 1) % 4], outer[q]] + [inner[i % NPOLY] for i in range(a0, a1 + 1)])
for f in bm.faces:
    if f.normal.z < 0: f.normal_flip()
bmesh.ops.triangulate(bm, faces=bm.faces[:])
ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:]); bmesh.ops.translate(bm, vec=(0, 0, -TH), verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
add_pos0(me); ice = obj('HIELO_estanque', me, m_ice, C_ICE)

# placas fracturadas (Voronoi 2D dentro del poligono): las de adentro vuelan, las del borde se levantan y se hunden a medias
def clip(poly, a, b):
    m_ = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); nrm = (b[0] - a[0], b[1] - a[1]); out = []
    def side(p): return (p[0] - m_[0]) * nrm[0] + (p[1] - m_[1]) * nrm[1]
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]; sp_, sq = side(p), side(q)
        if sp_ <= 0: out.append(p)
        if sp_ * sq < 0:
            t = sp_ / (sp_ - sq); out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out
seeds = []
for i in range(14): a = rng.uniform(0, 6.283); r = rng.uniform(0.06, 0.45); seeds.append((r * math.cos(a), r * math.sin(a)))
for i in range(22): a = 2 * math.pi * i / 22 + rng.uniform(-0.15, 0.15); r = rng.uniform(0.55, 0.85); seeds.append((r * math.cos(a), r * math.sin(a)))
for i in range(26): a = 2 * math.pi * i / 26 + rng.uniform(-0.12, 0.12); r = rng.uniform(1.05, 1.40); seeds.append((r * math.cos(a), r * math.sin(a)))
def edge_jit(p, q, j, n):                                                      # mismo quiebre en los dos lados de una grieta
    kp, kq = tuple(round(c, 4) for c in p), tuple(round(c, 4) for c in q); fwd = kp <= kq
    idx = j if fwd else n - j
    return random.Random(str((min(kp, kq), max(kp, kq), idx))).uniform(-0.012, 0.012), fwd
cells = []
for i, s in enumerate(seeds):
    poly = list(ring)
    for j, t in enumerate(seeds):
        if i != j and len(poly) > 2: poly = clip(poly, s, t)
    if len(poly) < 3: continue
    cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
    pts = []
    for k in range(len(poly)):
        p, q = poly[k], poly[(k + 1) % len(poly)]; L = math.dist(p, q); n_ = max(1, int(L / 0.06))
        nx, ny = -(q[1] - p[1]) / (L + 1e-9), (q[0] - p[0]) / (L + 1e-9)
        for j in range(n_):
            t = j / n_
            if j == 0: jit = 0.0
            else:
                jit, fwd = edge_jit(p, q, j, n_); jit = jit if fwd else -jit
            pts.append((p[0] + (q[0] - p[0]) * t + nx * jit - cx, p[1] + (q[1] - p[1]) * t + ny * jit - cy))
    me = bpy.data.meshes.new(f'placa{i}'); bm = bmesh.new(); th_k = rng.uniform(0.6, 1.3)
    top = bm.faces.new([bm.verts.new((x, y, 0.0)) for x, y in pts])
    ext = bmesh.ops.extrude_face_region(bm, geom=[top]); bmesh.ops.translate(bm, vec=(0, 0, -TH), verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    for v in bm.verts:                                                           # quiebre irregular: mismo ruido en los dos lados de cada grieta
        wp = Vector((v.co.x + cx, v.co.y + cy, v.co.z)); nv = mnoise.noise_vector(wp * 9.0)
        v.co.x += nv.x * 0.016; v.co.y += nv.y * 0.016
        if v.co.z < -0.01:                                                       # cara de abajo: espesor irregular (0,4 a 1,7 veces), mas fino en algunos bordes
            n1_ = mnoise.noise(wp * 4.0); n2_ = mnoise.noise(wp * 13.0)
            v.co.z = -TH * th_k * max(0.35, 1.0 + 0.55 * n1_ + 0.25 * n2_)
        else: v.co.z += nv.z * 0.003
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(me); bm.free(); add_pos0(me, (cx, cy, 0))
    o = obj(f'HIELO_placa_{i:02d}', me, m_cell, C_ICE); o.location = (cx, cy, 0.0); o.rotation_mode = 'XYZ'
    cells.append((o, math.hypot(cx, cy), math.atan2(cy, cx)))
for o, r0, a0 in cells:
    out = Vector((math.cos(a0), math.sin(a0), 0)); tang = Vector((-math.sin(a0), math.cos(a0), 0))
    vout = Vector((out.x, max(out.y, 0.15), 0)).normalized()                     # no vuelan hacia la camara (taparian al pez)
    fly = r0 < 0.5 or (r0 < 0.95 and rng.random() < 0.6)
    p = Vector(o.location); rot = Vector((0, 0, 0)); home = Vector(o.location)
    if fly:
        v = vout * rng.uniform(1.0, 5.0) * (0.4 + r0) + Vector((rng.uniform(0.5, 2.5), rng.uniform(0.5, 2.0), rng.uniform(4.0, 10.0) * (1.3 - 0.6 * r0)))
        wv_ = Vector((rng.uniform(-16, 16), rng.uniform(-16, 16), rng.uniform(-6, 6)))
    tilt_max = 0.0 if fly else (rng.uniform(0.25, 0.55) if r0 < 1.1 else rng.uniform(0.04, 0.14))
    t_prev = 0.0; landed = False; sunk = False
    for f in range(F0, F1 + 1):
        t = ts(f); dt = t - t_prev; t_prev = t
        gap = 1.003 - 0.014 * min(1.0, max(0.0, (f - (FB - 38)) / 38.0))            # las grietas se abren antes de romper
        if fly and f > FB and not landed and not sunk and dt > 0:
            for _ in range(4):
                h = dt / 4; v.z -= G * h; p += v * h; rot += wv_ * h
                rr = math.hypot(p.x, p.y)
                if p.z < 0.02 and v.z < 0:
                    if rr > RF + 0.1:
                        p.z = 0.02; v.z *= -0.2; v.x *= 0.5; v.y *= 0.5; wv_ *= 0.35
                        if abs(v.z) < 1.0: landed = True; rot.x = round(rot.x / math.pi) * math.pi; rot.y = round(rot.y / math.pi) * math.pi
                    elif p.z < -0.6: sunk = True
            o.location = p; o.rotation_euler = rot
        elif not fly:
            k = 0.0 if f <= FB else min(1.0, t / 0.06)
            settle = 0.0 if f <= FB else max(0.0, min(1.0, (t - 0.06) / 0.25))
            ang = tilt_max * (k - 0.55 * settle)                                     # el borde interior sube y vuelve a bajar a medias
            o.rotation_euler = Quaternion(tang, ang).to_euler()
            o.location = home + out * (0.03 * k) + Vector((0, 0, -0.06 * settle if tilt_max > 0.2 else 0.0))
        o.scale = (gap, gap, 1.0)
        for dp in ('location', 'rotation_euler', 'scale'): o.keyframe_insert(dp, frame=f)
        o.hide_render = fly and sunk; o.keyframe_insert('hide_render', frame=f)

# agua: negra bajo el hielo, y una superficie con ondas dentro del agujero
m_w, nt, bs = new_mat('agua')
bs.inputs['Base Color'].default_value = (1, 1, 1, 1); bs.inputs['Roughness'].default_value = 0.01; bs.inputs['IOR'].default_value = 1.333; bs.inputs['Transmission Weight'].default_value = 1.0
bs.inputs['Specular IOR Level'].default_value = 0.5
wtc2 = N(nt, 'ShaderNodeTexCoord'); wave = N(nt, 'ShaderNodeTexWave'); wave.wave_type = 'RINGS'; wave.inputs['Scale'].default_value = 2.2; wave.inputs['Distortion'].default_value = 3.0
nt.links.new(wtc2.outputs['Object'], wave.inputs['Vector'])
for f, ph in ((FB, 0.0), (F1, -14.0)): wave.inputs['Phase Offset'].default_value = ph; wave.inputs['Phase Offset'].keyframe_insert('default_value', frame=f)
wb = N(nt, 'ShaderNodeBump'); wb.inputs['Strength'].default_value = 0.3; nt.links.new(wave.outputs['Fac'], wb.inputs['Height']); nt.links.new(wb.outputs[0], bs.inputs['Normal'])
me = bpy.data.meshes.new('agua'); bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=RF + 0.05); bm.to_mesh(me); bm.free()
water = obj('AGUA_agujero', me, m_w, C_ICE); water.location.z = -0.035
for f, h in ((F0, True), (FB, True), (FB + 1, False)): water.hide_render = h; water.keyframe_insert('hide_render', frame=f)   # desde abajo taparia la vista
me = bpy.data.meshes.new('fondo'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=PS); bm.to_mesh(me); bm.free()
m_deep, nt, bs = new_mat('agua_profunda'); bs.inputs['Base Color'].default_value = (0.0, 0.003, 0.006, 1); bs.inputs['Roughness'].default_value = 0.3
deep = obj('AGUA_debajo', me, m_deep, C_ICE); deep.location.z = -TH - 0.02
for f, r in ((1, RF), (FB - 38, RF), (FB - 22, RF + 0.8), (FB - 10, RF + 1.6), (FB, RF + 2.6), (FB + 34, RF + 3.4), (F1, RF + 3.6)):
    for rv in crack_val: rv.outputs[0].default_value = r; rv.outputs[0].keyframe_insert('default_value', frame=f)

# ------------------------------------------------------------------ orilla nevada, abetos reales (Poly Haven) y juncos secos atrapados en el hielo
m_snow, nt, bs = new_mat('nieve')
tco = N(nt, 'ShaderNodeTexCoord'); mp = N(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.08, 0.08, 0.08); nt.links.new(tco.outputs['Object'], mp.inputs['Vector'])
for im_, sock in ((snow_d, 'Base Color'), (snow_r, 'Roughness')):
    t = N(nt, 'ShaderNodeTexImage'); t.image = im_; nt.links.new(mp.outputs[0], t.inputs['Vector']); nt.links.new(t.outputs[0], bs.inputs[sock])
t = N(nt, 'ShaderNodeTexImage'); t.image = snow_n; nt.links.new(mp.outputs[0], t.inputs['Vector']); nm = N(nt, 'ShaderNodeNormalMap'); nt.links.new(t.outputs[0], nm.inputs['Color']); nt.links.new(nm.outputs[0], bs.inputs['Normal'])
bs.inputs['Subsurface Weight'].default_value = 0.3
POND = 140.0                                                                    # radio del estanque (~36 m)
me = bpy.data.meshes.new('orilla'); bm = bmesh.new(); NA, NRr = 256, 40
nz = lambda x, y: (math.sin(x * 0.031) * 0.8 + math.sin(y * 0.047 + 1.3) * 0.6 + math.sin((x + y) * 0.013) * 1.2)
vg = []
for j in range(NRr + 1):
    rr = POND * (0.97 + 0.01 * j) if j < 4 else POND + (j - 3) ** 1.6 * 18.0
    row = []
    for i in range(NA):
        a = 2 * math.pi * i / NA; wob = 1.0 + 0.10 * math.sin(3 * a + 0.7) + 0.05 * math.sin(7 * a)
        R_ = rr * wob; x, y = R_ * math.cos(a), R_ * math.sin(a) + 30.0
        hgt = 0.0 if j < 2 else min(1.0, (j - 1) / 5.0) ** 1.5 * (2.2 + 0.8 * nz(x, y)) * (1.0 if j < 12 else max(0.25, 1 - (j - 12) / 30))
        row.append(bm.verts.new((x, y, hgt + (0.03 if j == 0 else 0.0))))
    vg.append(row)
for j in range(NRr):
    for i in range(NA): bm.faces.new((vg[j][i], vg[j][(i + 1) % NA], vg[j + 1][(i + 1) % NA], vg[j + 1][i]))
bm.to_mesh(me); bm.free()
bank = obj('ENTORNO_orilla_nevada', me, m_snow, C_ENV)
for p in me.polygons: p.use_smooth = True
fir_path = os.path.join(RES, 'fir_tree_01_1k.blend')
with bpy.data.libraries.load(fir_path, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in ('fir_tree_01_a_LOD1', 'fir_tree_01_b_LOD1', 'fir_tree_01_c_LOD1')]
firs = [o for o in dst.objects if o is not None]
for im_ in bpy.data.images:
    if im_.filepath.startswith('//textures/'): im_.filepath = os.path.join(RES, 'textures', os.path.basename(im_.filepath))
FIR_SCALE = 1 / 0.26                                                            # los abetos estan en metros
for k in range(90):
    a = math.radians(rng.choice([rng.uniform(25, 68), rng.uniform(112, 160)]))
    rr = rng.uniform(420, 760); x, y = rr * math.cos(a), rr * math.sin(a) + 30.0
    src_ = rng.choice(firs); inst = bpy.data.objects.new(f'ENTORNO_abeto_{k:02d}', src_.data); C_ENV.objects.link(inst)
    s = FIR_SCALE * rng.uniform(0.55, 1.15); inst.scale = (s, s, s); inst.rotation_euler = (0, 0, rng.uniform(0, 6.28)); inst.location = (x, y, 1.0)
m_reed, nt, bs = new_mat('junco_seco')
tco = N(nt, 'ShaderNodeTexCoord'); nr = N(nt, 'ShaderNodeTexNoise'); nr.inputs['Scale'].default_value = 40.0; nt.links.new(tco.outputs['Object'], nr.inputs['Vector'])
nt.links.new(mix(nt, nr.outputs['Fac'], lin((150, 122, 78)), lin((206, 182, 132))), bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.6
bs.inputs['Subsurface Weight'].default_value = 0.2
m_cat, nt, bs = new_mat('totora'); bs.inputs['Base Color'].default_value = (*lin((74, 48, 30)), 1); bs.inputs['Roughness'].default_value = 0.9
me = bpy.data.meshes.new('juncos'); bm = bmesh.new()
def stalk(base, h, bend, rad, head=False):
    segs = 10; d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)).normalized()
    pts = [base + d * bend * (k / segs) ** 2 * h + Vector((0, 0, h * k / segs)) for k in range(segs + 1)]
    for k in range(segs):
        p0, p1 = pts[k], pts[k + 1]; r0, r1 = rad * (1 - 0.8 * k / segs), rad * (1 - 0.8 * (k + 1) / segs)
        dd = p1 - p0; q = dd.to_track_quat('Z', 'Y')
        ret = bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=r0, radius2=r1, depth=dd.length)
        for v in ret['verts']: v.co = p0 + q @ (v.co + Vector((0, 0, dd.length / 2)))
    if head:
        kk = int(segs * 0.78); p = pts[kk]; dd = pts[kk + 1] - p; q = dd.to_track_quat('Z', 'Y')
        ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=rad * 2.6, radius2=rad * 2.4, depth=h * 0.12)
        for v in ret['verts']: v.co = p + q @ v.co
        for f_ in {f_ for v in ret['verts'] for f_ in v.link_faces}: f_.material_index = 1
for cx_, cy_, n_ in ((-2.6, -3.2, 26), (-3.4, -1.0, 18), (4.6, -3.4, 22), (6.0, 1.8, 16), (-6.5, 3.0, 30), (8.0, 5.0, 30)):
    for _ in range(n_):
        stalk(Vector((cx_ + rng.gauss(0, 0.35), cy_ + rng.gauss(0, 0.35), -0.05)), rng.uniform(1.6, 4.6), rng.uniform(0.05, 0.35), rng.uniform(0.012, 0.022), head=rng.random() < 0.18)
bm.to_mesh(me); bm.free()
reeds = obj('ENTORNO_juncos', me, m_reed, C_ENV); me.materials.append(m_cat)
for p in me.polygons: p.use_smooth = True

# ------------------------------------------------------------------ trucha: rig girado (cabeza arriba), sube del agua en camara lenta
rig = bpy.data.objects['TRUCHA_rig']; body = bpy.data.objects['TRUCHA_cuerpo']
names = ['Head'] + [f'Spine{i}' for i in range(1, 9)]
YAW = Matrix.Rotation(math.radians(-18), 4, 'Z')                                  # un poco de 3/4 hacia la camara
# antes del estallido: nada bajo el hielo hacia +X, gira hacia arriba y acelera hasta salir a 45 grados (se integra hacia atras desde la salida)
SWIM = {}
VEX = math.hypot(VX, VZ)
def head_spd(f):
    head = ANG * max(0.0, min(1.0, (f - (FB - 45)) / 38.0)) ** 1.5                # gira de horizontal a 45 grados
    spd = 1.5 + (VEX - 1.5) * max(0.0, 1 - (FB - f) / 14.0) ** 2 + 0.6 * max(0.0, 1 - (FB - f) / 45.0)
    return head, spd
px_, pz_ = 0.0, -1.45; raw = {}
for f in range(F0, FB + 1):                                                     # se integra hacia adelante desde media agua
    h_, v_ = head_spd(f); raw[f] = (px_, pz_, h_, v_)
    px_ += v_ / FPS * math.cos(h_); pz_ += v_ / FPS * math.sin(h_)
ex, ez = raw[FB][0], raw[FB][1]
kz = (Z0 + 1.45) / max(ez + 1.45, 1e-3)                                         # la subida se escala para llegar justo a la salida
for f in range(F0, FB + 1):
    x_, z_, h_, v_ = raw[f]
    SWIM[f] = (x_ + (X0 - ex), -1.45 + (z_ + 1.45) * kz, h_, v_)
for f in range(F0, F1 + 1):
    t = ts(f) if f > FB else 0.0
    if f > FB:
        x = X0 + VX * t; z = Z0 + VZ * t - 0.5 * G * t * t
        phi = 0.30 * math.atan2(VZ - G * t, VX) + 0.70 * ANG                       # el cuerpo queda a ~45 grados, apenas sigue la curva
    else:
        x, z, phi, spd = SWIM[f]
        t = (f - FB) / FPS                                                          # tiempo real para el coleteo
    k = min(1.0, max(0.0, t) / TAP)
    c, s_ = math.cos(phi), math.sin(phi)
    Rm = Matrix(((0, -c, -s_), (1, 0, 0), (0, -s_, c)))                             # columnas: X->(0,1,0), Y->-d, Z->dorso
    rig.location = (x, 0.0, z); rig.rotation_euler = (YAW @ Rm.to_4x4()).to_euler('XYZ', rig.rotation_euler)   # euler continuo
    rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f)
    amp = 0.20 * (1 - 0.55 * k) if f > FB - 14 else 0.13                              # nado tranquilo, coletazo fuerte al acelerar
    for i, n in enumerate(names[1:], 1):
        pb = rig.pose.bones[n]; s2_ = i / 8.0
        lat = amp * (0.15 + 0.85 * s2_ * s2_) * math.sin(2 * math.pi * ((4.5 if f > FB - 14 else 2.0) * t + 0.35 * i) - 0.3)
        arch = 0.06 * k * math.sin(math.pi * s2_)                                     # se curva siguiendo el arco
        pb.rotation_euler = (arch, 0.0, lat); pb.keyframe_insert('rotation_euler', frame=f)
    jaw = rig.pose.bones['Jaw']; jaw.rotation_mode = 'XYZ'; jaw.rotation_euler = (0.18 * k, 0, 0); jaw.keyframe_insert('rotation_euler', frame=f)
for fc in rig.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
for ms in body.material_slots:                                                   # piel mas mojada para Cycles
    b_ = [n for n in ms.material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED']
    if b_: b_[0].inputs['Coat Weight'].default_value = 0.8; b_[0].inputs['Subsurface Weight'].default_value = 0.12; b_[0].inputs['Subsurface Radius'].default_value = (0.02, 0.012, 0.008)

# ------------------------------------------------------------------ agua del estallido: gotas (vidrio de agua) y chorreo del pez
m_d, nt, bs = new_mat('gota'); bs.inputs['Base Color'].default_value = (1, 1, 1, 1); bs.inputs['Roughness'].default_value = 0.0
bs.inputs['Transmission Weight'].default_value = 1.0; bs.inputs['IOR'].default_value = 1.333
me = bpy.data.meshes.new('gota'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0); bm.to_mesh(me); bm.free()
drop = obj('GOTA', me, m_d, C_FX); drop.location = (0, 0, -80); drop.hide_render = True
for p in me.polygons: p.use_smooth = True
ringv = []
for i in range(160):
    a = rng.uniform(0, 6.283); r = math.sqrt(rng.uniform(0.0, 1.0)) * 0.75; ringv.append((r * math.cos(a), r * math.sin(a), -0.02))
me = bpy.data.meshes.new('estallido'); me.from_pydata(ringv, [], []); em = obj('AGUA_emisor', me, None, C_FX); em.hide_render = True
def particles(o, name, count, f0, f1, vel, rand, size, sizer, life, src='VERT'):
    md = o.modifiers.new(name, 'PARTICLE_SYSTEM'); ps = md.particle_system.settings
    ps.count = count; ps.frame_start = f0; ps.frame_end = f1; ps.lifetime = life; ps.emit_from = src
    ps.normal_factor = 0.0; ps.object_align_factor = vel; ps.factor_random = rand
    ps.render_type = 'OBJECT'; ps.instance_object = drop; ps.particle_size = size; ps.size_random = sizer; ps.physics_type = 'NEWTON'
    return ps
s1 = particles(em, 'estallido', 7000, FB, FB + 26, (6.5, 0, 9.5), 4.5, 0.022, 0.9, 500)
s2 = particles(body, 'chorreo', 1600, FB + 4, F1, (0, 0, 0.0), 0.25, 0.014, 0.8, 500, 'FACE'); s2.normal_factor = 0.5
for ps in (s1, s2):
    for f in range(F0, F1 + 1): ps.timestep = dts(f) if f > FB else 0.04; ps.keyframe_insert('timestep', frame=f)
ice.modifiers.new('choque', 'COLLISION'); ice.collision.damping = 0.85; ice.collision.friction_factor = 0.7

# ------------------------------------------------------------------ luz: llave dorada solo sobre el pez (light linking), contraluz frio
def spot(name, loc, target, energy, color, size, ang):
    l = bpy.data.lights.new(name, 'SPOT'); l.energy = energy; l.color = color; l.spot_size = math.radians(ang); l.spot_blend = 0.7; l.shadow_soft_size = size
    o = obj(name, l, None, C_ENV); o.location = loc; o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
key = spot('LUZ_llave_dorada', (-3.4, -4.4, 3.2), (0, 0, 1.3), 2200, lin((255, 170, 82)), 0.8, 26)
rim = spot('LUZ_contra_fria', (1.8, 5.0, 3.0), (0, 0, 1.1), 3000, lin((150, 190, 255)), 0.6, 30)
fish_c = bpy.data.collections.new('RECIBE_LLAVE')
for o in bpy.data.objects:
    if o.name.startswith('TRUCHA_') and o.type == 'MESH': fish_c.objects.link(o)
rim_c = bpy.data.collections.new('RECIBE_CONTRALUZ')                          # el contraluz no toca el hielo grande (si no, refleja un foco)
for o in list(fish_c.objects) + list(C_FX.objects) + [c[0] for c in cells] + [reeds]: rim_c.objects.link(o)
key_c = bpy.data.collections.new('RECIBE_LLAVE_TODO')
for o in list(fish_c.objects) + list(C_FX.objects): key_c.objects.link(o)
try: key.light_linking.receiver_collection = key_c; key.light_linking.blocker_collection = fish_c; rim.light_linking.receiver_collection = rim_c
except Exception as e: print('light linking', e)

# ------------------------------------------------------------------ camara: baja, casi a ras del hielo, empuje lento
cam = obj('CAMARA', bpy.data.cameras.new('CAMARA')); sc.camera = cam; cam.data.lens = 58; cam.data.clip_end = 8000
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 5.6
tgt = obj('CAMARA_mira', None); tgt.empty_display_size = 0.2; cam.data.dof.focus_object = tgt
tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
sc.frame_set(F0)
def fishpos(f):
    sc.frame_set(f); return rig.matrix_world.translation.copy()
FP = {f: fishpos(f) for f in range(F0, F1 + 1)}
def smoothstep(a, b, x): x = min(1.0, max(0.0, (x - a) / (b - a))); return x * x * (3 - 2 * x)
END_C, END_T = Vector((1.45, -7.7, 0.38)), Vector((1.55, 0.0, 0.82))
for f in range(F0, F1 + 1):
    fp = FP[f]
    under = fp + Vector((-0.5, -2.4, -1.0))                                         # bajo el agua: abajo del pez, mirando hacia el techo de hielo
    PB, PA = Vector((-1.3, -2.5, -0.45)), Vector((-1.1, -2.8, 0.38))                  # cruza la superficie del hielo junto al agujero
    if f <= FB - 25: cl = under; tl = fp + Vector((0.6, 0, 0.45))
    elif f <= FB + 1:
        u = smoothstep(FB - 25, FB + 1, f); cl = under.lerp(PB, u); tl = fp
    elif f <= FB + 7:
        u = smoothstep(FB + 1, FB + 7, f); cl = PB.lerp(PA, u); tl = fp                # rompe la superficie con el estallido
    else:
        u = smoothstep(FB + 7, F1 - 20, f); cl = PA.lerp(END_C, u); tl = fp.lerp(END_T, u * 0.7)
    cam.location = cl; tgt.location = tl; cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f)
    cam.data.lens = 32 + 26 * smoothstep(FB + 7, F1 - 20, f); cam.data.keyframe_insert('lens', frame=f)
sc['KF'] = KF; sc['KT'] = KT; sc['FB'] = FB

# ------------------------------------------------------------------ bajo el agua: volumen de agua turbia, fondo de barro, juncos, particulas y burbujas bajo el hielo
m_vol = bpy.data.materials.new('agua_volumen'); m_vol.use_nodes = True; vt = m_vol.node_tree; vt.nodes.clear()
vo_ = N(vt, 'ShaderNodeOutputMaterial'); pv = N(vt, 'ShaderNodeVolumePrincipled')
pv.inputs['Color'].default_value = (*lin((150, 200, 185)), 1); pv.inputs['Density'].default_value = 0.06; pv.inputs['Anisotropy'].default_value = 0.75
pv.inputs['Absorption Color'].default_value = (*lin((95, 155, 140)), 1)
pv.inputs['Emission Color'].default_value = (*lin((40, 90, 100)), 1); pv.inputs['Emission Strength'].default_value = 0.015   # luz ambiente difusa bajo el hielo
vt.links.new(pv.outputs[0], vo_.inputs['Volume'])
me = bpy.data.meshes.new('agua_vol'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
vol = obj('AGUA_volumen', me, m_vol, C_ICE); vol.location = (0, 0, -3.0 - TH / 2 - 0.005); vol.scale = (70, 70, 6.0 - TH - 0.01)
m_mud, nt, bs = new_mat('barro'); tco = N(nt, 'ShaderNodeTexCoord'); nm_ = N(nt, 'ShaderNodeTexNoise'); nm_.inputs['Scale'].default_value = 0.6; nm_.inputs['Detail'].default_value = 12.0
nt.links.new(tco.outputs['Object'], nm_.inputs['Vector']); nt.links.new(mix(nt, nm_.outputs['Fac'], lin((30, 32, 22)), lin((70, 66, 46))), bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.9
mb = N(nt, 'ShaderNodeBump'); mb.inputs['Strength'].default_value = 0.6; nt.links.new(nm_.outputs['Fac'], mb.inputs['Height']); nt.links.new(mb.outputs[0], bs.inputs['Normal'])
me = bpy.data.meshes.new('fondo_barro'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=80, y_segments=80, size=35.0)
for v in bm.verts: v.co.z = 0.35 * mnoise.noise(v.co * 0.25) + 0.08 * mnoise.noise(v.co * 1.7)
bm.to_mesh(me); bm.free(); mud = obj('AGUA_fondo_barro', me, m_mud, C_ICE); mud.location.z = -5.2
for p in me.polygons: p.use_smooth = True
deep.hide_render = True                                                         # el plano negro de abajo ya no hace falta: hay agua de verdad
me = bpy.data.meshes.new('tallos'); bm = bmesh.new()
for _ in range(140):                                                            # tallos de juncos desde el fondo hasta el hielo
    b = Vector((rng.uniform(-16, 10), rng.choice([rng.uniform(-9, -5), rng.uniform(-0.8, 14)]), -5.1)); stalk(b, rng.uniform(3.0, 5.0), rng.uniform(0.02, 0.15), rng.uniform(0.012, 0.02))
bm.to_mesh(me); bm.free(); obj('AGUA_tallos', me, m_reed, C_ICE)
m_sp, nt, bs = new_mat('particulas'); bs.inputs['Base Color'].default_value = (*lin((180, 190, 170)), 1); bs.inputs['Roughness'].default_value = 0.8
bs.inputs['Emission Color'].default_value = (0.5, 0.6, 0.6, 1); bs.inputs['Emission Strength'].default_value = 0.05
me = bpy.data.meshes.new('mota'); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0); bm.to_mesh(me); bm.free()
mota = obj('AGUA_mota', me, m_sp, C_FX); mota.location = (0, 0, -80); mota.hide_render = True
pts = [(rng.uniform(-14, 6), rng.uniform(-7, 3), rng.uniform(-4.8, -0.2)) for _ in range(2500)]
me = bpy.data.meshes.new('motas'); me.from_pydata(pts, [], []); mo_ = obj('AGUA_motas', me, None, C_FX)
mo_.instance_type = 'VERTS'; mota.parent = mo_; mota.location = (0, 0, 0); mota.scale = (0.006, 0.006, 0.006); mota.hide_render = False
bub_pts = [(rng.uniform(-12, 4), rng.uniform(-5, 3), -TH - 0.004) for _ in range(900)]
m_bu, nt, bs = new_mat('burbuja_aire'); bs.inputs['Base Color'].default_value = (1, 1, 1, 1); bs.inputs['Metallic'].default_value = 0.8; bs.inputs['Roughness'].default_value = 0.05
bs.inputs['Emission Color'].default_value = (*lin((190, 215, 235)), 1); bs.inputs['Emission Strength'].default_value = 0.9   # reflejo total: se ven plateadas
me = bpy.data.meshes.new('burbuja'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0)
for v in bm.verts: v.co.z *= 0.25
bm.to_mesh(me); bm.free()
for k in range(28):                                                              # racimos de burbujas atrapadas, de tamanos distintos
    cxb, cyb = rng.uniform(-12, 3), rng.uniform(-5, 3)
    for _ in range(rng.randint(3, 14)):
        b_ = obj(f'AGUA_burbuja_{k}_{_}', me, None, C_FX); r_ = rng.uniform(0.006, 0.05) ** 1.0
        b_.location = (cxb + rng.gauss(0, 0.25), cyb + rng.gauss(0, 0.25), -TH - 0.004 - r_ * 0.2); b_.scale = (r_ * rng.uniform(0.7, 1.4), r_, r_)
if 'burbuja_aire' not in [m_.name for m_ in me.materials]: me.materials.append(m_bu)
# luz de luna/cielo que entra por el hielo (rayos bajo el agua) y suma un poco de luz arriba
moon = bpy.data.lights.new('LUZ_cielo_alto', 'SUN'); moon.energy = 0.9;   moon.color = lin((160, 190, 255)); moon.angle = math.radians(12)
mo = obj('LUZ_cielo_alto', moon, None, C_ENV); mo.rotation_euler = (math.radians(24), math.radians(-14), 0)
for f, e in ((F0, 3.2), (FB + 3, 3.2), (FB + 7, 0.9)): moon.energy = e; moon.keyframe_insert('energy', frame=f)   # fuerte bajo el agua (rayos), suave arriba
# sombra de la nieve: un plano invisible encima del hielo que solo hace sombra -> rayos de luz bajo el agua entre las manchas de nieve
m_sn = bpy.data.materials.new('sombra_nieve'); m_sn.use_nodes = True; st_ = m_sn.node_tree; st_.nodes.clear()
so_ = N(st_, 'ShaderNodeOutputMaterial'); tr_ = N(st_, 'ShaderNodeBsdfTransparent'); df_ = N(st_, 'ShaderNodeBsdfDiffuse')
tcs = N(st_, 'ShaderNodeTexCoord'); ns_ = N(st_, 'ShaderNodeTexNoise'); ns_.inputs['Scale'].default_value = 0.35; ns_.inputs['Detail'].default_value = 6.0; st_.links.new(tcs.outputs['Object'], ns_.inputs['Vector'])
ss2 = N(st_, 'ShaderNodeSeparateXYZ'); st_.links.new(tcs.outputs['Object'], ss2.inputs[0])
rr2 = M(st_, 'SQRT', M(st_, 'ADD', M(st_, 'MULTIPLY', ss2.outputs[0], ss2.outputs[0]), M(st_, 'MULTIPLY', ss2.outputs[1], ss2.outputs[1])))
msk = M(st_, 'MULTIPLY', smooth(st_, ns_.outputs['Fac'], 0.47, 0.53), smooth(st_, rr2, RF + 0.1, RF + 0.6))
mxs = N(st_, 'ShaderNodeMixShader'); st_.links.new(msk, mxs.inputs[0]); st_.links.new(tr_.outputs[0], mxs.inputs[1]); st_.links.new(df_.outputs[0], mxs.inputs[2]); st_.links.new(mxs.outputs[0], so_.inputs[0])
me = bpy.data.meshes.new('sombra_nieve'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40.0); bm.to_mesh(me); bm.free()
sn_ = obj('AGUA_sombra_nieve', me, m_sn, C_ICE); sn_.location.z = 0.03
for attr in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(sn_, attr, False)
for f, h in ((F0, False), (FB + 3, False), (FB + 4, True)): sn_.hide_render = h; sn_.keyframe_insert('hide_render', frame=f)
for o in [ice] + [c[0] for c in cells] + [water]: o.visible_shadow = False          # sin causticas el vidrio bloquearia la luz: el hielo deja pasar la luz
uw = bpy.data.lights.new('LUZ_bajo_agua', 'AREA'); uw.shape = 'DISK'; uw.size = 3.0; uw.color = lin((225, 238, 236))
uwo = obj('LUZ_bajo_agua', uw, None, C_ENV); uwo.rotation_euler = (0, 0, 0)
cl_ = uwo.constraints.new('COPY_LOCATION'); cl_.target = rig; cl_.use_offset = True
uwo.location = (0.3, 0.4, 1.0); off = uwo.constraints.new('LIMIT_LOCATION'); off.use_max_z = True; off.max_z = -TH - 0.3
for f, e in ((F0, 60.0), (FB - 6, 60.0), (FB + 6, 0.0)): uw.energy = e; uw.keyframe_insert('energy', frame=f)   # luz suave del hielo sobre el pez bajo el agua
try: uwo.light_linking.receiver_collection = fish_c
except Exception: pass

# ------------------------------------------------------------------ render: Cycles
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1350, 100
sc.render.engine = 'CYCLES'; cy = sc.cycles
cy.samples = 256; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02; cy.use_denoising = True
cy.max_bounces = 16; cy.transmission_bounces = 14; cy.transparent_max_bounces = 16; cy.glossy_bounces = 8; cy.diffuse_bounces = 4
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except TypeError: pass
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = '//render/btw_'
cy.volume_step_rate = 4.0; cy.volume_max_steps = 256
bpy.ops.ptcache.bake_all(bake=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print('ESCENA_OK', OUT, 'placas', len(cells), 'sol', round(math.degrees(a_sun), 1))
