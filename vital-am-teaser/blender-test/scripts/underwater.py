import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/bt')
from common import *
random.seed(7)
sc=reset(); W,H,SAMP=[int(x) for x in sys.argv[sys.argv.index('--')+1:][:3]]; OUT=sys.argv[-1]
sc.render.resolution_x=W; sc.render.resolution_y=H; sc.cycles.samples=SAMP
sc.cycles.volume_step_rate=4; sc.cycles.max_bounces=6; sc.cycles.volume_bounces=1; sc.cycles.transmission_bounces=6
# world: dim teal so the volume gets ambient
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.05,0.10,0.07,1); bg.inputs[1].default_value=1.0
# water volume box (z from -1.6 to 0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,-0.8)); vol=bpy.context.object; vol.scale=(40,40,1.6); vol.name='WaterVolume'
m,n,l=node_mat('WaterVol'); n.remove(n['Principled BSDF']); pv=n.new('ShaderNodeVolumePrincipled')
pv.inputs['Color'].default_value=(0.22,0.42,0.26,1); pv.inputs['Density'].default_value=float(__import__('os').environ.get('DENS','0.25')); pv.inputs['Anisotropy'].default_value=0.75
pv.inputs['Absorption Color'].default_value=(0.30,0.55,0.36,1)
l.new(pv.outputs[0], n['Material Output'].inputs['Volume']); vol.data.materials.append(m)
# water surface (seen from below): glass with wave bump
bpy.ops.mesh.primitive_plane_add(size=80, location=(0,0,0)); surf=bpy.context.object; surf.name='WaterSurface'
m,n,l=node_mat('Surface'); bs=n['Principled BSDF']; bs.inputs['Transmission Weight'].default_value=1; bs.inputs['Roughness'].default_value=0.02; bs.inputs['IOR'].default_value=1.33
nz=n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.0; nz.inputs['Detail'].default_value=6
bp=n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.35; l.new(nz.outputs['Fac'],bp.inputs['Height']); l.new(bp.outputs['Normal'],bs.inputs['Normal'])
surf.data.materials.append(m); surf.visible_shadow=False
# silt floor
bpy.ops.mesh.primitive_plane_add(size=80, location=(0,0,-1.6)); fl=bpy.context.object
bpy.ops.object.modifier_add(type='SUBSURF'); fl.modifiers[0].levels=6; fl.modifiers[0].render_levels=7; fl.modifiers[0].subdivision_type='SIMPLE'
m,n,l=node_mat('Silt'); bs=n['Principled BSDF']; nz=n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=6; nz.inputs['Detail'].default_value=10
cr=n.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.06,0.06,0.03,1); cr.color_ramp.elements[1].color=(0.16,0.15,0.08,1)
l.new(nz.outputs['Fac'],cr.inputs[0]); l.new(cr.outputs[0],bs.inputs['Base Color']); bs.inputs['Roughness'].default_value=1
dp=n.new('ShaderNodeDisplacement'); dp.inputs['Scale'].default_value=0.04; l.new(nz.outputs['Fac'],dp.inputs['Height']); l.new(dp.outputs[0],n['Material Output'].inputs['Displacement'])
m.cycles.displacement_method='BOTH'; fl.data.materials.append(m)
# sun from above-front, slightly soft -> god rays through the volume
sd=bpy.data.lights.new('Sun','SUN'); sd.energy=18; sd.angle=math.radians(1.5); sd.color=(1.0,0.93,0.78)
so=bpy.data.objects.new('Sun',sd); sc.collection.objects.link(so); so.rotation_euler=(math.radians(20),math.radians(-12),math.radians(15))

# bright sky seen through the surface (camera-visible only, no shadows)
bpy.ops.mesh.primitive_plane_add(size=120, location=(0,0,3)); skyp=bpy.context.object
m,n,l=node_mat('SkyEm'); n.remove(n['Principled BSDF']); em=n.new('ShaderNodeEmission'); em.inputs[0].default_value=(1.0,0.93,0.80,1); em.inputs[1].default_value=0.45
l.new(em.outputs[0],n['Material Output'].inputs['Surface']); skyp.data.materials.append(m); skyp.visible_shadow=False
# gobo with irregular gaps above the water -> visible light shafts in the volume
bpy.ops.mesh.primitive_plane_add(size=80, location=(0,0,0.6)); gob=bpy.context.object
m,n,l=node_mat('Gobo'); bs=n['Principled BSDF']; nz=n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.6; nz.inputs['Detail'].default_value=3
cr=n.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.48; cr.color_ramp.elements[1].position=0.53
l.new(nz.outputs['Fac'],cr.inputs[0]); l.new(cr.outputs[0],bs.inputs['Alpha']); bs.inputs['Base Color'].default_value=(0,0,0,1)
gob.data.materials.append(m); gob.visible_camera=False; gob.visible_diffuse=False; gob.visible_glossy=False; gob.visible_transmission=False; gob.visible_volume_scatter=False
# --- shrimp: import once, then linked duplicates with NLA time offsets
src=imp(P+'shrimp_ae.glb')
for o in src:
    if o.name.startswith('Icosphere'): bpy.data.objects.remove(o)
