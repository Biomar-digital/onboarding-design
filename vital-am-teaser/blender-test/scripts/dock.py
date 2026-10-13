import sys,os; sys.path.insert(0,'/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/bt')
from common import *
from farmer_lib import *
random.seed(3)
a=sys.argv[sys.argv.index('--')+1:]; MODE=a[0]; W,H,SAMP=int(a[1]),int(a[2]),int(a[3]); OUT=a[4]
sc=reset(); sc.render.resolution_x=W; sc.render.resolution_y=H; sc.cycles.samples=SAMP
# --- sky: Nishita sunrise
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; nt=w.node_tree; sk=nt.nodes.new('ShaderNodeTexSky'); sk.sky_type='NISHITA'
SUN_EL=math.radians(float(os.environ.get('SUNEL','6'))); SUN_AZ=math.radians(float(os.environ.get('SUNAZ','14')))   # sun straight ahead (+Y)
sk.sun_elevation=SUN_EL; sk.sun_rotation=SUN_AZ+math.pi; sk.altitude=50; sk.air_density=1.0; sk.dust_density=1.2; sk.ozone_density=1.5; sk.sun_intensity=0.22
nt.links.new(sk.outputs[0],nt.nodes['Background'].inputs[0]); nt.nodes['Background'].inputs[1].default_value=0.5
sd=bpy.data.lights.new('Sun','SUN'); sd.energy=1.8; sd.angle=math.radians(2); sd.color=(1.0,0.72,0.45); sd.specular_factor=0.25
so=bpy.data.objects.new('Sun',sd); sc.collection.objects.link(so)
d=Vector((-math.sin(SUN_AZ), math.cos(SUN_AZ), math.tan(SUN_EL))).normalized()   # direction TO sun (+Y, slightly up)
so.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
# --- pond water
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,0)); wat=bpy.context.object
oc=wat.modifiers.new('Ocean','OCEAN'); oc.geometry_mode='GENERATE'; oc.spatial_size=40; oc.resolution=14; oc.repeat_x=10; oc.repeat_y=10
oc.wave_scale=0.05; oc.choppiness=0.6; oc.wind_velocity=4.0; oc.wave_alignment=0.3; oc.random_seed=4; oc.time=1.0
wat.location=(-200,-60,0)
m,n,l=node_mat('Pond'); bs=n['Principled BSDF']; bs.inputs['Base Color'].default_value=(0.02,0.045,0.03,1); bs.inputs['Roughness'].default_value=0.07; bs.inputs['IOR'].default_value=1.33
bs.inputs['Specular IOR Level'].default_value=0.6
tc=n.new('ShaderNodeTexCoord'); mp=n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(0.6,4.5,1); l.new(tc.outputs['Object'],mp.inputs[0])
nz=n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=8; nz.inputs['Roughness'].default_value=0.55; l.new(mp.outputs[0],nz.inputs[0])
nz2=n.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value=40; nz2.inputs['Detail'].default_value=4; l.new(mp.outputs[0],nz2.inputs[0])
ad=n.new('ShaderNodeMath'); ad.operation='ADD'; l.new(nz2.outputs['Fac'],ad.inputs[1])
bp=n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.3; bp.inputs['Distance'].default_value=0.02; l.new(nz.outputs['Fac'],ad.inputs[0]); l.new(ad.outputs[0],bp.inputs['Height']); l.new(bp.outputs['Normal'],bs.inputs['Normal'])
wat.data.materials.append(m)
# --- far bank (dike) with grass + tree line silhouettes
def mat_rgb(name,rgb,rough=0.9):
    m,n,l=node_mat(name); b=n['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; return m
grass=mat_rgb('Grass',(0.05,0.07,0.025)); trunk=mat_rgb('Trunk',(0.06,0.045,0.03)); frond=mat_rgb('Frond',(0.025,0.05,0.02)); wall=mat_rgb('Wall',(0.25,0.17,0.10)); roof=mat_rgb('Roof',(0.20,0.13,0.07))
BANK_Y=140
bpy.ops.mesh.primitive_cube_add(location=(0,BANK_Y,0.35)); bk=bpy.context.object; bk.scale=(300,3,0.4); bk.data.materials.append(grass)
def palm(x,y,h,lean):
    curve=bpy.data.curves.new('tr','CURVE'); curve.dimensions='3D'; curve.bevel_depth=0.11+0.02*random.random(); sp=curve.splines.new('BEZIER'); sp.bezier_points.add(1)
    p0=Vector((x,y,0.6)); p1=Vector((x+lean,y,h)); sp.bezier_points[0].co=p0; sp.bezier_points[1].co=p1
    for bpnt,c in ((sp.bezier_points[0],p0),(sp.bezier_points[1],p1)): bpnt.handle_left_type=bpnt.handle_right_type='AUTO'
    t=bpy.data.objects.new('Palm',curve); sc.collection.objects.link(t); t.data.materials.append(trunk)
    for k in range(11):
        ang=k/11*2*math.pi+random.uniform(-0.2,0.2); L=random.uniform(2.2,3.0)
        fc=bpy.data.curves.new('fr','CURVE'); fc.dimensions='3D'; fc.bevel_depth=0.0; fc.extrude=0.0
        fc.bevel_mode='ROUND'; fc.bevel_depth=0.05
        s2=fc.splines.new('BEZIER'); s2.bezier_points.add(2)
        a0=p1; a1=p1+Vector((math.cos(ang)*L*0.5,math.sin(ang)*L*0.5,0.5)); a2=p1+Vector((math.cos(ang)*L,math.sin(ang)*L,-0.9))
        for bpnt,c in zip(s2.bezier_points,(a0,a1,a2)): bpnt.co=c; bpnt.handle_left_type=bpnt.handle_right_type='AUTO'
        s2.bezier_points[0].radius=0.4; s2.bezier_points[1].radius=2.4; s2.bezier_points[2].radius=0.2
        f=bpy.data.objects.new('Frond',fc); sc.collection.objects.link(f); f.data.materials.append(frond); f.scale=(1,1,1)
for i in range(34):
    x=random.uniform(-160,160); palm(x,BANK_Y+random.uniform(-1,1),random.uniform(9,14),random.uniform(-1.5,1.5))
for i in range(80):   # low bushes for a continuous tree line
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=random.uniform(2.5,5),location=(random.uniform(-200,200),BANK_Y+random.uniform(0,6),random.uniform(0.8,2.0)))
    bpy.context.object.scale=(1.6,1,0.6); bpy.context.object.data.materials.append(frond)
