# Build the Blender film scene from the previs GLB + client assets. Saves film.blend
import bpy, json, math, sys, os, re
from mathutils import Matrix, Vector
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
P=S+'prev/'
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def imp(path):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path); return [o for o in bpy.data.objects if o not in before]
# ---------- previs scene
env=imp(P+'scene_v10.glb')
for o in env:
    if o.animation_data: o.animation_data_clear()
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
bpy.context.view_layer.update()
# flatten hierarchy (we drive world matrices)
for o in env:
    if o.parent is not None:
        mw=o.matrix_world.copy(); o.parent=None; o.matrix_world=mw
DROP=re.compile(r'^(SHRIMP_|SHR\d\d_|ANAT_|FEED_|MESH_|Icosphere|LIGHT_|CAM_|FARMER_(?!Root$|Scoop_Load$|Feed_Bucket$)|POND_Water_Volume|SET_Spray_Droplet)')
for o in list(env):
    if DROP.match(o.name) or o.type in ('CAMERA','LIGHT','ARMATURE'):
        bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    if o.name in ('FARMER_Root','FARMER_Scoop_Load','FARMER_Feed_Bucket'): o.hide_render=True
for m in list(bpy.data.meshes):
    if m.users==0: bpy.data.meshes.remove(m)
names=json.load(open(S+'bt/dump.jsonl.names.json'))
idx={}
bynorm={o.name.replace('.',''):o.name for o in bpy.data.objects}
for i,n in enumerate(names):
    if not n: continue
    nm=bynorm.get(n.replace('.',''))
    if nm: idx[i]=nm
sc['idxmap']=json.dumps(idx)
print('MAPPED',len(idx),'of',len(names))
# ---------- client shrimp pool
def norm_axis0(objs,target):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for o in objs if o.type=='MESH' for c in o.bound_box]
    ext=max(p[0] for p in pts)-min(p[0] for p in pts); return target/ext
shr=imp(P+'shrimp_ae.glb')
for o in list(shr):
    if o.name.startswith('Icosphere'): bpy.data.objects.remove(o); shr.remove(o)
rig=[o for o in shr if o.type=='ARMATURE'][0]; mesh=[o for o in shr if o.type=='MESH'][0]
rig.name='SHR_000'; mesh.name='SHRM_000'
if rig.animation_data: rig.animation_data.action=None
mt=mesh.data.materials[0]; bs=[x for x in mt.node_tree.nodes if x.type=='BSDF_PRINCIPLED'][0]
bs.inputs['Transmission Weight'].default_value=0.3; bs.inputs['Roughness'].default_value=0.28
bs.inputs['Subsurface Weight'].default_value=0.25; bs.inputs['Subsurface Radius'].default_value=(0.004,0.003,0.002)
bs.inputs['Coat Weight'].default_value=0.4; bs.inputs['Alpha'].default_value=0.8; bs.inputs['Emission Color'].default_value=(0.55,0.65,0.6,1); bs.inputs['Emission Strength'].default_value=0.06
NSHR=int(os.environ.get('NSHR','98'))
for i in range(1,NSHR):
    r2=rig.copy(); m2=mesh.copy(); sc.collection.objects.link(r2); sc.collection.objects.link(m2)
    r2.name='SHR_%03d'%i; m2.name='SHRM_%03d'%i; m2.parent=r2
    for md in m2.modifiers:
        if md.type=='ARMATURE': md.object=r2
# ---------- pellet pools (client pellet, shared mesh)
pel=imp(P+'user_pellet.glb')[0]; pel.name='PEL_SRC'
lod=imp(P+'user_pellet_lod.glb')[0]; lodlen=max(v.co.x for v in lod.data.vertices)-min(v.co.x for v in lod.data.vertices)
fulllen=max(v.co.x for v in pel.data.vertices)-min(v.co.x for v in pel.data.vertices)
sc['pel_fix']=lodlen/fulllen; print('PELLEN lod',lodlen,'full',fulllen)
bpy.data.objects.remove(lod)
pm=pel.data.materials[0]
for i in range(700):
    q=pel.copy(); sc.collection.objects.link(q); q.name='PEL_%03d'%i; q.hide_render=True
