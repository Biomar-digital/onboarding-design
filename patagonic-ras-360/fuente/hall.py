# Patagonic RAS 360: one shared underwater world around the hall, one "window" camera per LED screen.
# blender -b --factory-startup -P hall.py -- OUTDIR T0 FRAMES SCALE
import bpy, bmesh, sys, math, random, mathutils, os
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import hallgeo as hg; from school import simulate
args=sys.argv[sys.argv.index('--')+1:]
OUT=args[0]; T0=float(args[1]); F=int(args[2]); SCALE=float(args[3]); ONLY=args[4].split(',') if len(args)>4 else None   # optional: only these screens
os.makedirs(OUT,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene
def mk(name,build):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); sc.collection.objects.link(ob); return ob
# ---------------- fish (client model, original material)
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE,'fish_feeding.glb'))
for o in sc.objects:
    if o.name.startswith('Icosphere'): o.hide_render=True; o.hide_viewport=True
arm=[o for o in sc.objects if o.type=='ARMATURE'][0]
body=max([o for o in sc.objects if o.type=='MESH'],key=lambda o:len(o.data.vertices))
act=bpy.data.actions[0]
roots=[o for o in sc.objects if o.parent is None and not o.name.startswith('Icosphere')]
root=bpy.data.objects.new('FishRoot',None); sc.collection.objects.link(root)
for o in roots: o.parent=root
bpy.context.view_layer.update()
bb=[body.matrix_world@mathutils.Vector(c) for c in body.bound_box]
L=max(max(v[i] for v in bb)-min(v[i] for v in bb) for i in range(3))
def dup_fish():
    objs=[root]+[o for o in root.children_recursive if not o.name.startswith('Icosphere')]
    m={}
    for o in objs:
        c=o.copy()
        if o.type=='ARMATURE': c.animation_data_clear()
        sc.collection.objects.link(c); m[o]=c
    for o,c in m.items():
        if o.parent in m: c.parent=m[o.parent]
        for md in c.modifiers:
            if md.type=='ARMATURE' and md.object in m: md.object=m[md.object]
    return m[root],[c for o,c in m.items() if o.type=='ARMATURE'][0]
fr=act.frame_range
def swim(a,phase,v):
    a.animation_data_create(); tr=a.animation_data.nla_tracks.new(); st=tr.strips.new('swim',int(fr[0]),act)
    st.repeat=30; st.scale=0.9                    # close to the authored speed: calm, not violent
    st.frame_start=fr[0]-phase
    st.use_animated_influence=True; st.influence=0.6; st.keyframe_insert('influence',frame=1)   # 60% amplitude
arm.animation_data.action=None
# ---------------- depth layers: schools at different distances behind the screens + loners
# each layer has its own circuit (parallel to the screens, `behind` metres back) and does 1 lap in 90 s
def lead_fn(C,S_,LEN,phase_s,sgn=1,bob=0.25):
    V=LEN/90.0
    def lead(t):
        s=(sgn*V*(t+T0+phase_s))%LEN; i=np.searchsorted(S_,s,side='right')-1; i=max(0,min(i,len(C)-1))
        a=C[i]; b=C[(i+1)%len(C)]; u=(s-S_[i])/max(S_[i+1]-S_[i],1e-6); p=a+(b-a)*u
        d=b-a; d=sgn*d/np.linalg.norm(d)*V
        p=p.copy(); p[2]+=bob*math.sin(0.4*(t+T0)+phase_s)
        return p,d
    return lead
# (name, behind m, height offset m, direction, [(fish, phase s), ...], spread)
LAYERS=[
 ('cerca',  1.4,  -0.2,  1, [(9, 29.6),(7, 81.5)],                 0.6),
 ('medio',  3.5,   0.0,  1, [(34, 14.2),(22, 45.5),(26, 71.5)],    1.0),
 ('lejos',  7.5,   0.7, -1, [(40, 5.4),(30, 35.2),(30, 64.9)],     1.2),   # swims the other way
 ('fondo', 15.0,  -0.4,  1, [(60, 22.2),(50, 67.1)],               2.0),   # big schools fading into the haze
]
random.seed(11); rng=np.random.default_rng(3)
plan=[]
for name,beh,dz,sgn,schools,spr in LAYERS:
    C,S_,LEN=hg.circuit(behind=beh,dz=dz)
    for ns,ph in schools: plan.append((C,S_,LEN,ph,sgn,ns,spr,0.25))
for k in range(7):                                   # loners: single salmon at random depths and heights
    C,S_,LEN=hg.circuit(behind=float(rng.uniform(1.0,9.0)),dz=float(rng.uniform(-1.0,1.2)))
    plan.append((C,S_,LEN,float(rng.uniform(0,90)),1 if k%3 else -1,1,1.0,0.6))
