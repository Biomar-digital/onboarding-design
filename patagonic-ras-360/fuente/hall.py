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
GLB=next(p for p in (os.path.join(HERE,'fish_feeding.glb'),os.path.join(HERE,'..','referencias','Fish_Feeding_boca.glb')) if os.path.exists(p))
bpy.ops.import_scene.gltf(filepath=GLB)
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
    st.repeat=max(30,int((F+400)/max(1,fr[1]-fr[0])/0.9)+2); st.scale=0.9                    # close to the authored speed: calm, not violent
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
 ('cerca',  1.4,  -0.2,  1, [(12, 0.9),(10, 31.6),(10, 61.8)],                0.7),
 ('medio',  3.5,   0.0,  1, [(55, 7.7),(45, 33.3),(50, 54.2),(40, 76.9)],     1.3),
 ('lejos',  7.5,   0.7, -1, [(70, 17.9),(60, 42.9),(60, 63.6),(55, 84.6)],    1.6),   # swims the other way
 ('fondo', 15.0,  -0.4,  1, [(140, 2.2),(120, 30.0),(120, 59.4)],             2.4),   # big schools fading into the haze
 ('pared', 26.0,   0.6, -1, [(220, 25.1),(200, 66.1)],                        3.2),   # far wall of fish: RAS density
]
random.seed(11); rng=np.random.default_rng(3)
plan=[]
for name,beh,dz,sgn,schools,spr in LAYERS:
    C,S_,LEN=hg.circuit(behind=beh,dz=dz)
    for ns,ph in schools: plan.append((C,S_,LEN,ph,sgn,ns,spr,0.25))
for k in range(12):                                   # loners: single salmon at random depths and heights
    C,S_,LEN=hg.circuit(behind=float(rng.uniform(1.0,9.0)),dz=float(rng.uniform(-1.0,1.2)))
    plan.append((C,S_,LEN,float(rng.uniform(0,90)),1 if k%3 else -1,1,1.0,0.6))
if os.environ.get('FEWFISH'): plan=plan[:2]          # quick look-dev of the environment
NT=sum(p[5] for p in plan); fish=[(root,arm)]
for i in range(NT-1): fish.append(dup_fish())
k=0
for q,(C,S_,LEN,ph,sgn,ns,spr,bob) in enumerate(plan):
    P,Vt=simulate(lead_fn(C,S_,LEN,ph,sgn,bob),F,ns,seed=5+q,spread=spr)
    for j in range(ns):
        r,a=fish[k]; k+=1
        r.scale=(0.7/L*random.uniform(0.85,1.15)*(1.15 if ns==1 else 1.0),)*3
        yw=None; bk=0.0; loc=np.zeros((F,3)); rot=np.zeros((F,3))
        for f in range(F):
            v=Vt[f,j]; yaw=math.atan2(v[0],-v[1]); h=math.hypot(v[0],v[1]); pitch=max(-0.21,min(0.21,-math.atan2(v[2],h)))
            if yw is not None:
                dy=(yaw-yw+math.pi)%(2*math.pi)-math.pi; yaw=yw+dy; bk=0.85*bk+0.15*max(-0.35,min(0.35,-dy*24*0.3))
            yw=yaw; loc[f]=P[f,j]; rot[f]=(pitch,bk,yaw)
        # write all keys at once (keyframe_insert per frame is far too slow for 1300 fish x 2160 frames)
        r.animation_data_create(); ac=bpy.data.actions.new('swimpath'); r.animation_data.action=ac
        fr_=np.arange(1,F+1,dtype=float)
        for path,arr in (('location',loc),('rotation_euler',rot)):
            for ax in range(3):
                fc=ac.fcurves.new(path,index=ax); fc.keyframe_points.add(F)
                fc.keyframe_points.foreach_set('co',np.c_[fr_,arr[:,ax]].ravel())
                fc.update()
        swim(a,random.randint(0,190),0)