src=[o for o in bpy.data.objects if o.name in ('ShrimpRig','Shrimp1')]
rig=[o for o in src if o.type=='ARMATURE'][0]; mesh=[o for o in src if o.type=='MESH'][0]
s=norm_size(src,0.137,axis=0)
# glTF Y-up -> Blender: shrimp long axis currently along Y; measure heading later per instance via rotation_z
mt=mesh.data.materials[0]; nt=mt.node_tree; bs=[x for x in nt.nodes if x.type=='BSDF_PRINCIPLED'][0]
bs.inputs['Transmission Weight'].default_value=0.3; bs.inputs['Roughness'].default_value=0.28
bs.inputs['Subsurface Weight'].default_value=0.25; bs.inputs['Subsurface Radius'].default_value=(0.004,0.003,0.002)
bs.inputs['Coat Weight'].default_value=0.4; bs.inputs['Alpha'].default_value=0.85
act=bpy.data.actions[0]
def place(rigobj,loc,yaw,pitch,toff):
    rigobj.rotation_mode='XYZ'; rigobj.location=loc; rigobj.rotation_euler=(0,pitch,yaw)
    ad=rigobj.animation_data or rigobj.animation_data_create(); ad.action=None
    tr=ad.nla_tracks.new(); st=tr.strips.new('swim',int(toff),act); st.extrapolation='HOLD'
shr=[(rig,mesh)]
for i in range(26):
    r2=rig.copy(); m2=mesh.copy(); sc.collection.objects.link(r2); sc.collection.objects.link(m2)
    m2.parent=r2; m2.modifiers[0].object=r2 if m2.modifiers else None; shr.append((r2,m2))
FEEDT=1
# layout: a loose school around a feeding column in front of camera, mid-water (z -0.5..-1.2), none closer than 0.14 m
pts=[]
while len(pts)<len(shr):
    p=Vector((random.uniform(-0.55,0.55),random.uniform(0.35,1.6),random.uniform(-1.15,-0.55)))
    if all((p-q).length>0.17 for q in pts): pts.append(p)
for (r,mm),p in zip(shr,pts):
    to=Vector((random.gauss(0,0.15),p.y+random.uniform(-0.3,0.3),0))-Vector((p.x,p.y,0)); yaw=math.atan2(to.y,to.x)+math.pi+random.uniform(-0.6,0.6); place(r,p,yaw,random.uniform(-0.22,0.12),-random.randint(0,180))
# pellets: client mesh, 3.2 mm long, many falling through the column
pel=imp(P+'user_pellet.glb')[0]; norm_size([pel],0.0032)
pel.location=(0,1.2,-0.6)
for i in range(160):
    q=pel.copy(); sc.collection.objects.link(q)
    q.location=(random.gauss(0,0.3),random.uniform(0.25,1.4),random.uniform(-1.2,-0.3)); q.rotation_euler=[random.uniform(0,6.3) for _ in range(3)]
# foreground pellets near the lens and in front of shrimp mouths so the real size reads
for i in range(14):
    q=pel.copy(); sc.collection.objects.link(q); q.location=(random.uniform(-0.12,0.12),random.uniform(-0.25,0.05),random.uniform(-1.12,-0.95)); q.rotation_euler=[random.uniform(0,6.3) for _ in range(3)]
for (r,mm) in shr[:12]:
    hd=r.matrix_world@Vector((-0.07/r.scale[0],0,0)); q=pel.copy(); sc.collection.objects.link(q); q.location=hd+Vector((random.gauss(0,0.01),random.gauss(0,0.01),0.01)); q.rotation_euler=[random.uniform(0,6.3) for _ in range(3)]
# a few bubbles
bm,bn,bl=node_mat('Bubble'); bb=bn['Principled BSDF']; bb.inputs['Transmission Weight'].default_value=1; bb.inputs['IOR'].default_value=1.0/1.33; bb.inputs['Roughness'].default_value=0
for i in range(40):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.0008,0.002),location=(random.gauss(0,0.3),random.uniform(0.5,2.0),random.uniform(-1.0,-0.05)),segments=12,ring_count=8)
    bpy.context.object.data.materials.append(bm)
bpy.context.view_layer.update(); sc.frame_set(FEEDT); sc.view_settings.look='AgX - High Contrast'
if __import__('os').environ.get('CAMMODE')=='macro':
    r0,m0=shr[0]; r0.location=(0,0.5,-0.7); r0.rotation_euler=(0,0.1,math.radians(-90)); bpy.context.view_layer.update()
    head=r0.matrix_world@Vector((-0.075/r0.scale[0],0,0.01/r0.scale[0]))
    hp=pel.copy(); sc.collection.objects.link(hp); hp.location=head+Vector((0.0,-0.012,0.018)); hp.rotation_euler=(0.4,1.1,0.3)
    cc=cam(head+Vector((0.07,-0.17,0.03)),head+Vector((0.0,0,0.008)),lens=60); cc.data.dof.use_dof=True; cc.data.dof.focus_distance=(cc.location-hp.location).length; cc.data.dof.aperture_fstop=4.0
else:
    cam((0.0,-0.45,-1.05),(0,1.2,-0.62),lens=30)
sc.render.filepath=OUT
import time; t=time.time(); bpy.ops.render.render(write_still=True); print('RENDER_SECONDS',round(time.time()-t,1))
bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.png','.blend'))