NT=sum(p[5] for p in plan); fish=[(root,arm)]
for i in range(NT-1): fish.append(dup_fish())
k=0
for q,(C,S_,LEN,ph,sgn,ns,spr,bob) in enumerate(plan):
    P,Vt=simulate(lead_fn(C,S_,LEN,ph,sgn,bob),F,ns,seed=5+q,spread=spr)
    for j in range(ns):
        r,a=fish[k]; k+=1
        r.scale=(0.7/L*random.uniform(0.85,1.15)*(1.15 if ns==1 else 1.0),)*3
        yw=None; bk=0.0
        for f in range(F):
            v=Vt[f,j]; yaw=math.atan2(v[0],-v[1]); h=math.hypot(v[0],v[1]); pitch=max(-0.21,min(0.21,-math.atan2(v[2],h)))
            if yw is not None:
                dy=(yaw-yw+math.pi)%(2*math.pi)-math.pi; yaw=yw+dy; bk=0.85*bk+0.15*max(-0.35,min(0.35,-dy*24*0.3))
            yw=yaw
            r.location=P[f,j]; r.rotation_euler=(pitch,bk,yaw)
            r.keyframe_insert('location',frame=f+1); r.keyframe_insert('rotation_euler',frame=f+1)
        swim(a,random.randint(0,190),0)
print('FISH',NT)
# ---------------- water world
CX,CY=23.0,-8.0
box=mk('WaterBox',lambda bm: bmesh.ops.create_cube(bm,size=1.0)); box.location=(CX,CY,-1.0); box.scale=(150,150,15.0)
vm=bpy.data.materials.new('water'); vm.use_nodes=True; vn=vm.node_tree; vn.nodes.remove(vn.nodes['Principled BSDF'])
vol=vn.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Color'].default_value=(0.24,0.46,0.45,1); vol.inputs['Density'].default_value=0.085
vol.inputs['Anisotropy'].default_value=0.75; vol.inputs['Absorption Color'].default_value=(0.45,0.72,0.7,1)
vn.links.new(vol.outputs[0],vn.nodes['Material Output'].inputs['Volume']); box.data.materials.append(vm)
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.16,0.3,0.31,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.6
sun=bpy.data.lights.new('sun','SUN'); sun.energy=34; sun.color=(0.92,0.98,1.0); sun.angle=math.radians(2)
so=bpy.data.objects.new('sun',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(-30),math.radians(25),math.radians(-20))
ZS=9.0
surf=mk('Surface',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); surf.location=(CX,CY,ZS)
sm=bpy.data.materials.new('surf'); sm.use_nodes=True; sb=sm.node_tree.nodes['Principled BSDF']; sb.inputs['Transmission Weight'].default_value=1; sb.inputs['Roughness'].default_value=0.05; sb.inputs['IOR'].default_value=1.33
sn=sm.node_tree; wv=sn.nodes.new('ShaderNodeTexNoise'); wv.inputs['Scale'].default_value=3.5; wv.inputs['Detail'].default_value=8; wv.inputs['Distortion'].default_value=1.5
bmp=sn.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value=1.0; sn.links.new(wv.outputs['Fac'],bmp.inputs['Height']); sn.links.new(bmp.outputs['Normal'],sb.inputs['Normal'])
surf.data.materials.append(sm); surf.visible_shadow=False
gobo=mk('Gobo',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); gobo.location=(CX,CY,ZS-0.3)
gm=bpy.data.materials.new('gobo'); gm.use_nodes=True; gn=gm.node_tree; gb=gn.nodes['Principled BSDF']
cv=gn.nodes.new('ShaderNodeTexVoronoi'); cv.feature='DISTANCE_TO_EDGE'; cv.inputs['Scale'].default_value=1.4
gco=gn.nodes.new('ShaderNodeTexCoord'); wrp=gn.nodes.new('ShaderNodeTexNoise'); wrp.inputs['Scale'].default_value=0.6
wad=gn.nodes.new('ShaderNodeVectorMath'); wad.operation='ADD'; gn.links.new(gco.outputs['Object'],wad.inputs[0]); gn.links.new(wrp.outputs['Color'],wad.inputs[1])
gn.links.new(gco.outputs['Object'],wrp.inputs['Vector']); gn.links.new(wad.outputs[0],cv.inputs['Vector'])
gr=gn.nodes.new('ShaderNodeValToRGB'); gr.color_ramp.elements[0].position=0.05; gr.color_ramp.elements[0].color=(1,1,1,1); gr.color_ramp.elements[1].position=0.16; gr.color_ramp.elements[1].color=(0.12,0.12,0.12,1)
gn.links.new(cv.outputs['Distance'],gr.inputs[0]); inv=gn.nodes.new('ShaderNodeInvert'); gn.links.new(gr.outputs['Color'],inv.inputs['Color'])
gn.links.new(inv.outputs['Color'],gb.inputs['Alpha']); gb.inputs['Base Color'].default_value=(0,0,0,1); gobo.data.materials.append(gm)
for v in ('visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter'): setattr(gobo,v,False)
sky=mk('Sky',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); sky.location=(CX,CY,ZS+4)
km=bpy.data.materials.new('sky'); km.use_nodes=True; kn=km.node_tree; kn.nodes.remove(kn.nodes['Principled BSDF'])
em=kn.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value=(1.2,1.35,1.35,1); em.inputs["Strength"].default_value=1.0
kn.links.new(em.outputs[0],kn.nodes['Material Output'].inputs['Surface']); sky.data.materials.append(km); sky.visible_shadow=False
floor=mk('Floor',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); floor.location=(CX,CY,-8)
fm=bpy.data.materials.new('floor'); fm.use_nodes=True; fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.02,0.04,0.045,1); floor.data.materials.append(fm)
# ---------------- marine snow + bubbles, placed in the water seen through each screen
def flake(bm):
    bmesh.ops.create_icosphere(bm,subdivisions=1,radius=1.0)
    for v in bm.verts: v.co*=random.uniform(0.45,1.25)
    for v in bm.verts: v.co.z*=0.35