print('FISH',NT)
# ---------------- water world
CX,CY=23.0,-8.0
ZS=9.0; ZF=-8.0
box=mk('WaterBox',lambda bm: bmesh.ops.create_cube(bm,size=1.0)); box.location=(CX,CY,(ZF-0.5+ZS-0.02)/2); box.scale=(900,900,ZS-0.02-(ZF-0.5))   # big enough that its walls are lost in the haze
vm=bpy.data.materials.new('water'); vm.use_nodes=True; vn=vm.node_tree; vn.nodes.remove(vn.nodes['Principled BSDF'])
vol=vn.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Color'].default_value=(0.04,0.22,0.52,1); vol.inputs['Density'].default_value=0.075
vol.inputs['Anisotropy'].default_value=0.75; vol.inputs['Absorption Color'].default_value=(0.12,0.42,0.82,1)
vn.links.new(vol.outputs[0],vn.nodes['Material Output'].inputs['Volume']); box.data.materials.append(vm)
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.02,0.1,0.26,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.6
sun=bpy.data.lights.new('sun','SUN'); sun.energy=34; sun.color=(0.92,0.98,1.0); sun.angle=math.radians(2)
so=bpy.data.objects.new('sun',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(-30),math.radians(25),math.radians(-20))
# ---- living water: surface ripples and the caustic net / light shafts move, seamless over the 90 s loop.
# A texture evolving in 4D (W = time) is not periodic, so each one is evaluated at t and at t-90 and
# cross-faded by t/90: at t=90 the second copy is exactly the first one at t=0.
LOOP=90.0
def clock(nt):
    v=nt.nodes.new('ShaderNodeValue'); v.label='loop time'
    v.outputs[0].default_value=T0; v.outputs[0].keyframe_insert('default_value',frame=1)
    v.outputs[0].default_value=T0+1000/24.0; v.outputs[0].keyframe_insert('default_value',frame=1001)
    for fc in nt.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation='LINEAR'
        fc.extrapolation='LINEAR'
    t=nt.nodes.new('ShaderNodeMath'); t.operation='WRAP'; nt.links.new(v.outputs[0],t.inputs[0]); t.inputs[1].default_value=LOOP; t.inputs[2].default_value=0.0
    return t.outputs[0]
def looped(nt,make,vec,t,rate,out):
    A=make(); B=make()
    for node,off in ((A,0.0),(B,-LOOP)):
        w=nt.nodes.new('ShaderNodeMath'); w.operation='MULTIPLY_ADD'; nt.links.new(t,w.inputs[0]); w.inputs[1].default_value=rate; w.inputs[2].default_value=off*rate
        nt.links.new(w.outputs[0],node.inputs['W']); nt.links.new(vec,node.inputs['Vector'])
    f=nt.nodes.new('ShaderNodeMath'); f.operation='DIVIDE'; nt.links.new(t,f.inputs[0]); f.inputs[1].default_value=LOOP
    mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='FLOAT'; nt.links.new(f.outputs[0],mx.inputs['Factor'])
    nt.links.new(A.outputs[out],mx.inputs[2]); nt.links.new(B.outputs[out],mx.inputs[3])
    return mx.outputs[0]
surf=mk('Surface',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1000)); surf.location=(CX,CY,ZS)
sm=bpy.data.materials.new('surf'); sm.use_nodes=True; sb=sm.node_tree.nodes['Principled BSDF']; sb.inputs['Transmission Weight'].default_value=1; sb.inputs['Roughness'].default_value=0.05; sb.inputs['IOR'].default_value=1.33
sn=sm.node_tree; st_=clock(sn); sco=sn.nodes.new('ShaderNodeTexCoord')
def wave():
    n=sn.nodes.new('ShaderNodeTexNoise'); n.noise_dimensions='4D'; n.inputs['Scale'].default_value=0.12; n.inputs['Detail'].default_value=3; n.inputs['Distortion'].default_value=0.6; return n   # slow swells (~8 m), not a glittering ceiling
hgt=looped(sn,wave,sco.outputs['Object'],st_,0.35,'Fac')
bmp=sn.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value=0.35; sn.links.new(hgt,bmp.inputs['Height']); sn.links.new(bmp.outputs['Normal'],sb.inputs['Normal'])
surf.data.materials.append(sm); surf.visible_shadow=False
gobo=mk('Gobo',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1000)); gobo.location=(CX,CY,ZS-0.3)
gm=bpy.data.materials.new('gobo'); gm.use_nodes=True; gn=gm.node_tree; gb=gn.nodes['Principled BSDF']
gt=clock(gn); gco=gn.nodes.new('ShaderNodeTexCoord')
def warpn():
    n=gn.nodes.new('ShaderNodeTexNoise'); n.noise_dimensions='4D'; n.inputs['Scale'].default_value=0.6; return n
