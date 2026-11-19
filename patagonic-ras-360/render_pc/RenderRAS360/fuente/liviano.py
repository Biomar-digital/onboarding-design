# Deja el .blend liviano para abrirlo en Blender (la granja lo renderiza igual): oculta en la vista 3D los ~1400
# salmones y las burbujas (solo en la vista, NO en el render), vista en solido, y lo guarda en la version que lo abre.
import bpy, sys
out = sys.argv[sys.argv.index('--') + 1]
n = 0
for o in bpy.data.objects:
    if o.type in ('MESH', 'CURVE', 'EMPTY', 'ARMATURE') and not o.name.startswith('cam_'):
        o.hide_viewport = True; n += 1
for scr in bpy.data.screens:
    for a in scr.areas:
        for sp in a.spaces:
            if sp.type == 'VIEW_3D': sp.shading.type = 'SOLID'
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print('LIVIANO', bpy.app.version_string, n, 'objetos ocultos en la vista', out, flush=True)