# hut on the far right
bpy.ops.mesh.primitive_cube_add(location=(30,BANK_Y-2,2.0)); h=bpy.context.object; h.scale=(3,2.5,1.6); h.data.materials.append(wall)
bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=5.2,depth=2.4,location=(30,BANK_Y-2,4.8)); r=bpy.context.object; r.rotation_euler=(0,0,math.radians(45)); r.scale=(1,0.85,1); r.data.materials.append(roof)
# --- wooden dock + pallet (procedural wood)
m,n,l=node_mat('Wood'); b=n['Principled BSDF']; wv=n.new('ShaderNodeTexWave'); wv.wave_type='BANDS'; wv.inputs['Scale'].default_value=3.5; wv.inputs['Distortion'].default_value=6; wv.inputs['Detail'].default_value=6
cr=n.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.13,0.08,0.045,1); cr.color_ramp.elements[1].color=(0.30,0.20,0.12,1)
tc=n.new('ShaderNodeTexCoord'); mp=n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1,8,1); l.new(tc.outputs['Object'],mp.inputs[0]); l.new(mp.outputs[0],wv.inputs[0])
l.new(wv.outputs['Fac'],cr.inputs[0]); l.new(cr.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.75; wood=m
def board(loc,size):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.scale=[v/2 for v in size]; o.data.materials.append(wood)
    bpy.ops.object.modifier_add(type='BEVEL'); o.modifiers[0].width=0.006; o.modifiers[0].segments=2; return o
DOCK_LEN=6.0
for i in range(int(DOCK_LEN/0.16)):          # deck planks across, dock runs along +Y into the pond
    board((random.uniform(-0.004,0.004), i*0.16-1.0, 0.55),(1.2,0.145,0.035))
for x in (-0.55,0.55):
    board((x,DOCK_LEN/2-1.0,0.51),(0.08,DOCK_LEN,0.06))
    for y in range(0,int(DOCK_LEN),1.5 and 2): board((x,y-1.0,0.0),(0.1,0.1,1.1))
if MODE=='bag':
    # pallet at the dock end, bag on top
    PY=DOCK_LEN-1.6
    for k in range(5): board((0,PY-0.32+k*0.16,0.62),(0.8,0.10,0.022))
    for x in (-0.33,0,0.33): board((x,PY,0.592),(0.08,0.75,0.06))
    bag=imp(P+'SmartCare_Vital_AM_Bag.glb'); bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for o in bag if o.type=='MESH' for c in o.bound_box]; zmin=min(p.z for p in pts)
    for o in roots(bag): o.location=(0,PY,0.632-zmin); o.rotation_euler=(0,0,math.radians(180))
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for o in bag if o.type=='MESH' for c in o.bound_box]; print('BAGBB',[round(min(p[i] for p in pts),3) for i in range(3)],[round(max(p[i] for p in pts),3) for i in range(3)])
    c=cam((0.3,PY-3.4,1.0),(-0.1,PY,0.95),lens=38)
