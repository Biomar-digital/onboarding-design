# Turn the HF pointing hand into a fist: curl the extended index finger around a handle; save hf/fist.blend-ready mesh as glb.
import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
bpy.ops.import_scene.gltf(filepath=S+'hf/hand.glb')
h=[o for o in bpy.data.objects if o.type=='MESH'][0]
mw=h.matrix_world.copy(); h.parent=None; h.matrix_world=mw; bpy.context.view_layer.objects.active=h; h.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for o in list(bpy.data.objects):
    if o!=h: bpy.data.objects.remove(o)
X0=-0.60; ZC=0.155; TH=math.radians(265); L=0.35; R=L/TH
for v in h.data.vertices:
    x,y,z=v.co
    t=X0-x
    if t<=0 or z<0.05: continue
    w=min(1.0,t/0.06)                       # ease in over the first knuckle so the base does not crease
    hgt=z-ZC; phi=min(t,L)/R*w; rem=max(0.0,t-L)
    nx=X0-(R+hgt)*math.sin(phi); nz=ZC-R+(R+hgt)*math.cos(phi)
    # straight remainder continues along the tangent
    nx+=-rem*math.cos(phi); nz+=-rem*math.sin(phi)
    v.co.x=nx*w+x*(1-w) if w<1 else nx; v.co.z=nz*w+z*(1-w) if w<1 else nz
import bmesh
bm=bmesh.new(); bm.from_mesh(h.data); bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x>0.14],context='VERTS'); bm.to_mesh(h.data); bm.free()
h.data.update(); h.name='FIST'
bpy.ops.export_scene.gltf(filepath=S+'hf/fist.glb',use_selection=True)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=8; sc.render.resolution_x=400; sc.render.resolution_y=400
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[1].default_value=1.5
cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera=cam
c=Vector((-0.45,0,0)); sc.render.resolution_x=600; sc.render.resolution_y=600; sc.world.node_tree.nodes['Background'].inputs[1].default_value=3.0
for tag,off in (('side',(0,-1.6,0)),('top',(0,0.001,1.6)),('front',(-1.6,0,0.3)),('back',(0,1.6,0))):
    cam.location=c+Vector(off); cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=S+'film/fist_%s.jpg'%tag; bpy.ops.render.render(write_still=True)
print('FIST_OK')
