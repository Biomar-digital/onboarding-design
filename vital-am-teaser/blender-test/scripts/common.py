import bpy, math, random, mathutils
from mathutils import Vector, Euler
P='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/prev/'
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'
    sc.cycles.use_denoising=True; sc.cycles.denoiser='OPENIMAGEDENOISE'
    sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'
    sc.render.film_transparent=False; sc.render.fps=24
    return sc
def imp(path):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]
def roots(objs): return [o for o in objs if o.parent is None]
def norm_size(objs, target, axis=None):
    # scale the root(s) so the largest mesh extent = target metres
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for o in objs if o.type=='MESH' for c in o.bound_box]
    ext=[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)]
    s=target/(ext[axis] if axis is not None else max(ext))
    for r in roots(objs): r.scale=[v*s for v in r.scale]
    bpy.context.view_layer.update(); return s
def cam(loc, look, lens=35, name='Cam'):
    c=bpy.data.cameras.new(name); c.lens=lens; o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=loc; d=Vector(look)-Vector(loc); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=o; return o
def node_mat(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; return m, m.node_tree.nodes, m.node_tree.links
