# Agua real (simulacion de fluido Mantaflow FLIP) para Break Through Winter.
# El agua bajo el hielo es empujada por la trucha y sale por el agujero en un chorro que se rompe en gotas.
#   blender -b escena_hielo.blend -P agua_flip.py -- RESOLUCION [salida.blend]
# La camara lenta del resto de la escena se copia al "time scale" del dominio.
import bpy, sys, math, os
from mathutils import Vector
A = sys.argv[sys.argv.index('--') + 1:]
RESN = int(A[0]); OUT = A[1] if len(A) > 1 else bpy.data.filepath
sc = bpy.context.scene
FB = 56; F0, F1 = sc.frame_start, sc.frame_end
KF = [FB, FB + 10, 150, F1 + 10]; KT = [0.0, 0.20, 0.353, 0.40]
def ts(f):
    if f <= FB: return 0.0
    for i in range(len(KF) - 1):
        if f <= KF[i + 1]:
            u = (f - KF[i]) / (KF[i + 1] - KF[i])
            if i == 0: return KT[0] + (KT[1] - KT[0]) * (1 - (1 - u) ** 1.6)
            return KT[i] + (KT[i + 1] - KT[i]) * u
    return KT[-1]
def dts(f): return max(ts(f + 0.5) - ts(f - 0.5), 1e-5)
C = bpy.data.collections.get('AGUA_FX')
def box(name, lo, hi):
    bpy.ops.mesh.primitive_cube_add(size=1.0); o = bpy.context.object; o.name = name
    for c in o.users_collection: c.objects.unlink(o)
    C.objects.link(o); o.location = [(a + b) / 2 for a, b in zip(lo, hi)]; o.scale = [b - a for a, b in zip(lo, hi)]
    return o
TH = 0.05
dom = box('AGUA_dominio', (-2.0, -1.7, -1.05), (3.0, 1.7, 2.3))
md = dom.modifiers.new('fluido', 'FLUID'); md.fluid_type = 'DOMAIN'; ds = md.domain_settings
ds.domain_type = 'LIQUID'; ds.resolution_max = RESN; ds.use_mesh = True; ds.use_flip_particles = False
ds.cache_directory = os.path.join(os.path.dirname(bpy.path.abspath(OUT)) or '.', 'cache_agua'); ds.cache_type = 'ALL'
ds.cache_frame_start = F0; ds.cache_frame_end = F1
ds.mesh_scale = 2; ds.mesh_particle_radius = 1.6; ds.mesh_smoothen_pos = 2; ds.mesh_smoothen_neg = 2
ds.use_collision_border_top = False
for f in range(F0, F1 + 1):                                                     # misma camara lenta que el pez
    ds.time_scale = (dts(f) / 0.04) if f > FB else 1.0; ds.keyframe_insert('time_scale', frame=f)
ds.use_diffusion = False
# agua bajo el hielo (llena el fondo del dominio hasta justo debajo del hielo)
water = box('AGUA_inicial', (-1.99, -1.69, -1.04), (2.99, 1.69, -TH - 0.01))
mw = water.modifiers.new('fluido', 'FLUID'); mw.fluid_type = 'FLOW'; fs = mw.flow_settings
fs.flow_type = 'LIQUID'; fs.flow_behavior = 'GEOMETRY'; fs.flow_source = 'MESH'; water.hide_render = True; water.display_type = 'WIRE'
# chorro: la trucha arrastra una columna de agua al salir
jet = box('AGUA_chorro', (-0.75, -0.30, -0.70), (-0.15, 0.30, -0.30))
mj = jet.modifiers.new('fluido', 'FLUID'); mj.fluid_type = 'FLOW'; fj = mj.flow_settings
fj.flow_type = 'LIQUID'; fj.flow_behavior = 'INFLOW'; fj.flow_source = 'MESH'; fj.use_initial_velocity = True
fj.velocity_coord = (8.0, 0, 8.0); jet.hide_render = True; jet.display_type = 'WIRE'
for f, on in ((FB - 1, False), (FB, True), (FB + 7, True), (FB + 8, False)):
    fj.use_inflow = on; fj.keyframe_insert('use_inflow', frame=f)
# obstaculos: el hielo y la trucha (malla deformada por el rig)
for name, planar in (('HIELO_estanque', False), ('TRUCHA_cuerpo', False)):
    o = bpy.data.objects[name]; me_ = o.modifiers.new('fluido', 'FLUID'); me_.fluid_type = 'EFFECTOR'
    es = me_.effector_settings; es.effector_type = 'COLLISION'; es.use_effector = True; es.subframes = 1; es.use_plane_init = planar
# material de agua para la malla simulada
# agua del chorro: transparente pero aireada (blanca donde rompe), si no se ve negra contra la noche
m = bpy.data.materials.new('agua_chorro'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.92, 0.96, 1.0, 1); b.inputs['Roughness'].default_value = 0.03; b.inputs['IOR'].default_value = 1.333
b.inputs['Transmission Weight'].default_value = 1.0
tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6.0; nz.inputs['Detail'].default_value = 8.0
nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.5; mr.inputs['From Max'].default_value = 0.72; mr.inputs['To Max'].default_value = 0.85
nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
foam = nt.nodes.new('ShaderNodeBsdfPrincipled'); foam.inputs['Base Color'].default_value = (0.9, 0.94, 0.98, 1); foam.inputs['Roughness'].default_value = 0.35
foam.inputs['Subsurface Weight'].default_value = 1.0; foam.inputs['Subsurface Radius'].default_value = (0.05, 0.06, 0.08)
ms = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(mr.outputs[0], ms.inputs[0]); nt.links.new(b.outputs[0], ms.inputs[1]); nt.links.new(foam.outputs[0], ms.inputs[2])
nt.links.new(ms.outputs[0], nt.nodes['Material Output'].inputs[0])
dom.data.materials.clear(); dom.data.materials.append(m)
for cn in ('RECIBE_CONTRALUZ',):                                             # el chorro solo recibe el contraluz frio (con la dorada parecia oro fundido)
    c_ = bpy.data.collections.get(cn)
    if c_ and dom.name not in c_.objects: c_.objects.link(dom)
for p in dom.data.polygons: p.use_smooth = True
with bpy.context.temp_override(scene=sc, active_object=dom, object=dom, selected_objects=[dom]):
    import time; t = time.time()
    bpy.ops.fluid.bake_all()
    print('FLIP_BAKE', RESN, round(time.time() - t, 1), 's')
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print('FLIP_OK', OUT)
