# Vista de control de la bolsa 3D (frente y tres cuartos): blender -b -P render_bolsa.py -- bolsa.glb salida.png
import bpy, sys, math, mathutils
a = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=a[0])
objs = [o for o in sc.objects if o.type == 'MESH']
mn = mathutils.Vector((1e9,) * 3); mx = -mn
for o in objs:
    for v in o.bound_box: w = o.matrix_world @ mathutils.Vector(v); mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
c = (mn + mx) / 2; h = (mx - mn).length
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.92, 0.93, 0.95, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
for loc, e in (((2, -3, 3), 300), ((-3, -2, 1), 120)):
    l = bpy.data.lights.new('l', 'AREA'); l.energy = e; l.size = 2; lo = bpy.data.objects.new('l', l); sc.collection.objects.link(lo)
    lo.location = c + mathutils.Vector(loc); lo.rotation_euler = (c - lo.location).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('c'); cd.lens = 70; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.use_denoising = True; sc.render.resolution_x = 900; sc.render.resolution_y = 1100
sc.view_settings.view_transform = 'Standard'
outs = []
for i, ang in enumerate((0, 35, 180)):
    r = h * 2.4; t = math.radians(ang)
    cam.location = c + mathutils.Vector((r * math.sin(t), -r * math.cos(t), 0.1 * h)); cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    p = a[1].replace('.png', '_%d.png' % i); sc.render.filepath = p; bpy.ops.render.render(write_still=True); outs.append(p)
print('DONE', outs)