wx=looped(gn,warpn,gco.outputs['Object'],gt,0.06,'Fac')
wv_=gn.nodes.new('ShaderNodeVectorMath'); wv_.operation='ADD'; gn.links.new(gco.outputs['Object'],wv_.inputs[0]); gn.links.new(wx,wv_.inputs[1])
def cell():
    n=gn.nodes.new('ShaderNodeTexVoronoi'); n.voronoi_dimensions='4D'; n.feature='DISTANCE_TO_EDGE'; n.inputs['Scale'].default_value=1.4; return n
def looped_min(nt,make,vec,t,rate,out,k=0.35):
    A=make(); B=make(); f=nt.nodes.new('ShaderNodeMath'); f.operation='DIVIDE'; nt.links.new(t,f.inputs[0]); f.inputs[1].default_value=LOOP
    res=[]
    for node,off,sign in ((A,0.0,1),(B,-LOOP,-1)):
        w=nt.nodes.new('ShaderNodeMath'); w.operation='MULTIPLY_ADD'; nt.links.new(t,w.inputs[0]); w.inputs[1].default_value=rate; w.inputs[2].default_value=off*rate
        nt.links.new(w.outputs[0],node.inputs['W']); nt.links.new(vec,node.inputs['Vector'])
        b=nt.nodes.new('ShaderNodeMath'); b.operation='MULTIPLY_ADD'; nt.links.new(f.outputs[0],b.inputs[0]); b.inputs[1].default_value=sign*k; b.inputs[2].default_value=0.0 if sign>0 else k
        s=nt.nodes.new('ShaderNodeMath'); s.operation='ADD'; nt.links.new(node.outputs[out],s.inputs[0]); nt.links.new(b.outputs[0],s.inputs[1]); res.append(s.outputs[0])
    m=nt.nodes.new('ShaderNodeMath'); m.operation='MINIMUM'; nt.links.new(res[0],m.inputs[0]); nt.links.new(res[1],m.inputs[1])
    # remove the common bias k*min(f,1-f) so the dominant net keeps its true distances (edges stay at 0)
    g=nt.nodes.new('ShaderNodeMath'); g.operation='SUBTRACT'; g.inputs[0].default_value=1.0; nt.links.new(f.outputs[0],g.inputs[1])
    mn=nt.nodes.new('ShaderNodeMath'); mn.operation='MINIMUM'; nt.links.new(f.outputs[0],mn.inputs[0]); nt.links.new(g.outputs[0],mn.inputs[1])
    c=nt.nodes.new('ShaderNodeMath'); c.operation='MULTIPLY_ADD'; nt.links.new(mn.outputs[0],c.inputs[0]); c.inputs[1].default_value=-k; nt.links.new(m.outputs[0],c.inputs[2])
    return c.outputs[0]