pel.hide_render=True
# bubbles / drops / splash rings
def basic_mat(name,rgb,rough=0.1,trans=0.0,ior=1.33,alpha=1.0,emis=None):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; b.inputs['Transmission Weight'].default_value=trans; b.inputs['IOR'].default_value=ior; b.inputs['Alpha'].default_value=alpha
    if emis: b.inputs['Emission Color'].default_value=(*emis[:3],1); b.inputs['Emission Strength'].default_value=emis[3]
    return m
bubm=basic_mat('Bubble',(1,1,1),0.0,1.0,1/1.33); dropm=basic_mat('Drop',(0.9,0.95,0.95),0.02,1.0,1.33); ringm=basic_mat('Ring',(1,1,1),0.3,0,1.45,0.35)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1,segments=16,ring_count=8); sph=bpy.context.object; sph.name='SPH_SRC'; sph.hide_render=True
for kind,n,m in (('BUB',80,bubm),('DROP',160,dropm)):
    for i in range(n):
        q=sph.copy(); q.data=sph.data; sc.collection.objects.link(q); q.name='%s_%03d'%(kind,i); q.hide_render=True; q.material_slots and None
        q.data.materials.clear() if False else None
        q.active_material=m if False else None
bpy.ops.mesh.primitive_circle_add(vertices=48,radius=0.9,fill_type='NOTHING'); rg=bpy.context.object; rg.name='RING_SRC'; rg.data.transform(Matrix.Rotation(math.radians(90),4,'X')); rg.modifiers.new('sk','SKIN') if False else None
for i in range(40):
    q=rg.copy(); sc.collection.objects.link(q); q.name='RING_%03d'%i; q.hide_render=True
rg.hide_render=True
# per-object material for shared sphere data: use object-linked slots
for o in bpy.data.objects:
    if o.name.startswith(('BUB_','DROP_')):
        if not o.material_slots: o.data.materials.append(None) if not o.data.materials else None
        o.material_slots[0].link='OBJECT'; o.material_slots[0].material= bubm if o.name.startswith('BUB_') else dropm
# ---------- client bag (driven as JS_BAG)
bagobjs=imp(P+'SmartCare_Vital_AM_Bag.glb'); je=bpy.data.objects.new('JS_BAG',None); sc.collection.objects.link(je)
for o in bagobjs:
    if o.parent is None: o.parent=je
# ---------- rigged farmer (Higgsfield image_to_3d), IK right arm, scoop, bucket
sys.path.insert(0,S+'bt'); from farmer_lib import load_farmer, make_scoop, make_bucket
arm,body=load_farmer(imp); arm.name='FARMER_RIG'; body.name='FARMER_BODY'
arm.location=(0,9.62+0.2,0.16); arm.rotation_mode='XYZ'; arm.rotation_euler=(0,0,0)
for pb in arm.pose.bones: pb.rotation_mode='XYZ'
tg=bpy.data.objects.new('HAND_TGT',None); sc.collection.objects.link(tg)
pl=bpy.data.objects.new('ELBOW_POLE',None); sc.collection.objects.link(pl)
ik=arm.pose.bones['RightForeArm'].constraints.new('IK'); ik.target=tg; ik.pole_target=pl; ik.chain_count=2; ik.pole_angle=math.radians(-90)
sr=make_scoop(arm); sr.name='SCOOP'
bk=make_bucket((-0.42,9.5,0.16)); bk.name='BUCKET_BODY'; bpy.context.object.name='BUCKET_FEED'
bynorm={o.name.replace('.',''):o.name for o in bpy.data.objects}; idx={}
for i,n in enumerate(names):
    if n and bynorm.get(n.replace('.','')): idx[i]=bynorm[n.replace('.','')]
sc['idxmap']=json.dumps(idx); print('MAPPED2',len(idx))
cd=bpy.data.cameras.new('FILM_CAM'); cd.sensor_fit='HORIZONTAL'; cd.sensor_width=36; co=bpy.data.objects.new('FILM_CAM',cd); sc.collection.objects.link(co); sc.camera=co
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film_base.blend')
print('SAVED')
