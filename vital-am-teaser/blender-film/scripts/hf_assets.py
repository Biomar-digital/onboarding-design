# Swap the proxy palms (all instances share one mesh) and the farm shed for the Higgsfield image_to_3d models.
import bpy, math
from mathutils import Vector, Matrix
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
bpy.ops.wm.open_mainfile(filepath=S+'film/film.blend')
def load(path,name,ratio):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    new=[o for o in bpy.data.objects if o not in before]; ms=[o for o in new if o.type=='MESH']
    for o in new:
        if o.type!='MESH': pass
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active=ms[0]
    if len(ms)>1: bpy.ops.object.join()
    o=bpy.context.view_layer.objects.active; o.parent=None if o.parent is None else o.parent
    mw=o.matrix_world.copy(); o.parent=None; o.matrix_world=mw
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for x in new:
        if x!=o and x.name in bpy.data.objects: bpy.data.objects.remove(x)
    if ratio<1:
        d=o.modifiers.new('dec','DECIMATE'); d.ratio=ratio; bpy.ops.object.modifier_apply(modifier='dec')
    vs=[v.co for v in o.data.vertices]; lo=Vector((min(v.x for v in vs),min(v.y for v in vs),min(v.z for v in vs))); hi=Vector((max(v.x for v in vs),max(v.y for v in vs),max(v.z for v in vs)))
    base=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)); o.data.transform(Matrix.Translation(-base)); o.name=name
    print(name,'polys',len(o.data.polygons),'size',tuple(round(x,3) for x in hi-lo)); return o,hi-lo
# ---- palms
pn,sz=load(S+'hf3d/palm.glb','HF_PALM',0.35)
pn.data.transform(Matrix.Scale(1/sz.z,4))   # base at origin, height 1
old=bpy.data.objects['coconut_palm']
cs=[old.matrix_world@Vector(c) for c in old.bound_box]; zlo=min(c.z for c in cs); H=max(c.z for c in cs)-zlo
B=Vector((sum(c.x for c in cs)/8,sum(c.y for c in cs)/8,zlo))
loc=old.matrix_world.inverted()@Matrix.Translation(B)@Matrix.Scale(H*1.2,4)@Matrix.Diagonal((1,1,1.35,1))
me=pn.data.copy(); me.transform(loc); me.name='HF_PALM_ME'
oldme=old.data
for o in bpy.data.objects:
    if o.type=='MESH' and o.data==oldme: o.data=me
bpy.data.objects.remove(pn)
# ---- hut replaces shed
hut,hs=load(S+'hf3d/hut.glb','HF_HUT',0.5)
shed=bpy.data.objects['SET_Farm_Shed']; roof=bpy.data.objects['SET_Farm_Shed_Roof']
s=6.2/max(hs.x,hs.y); hut.scale=(s,s,s); hut.location=(shed.location.x,shed.location.y,shed.location.z-shed.dimensions.z/2)
if hs.y>hs.x: hut.rotation_euler=(0,0,math.radians(90))
for o in (shed,roof): o.hide_render=True; o.hide_viewport=True
# ---- tree line: break the smooth blobs into canopy clumps
tx=bpy.data.textures.new('CANOPY','CLOUDS'); tx.noise_scale=1.2; tx.noise_depth=3
for o in bpy.data.objects:
    if o.name.startswith('TREE_'):
        o.modifiers.clear(); sd=o.modifiers.new('sub','SUBSURF'); sd.levels=1; sd.render_levels=2
        d=o.modifiers.new('disp','DISPLACE'); d.texture=tx; d.strength=2.2; d.mid_level=0.45; d.texture_coords='GLOBAL'
mt=bpy.data.materials['MAT_TreeLine']; n=mt.node_tree.nodes; l=mt.node_tree.links; b=[x for x in n if x.type=='BSDF_PRINCIPLED'][0]
nz=n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.6; r=n.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(0.035,0.06,0.025,1); r.color_ramp.elements[1].color=(0.09,0.12,0.045,1)
l.new(nz.outputs['Fac'],r.inputs[0]); l.new(r.outputs[0],b.inputs['Base Color'])
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('HF_OK')
