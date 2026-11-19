# Re-guarda un .blend en la version de Blender que lo abre (para la granja blender.farm, que no acepta 4.2).
import bpy, sys
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print('CONVERTIDO', bpy.app.version_string, out, flush=True)