dist=looped_min(gn,cell,wv_.outputs[0],gt,0.22,'Distance')
gr=gn.nodes.new('ShaderNodeValToRGB'); gr.color_ramp.elements[0].position=0.05; gr.color_ramp.elements[0].color=(1,1,1,1); gr.color_ramp.elements[1].position=0.16; gr.color_ramp.elements[1].color=(0.12,0.12,0.12,1)
gn.links.new(dist,gr.inputs[0]); inv=gn.nodes.new('ShaderNodeInvert'); gn.links.new(gr.outputs['Color'],inv.inputs['Color'])
gn.links.new(inv.outputs['Color'],gb.inputs['Alpha']); gb.inputs['Base Color'].default_value=(0,0,0,1); gobo.data.materials.append(gm)
for v in ('visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter'): setattr(gobo,v,False)
sky=mk('Sky',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1000)); sky.location=(CX,CY,ZS+4)
km=bpy.data.materials.new('sky'); km.use_nodes=True; kn=km.node_tree; kn.nodes.remove(kn.nodes['Principled BSDF'])
em=kn.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value=(1.0,1.25,1.5,1); em.inputs["Strength"].default_value=1.0
# Snell's window is far brighter than the water: seen through refraction/reflection (bubble rims, fish flanks,
# looking up through the surface) the sky is 4x the strength it adds as diffuse fill
lp=kn.nodes.new('ShaderNodeLightPath'); gm_=kn.nodes.new('ShaderNodeMath'); gm_.operation='MAXIMUM'
td=kn.nodes.new('ShaderNodeMath'); td.operation='GREATER_THAN'; kn.links.new(lp.outputs['Transmission Depth'],td.inputs[0]); td.inputs[1].default_value=1.5   # through a bubble (2+ refractions), not just the surface
kn.links.new(lp.outputs['Is Glossy Ray'],gm_.inputs[0]); kn.links.new(td.outputs[0],gm_.inputs[1])
sk=kn.nodes.new('ShaderNodeMapRange'); kn.links.new(gm_.outputs[0],sk.inputs[0]); sk.inputs[3].default_value=1.0; sk.inputs[4].default_value=4.0
kn.links.new(sk.outputs[0],em.inputs['Strength'])
kn.links.new(em.outputs[0],kn.nodes['Material Output'].inputs['Surface']); sky.data.materials.append(km); sky.visible_shadow=False
floor=mk('Floor',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1000)); floor.location=(CX,CY,-8)
fm=bpy.data.materials.new('floor'); fm.use_nodes=True; fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.01,0.03,0.06,1); floor.data.materials.append(fm)
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
# aeration plumes (Geometry Nodes, loop-periodic): a couple per screen at different depths + far ones
import bubbles
bmat=bubbles.material(); bng=bubbles.group(bmat); brng=random.Random(21)
for i,s in enumerate(hg.SC):
    for j in range(2 if s['W']>=3 else 1):
        beh=brng.uniform(1.2,7.0); lat=brng.uniform(-0.5,0.5)*(s['W']+beh*0.6)
        p=s['c']-s['n']*beh+s['t']*lat
        bubbles.plume(sc,bng,(p[0],p[1],ZF+0.1),ZS-ZF-0.15,int(brng.uniform(6000,8000)),i*10+j,T0,size_max=0.012,
                      spread_top=brng.uniform(0.6,1.2),sway=brng.uniform(0.15,0.35))
    p=s['c']-s['n']*brng.uniform(0.5,1.2)+s['t']*brng.uniform(-0.35,0.35)*s['W']      # one close column: big wobbling bubbles
    bubbles.plume(sc,bng,(p[0],p[1],ZF+0.1),ZS-ZF-0.15,1600,300+i,T0,spread_top=0.45,sway=0.12,size_max=0.026)
    p=s['c']-s['n']*brng.uniform(0.12,0.35)+s['t']*brng.uniform(-0.3,0.3)*s['W']       # coarse-aeration gulps right behind the glass: big lens bubbles
    bubbles.plume(sc,bng,(p[0],p[1],ZF+0.1),ZS-ZF-0.15,70,700+i,T0,spread_top=0.3,sway=0.08,size_min=0.015,size_max=0.05)
    p=s['c']-s['n']*brng.uniform(16,24)+s['t']*brng.uniform(-4,4)                   # distant column, reads as a silvery curtain
    bubbles.plume(sc,bng,(p[0],p[1],ZF+0.1),ZS-ZF-0.15,6000,500+i,T0,spread_top=1.8,sway=0.4,size_max=0.016)
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
    cd.shift_x=loc.x/big; cd.shift_y=loc.y/big; cd.clip_start=D*0.97; cd.clip_end=3000
    cams.append((s,co))
# ---------------- render settings
sc.frame_start=1; sc.frame_end=F; sc.render.fps=24
sc.render.engine='CYCLES'; sc.cycles.device='CPU'
# GPU if available: set RAS_GPU=OPTIX / CUDA / HIP / METAL / ONEAPI (OPTIX for NVIDIA RTX)
if os.environ.get('RAS_GPU'):
    pr=bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type=os.environ['RAS_GPU']; pr.get_devices()
    for d in pr.devices: d.use=(d.type!='CPU')
    sc.cycles.device='GPU'; print('GPU',[d.name for d in pr.devices if d.use])
sc.cycles.samples=int(os.environ.get('RAS_SAMPLES','24')); sc.cycles.use_denoising=True
sc.cycles.volume_step_rate=10; sc.cycles.max_bounces=8; sc.cycles.diffuse_bounces=1; sc.cycles.glossy_bounces=4; sc.cycles.transmission_bounces=6; sc.cycles.transparent_max_bounces=8; sc.cycles.volume_bounces=0
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Punchy'
sc.render.image_settings.file_format='PNG'
for s,co in cams:
    if ONLY and s['name'] not in ONLY: continue
    sc.camera=co; sc.render.resolution_x=max(2,int(s['res'][0]*SCALE)); sc.render.resolution_y=max(2,int(s['res'][1]*SCALE))
    sc.render.filepath=os.path.join(OUT,s['name'],s['name']+'_') if F>1 else os.path.join(OUT,s['name']+'.png')
    sc.render.use_overwrite=False; sc.render.use_placeholder=True        # re-running resumes where it stopped
    bpy.ops.render.render(write_still=(F==1),animation=(F>1))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'hall.blend'))
print('DONE')