dm=bpy.data.materials.new('snow'); dm.use_nodes=True; dn=dm.node_tree; dn.nodes.remove(dn.nodes['Principled BSDF'])
trn=dn.nodes.new('ShaderNodeBsdfTransparent'); dsc=dn.nodes.new('ShaderNodeBsdfTranslucent'); dsc.inputs['Color'].default_value=(0.9,0.97,0.95,1)
dmx=dn.nodes.new('ShaderNodeMixShader'); dmx.inputs['Fac'].default_value=0.45; dn.links.new(trn.outputs[0],dmx.inputs[1]); dn.links.new(dsc.outputs[0],dmx.inputs[2])
dn.links.new(dmx.outputs[0],dn.nodes['Material Output'].inputs['Surface'])
flakes=[]
for q in range(16):
    f_=mk(f'Flake{q}',flake); f_.data.materials.append(dm); f_.location=(0,-500,0); f_.visible_shadow=False; flakes.append(f_)
for s in hg.SC:
    c,n,t=s['c'],s['n'],s['t']
    for i in range(int(450*max(1,s['W']/3))):
        d=random.choice(flakes).copy(); sc.collection.objects.link(d)
        depth=random.uniform(0.2,9); lat=random.uniform(-1,1)*(s['W']/2+depth*0.8)
        d.location=tuple(c-n*depth+t*lat+np.array([0,0,random.uniform(-s['H']/2-depth*0.5,s['H']/2+depth*0.5)]))
        sz=0.0012*math.exp(random.gauss(0,0.45)) if random.random()>0.04 else 0.006*math.exp(random.gauss(0,0.35))
        d.scale=(sz*random.uniform(0.5,1.5),sz*random.uniform(0.5,1.5),sz); d.rotation_euler=(random.uniform(0,6.3),random.uniform(0,6.3),random.uniform(0,6.3))
bm_=bpy.data.materials.new('bubble'); bm_.use_nodes=True; bbn=bm_.node_tree.nodes['Principled BSDF']
bbn.inputs['Transmission Weight'].default_value=1; bbn.inputs['IOR'].default_value=0.75; bbn.inputs['Roughness'].default_value=0.0
bub=mk('Bubble',lambda bm: bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=8,radius=1.0)); bub.data.materials.append(bm_); bub.location=(0,-500,0)
for p in bub.data.polygons: p.use_smooth=True
for s in hg.SC[::2]:
    base=s['c']-s['n']*random.uniform(3,7)+s['t']*random.uniform(-s['W'],s['W'])
    for i in range(120):
        d=bub.copy(); sc.collection.objects.link(d); h=random.uniform(-3,ZS)
        d.location=(base[0]+random.gauss(0,0.12+0.02*(h+3)),base[1]+random.gauss(0,0.12+0.02*(h+3)),h)
        r_=random.uniform(0.0015,0.006); d.scale=(r_,r_,r_*0.8); d.visible_shadow=False
# ---------------- one window camera per screen (off-axis: the frustum passes exactly through the screen)
cams=[]
for s in hg.SC:
    cd=bpy.data.cameras.new(s['name']); co=bpy.data.objects.new('cam_'+s['name'],cd); sc.collection.objects.link(co)
    eye=mathutils.Vector(s['eye']); look=-mathutils.Vector(s['n'])
    co.location=eye; co.rotation_euler=look.to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    R=co.matrix_world.to_3x3(); loc=R.transposed()@(mathutils.Vector(s['c'])-eye)
    big=max(s['W'],s['H']); D=-loc.z
    cd.sensor_fit='AUTO'; cd.sensor_width=36; cd.lens=D*36/big
    cd.shift_x=loc.x/big; cd.shift_y=loc.y/big; cd.clip_start=D*0.97; cd.clip_end=200
    cams.append((s,co))
# ---------------- render settings
sc.frame_start=1; sc.frame_end=F; sc.render.fps=24
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.cycles.volume_step_rate=10; sc.cycles.max_bounces=3; sc.cycles.transparent_max_bounces=4; sc.cycles.volume_bounces=0
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - High Contrast'
sc.render.image_settings.file_format='PNG'
for s,co in cams:
    if ONLY and s['name'] not in ONLY: continue
    sc.camera=co; sc.render.resolution_x=max(2,int(s['res'][0]*SCALE)); sc.render.resolution_y=max(2,int(s['res'][1]*SCALE))
    sc.render.filepath=os.path.join(OUT,s['name']+('_' if F>1 else '.png'))
    bpy.ops.render.render(write_still=(F==1),animation=(F>1))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'hall.blend'))
print('DONE')