elif MODE=='farmer':
    FY=DOCK_LEN-1.5
    arm,body=load_farmer(imp); arm.rotation_mode='XYZ'; arm.location=(0.05,FY,0.5725); arm.rotation_euler=(0,0,math.radians(180))
    pose(arm,{'RightArm':(62,0,-22),'RightForeArm':(12,0,0),'LeftArm':(0,0,float(os.environ.get('LZ','-25'))),'LeftForeArm':(10,0,0),'Spine':(0,0,-8),'neck':(-6,0,0)})
    sr=make_scoop(arm)
    attach_to_hand(sr,arm,'RightHand',off=(0,0.06,0),rot=(0,0,0))
    make_bucket((0.42,FY-0.15,0.5725))
    # broadcast spray: real-size pellets on ballistic arcs from the scoop toward the pond
    pel=imp(P+'user_pellet.glb')[0]; norm_size([pel],0.0032)
    bpy.context.view_layer.update(); S0=sr.matrix_world.translation.copy()
    for i in range(700):
        t=random.uniform(0.05,0.75); v=Vector((random.gauss(0.6,0.5),random.uniform(3.2,4.6),random.uniform(1.0,2.2)))
        q=pel.copy(); sc.collection.objects.link(q); q.location=S0+v*t+Vector((0,0,-4.9*t*t)); q.rotation_euler=[random.uniform(0,6.3) for _ in range(3)]
        if q.location.z<0.02: q.location.z=random.uniform(0.02,0.4)
    pel.location=(0,0,-5)
    c=cam((-1.1,FY-4.3,1.35),(0.2,FY+2.0,1.2),lens=32)
# atmospheric haze via mist pass in the compositor
sc.view_layers[0].use_pass_mist=True; w.mist_settings.start=20; w.mist_settings.depth=200; w.mist_settings.falloff='QUADRATIC'
sc.use_nodes=True; ct=sc.node_tree; rl=ct.nodes['Render Layers']; comp=ct.nodes['Composite']
mx=ct.nodes.new('CompositorNodeMixRGB'); mx.blend_type='MIX'; mx.inputs[2].default_value=(0.80,0.74,0.66,1)
mm=ct.nodes.new('CompositorNodeMath'); mm.operation='MULTIPLY'; mm.inputs[1].default_value=0.35
ct.links.new(rl.outputs['Mist'],mm.inputs[0]); ct.links.new(mm.outputs[0],mx.inputs[0]); ct.links.new(rl.outputs['Image'],mx.inputs[1]); ct.links.new(mx.outputs[0],comp.inputs[0])
sc.render.filepath=OUT
import time; t=time.time(); bpy.ops.render.render(write_still=True); print('RENDER_SECONDS',round(time.time()-t,1))
bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.png','.blend'))
