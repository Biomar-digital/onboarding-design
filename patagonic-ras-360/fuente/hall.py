# Patagonic RAS 360: one shared underwater world around the hall, one "window" camera per LED screen.
# blender -b --factory-startup -P hall.py -- OUTDIR T0 FRAMES SCALE
import bpy, bmesh, sys, math, random, mathutils, os
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import hallgeo as hg; from school import simulate
args=sys.argv[sys.argv.index('--')+1:]
LOOP_S=float(os.environ.get('RAS_LOOP','90'))     # seamless loop length (s): every motion in the scene repeats exactly
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
def salmon_skin(L):
    # keeps the client's texture; adds what real Atlantic salmon show underwater: wet clear-coat sheen,
    # silvery (metallic) flanks that flash when the fish banks, a darker blue-green back and the black
    # spots above the lateral line (the texture has none)
    m=bpy.data.materials['Fish_Shd']; nt=m.node_tree; N=nt.nodes; Lk=nt.links; bs=N['Principled BSDF']
    base=bs.inputs['Base Color'].links[0].from_socket
    tc=N.new('ShaderNodeTexCoord'); sep=N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Normal'],sep.inputs[0])
    def mr(x,a,b,lo=0.0,hi=1.0):
        r=N.new('ShaderNodeMapRange'); Lk.new(x,r.inputs[0]); r.inputs[1].default_value=a; r.inputs[2].default_value=b; r.inputs[3].default_value=lo; r.inputs[4].default_value=hi; return r.outputs[0]
    back=mr(sep.outputs['Z'],0.05,0.55)                     # 0 flank/belly -> 1 dorsal (object-space normal)
    flank=mr(sep.outputs['Z'],-0.75,0.1)                    # 0 belly -> 1 flank and up
    # spots: sparse voronoi cells, ~1 cm dots every ~4 cm, only from the lateral line up
    vo=N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=20.0/L; Lk.new(tc.outputs['Object'],vo.inputs['Vector'])
    dot=mr(vo.outputs['Distance'],0.27,0.38,1.0,0.0)
    keep=N.new('ShaderNodeMath'); keep.operation='GREATER_THAN'; Lk.new(vo.outputs['Color'],keep.inputs[0]); keep.inputs[1].default_value=0.5
    zone=mr(sep.outputs['Z'],-0.05,0.25)
    sp=N.new('ShaderNodeMath'); sp.operation='MULTIPLY'; Lk.new(dot,sp.inputs[0]); Lk.new(keep.outputs[0],sp.inputs[1])
    sp2=N.new('ShaderNodeMath'); sp2.operation='MULTIPLY'; Lk.new(sp.outputs[0],sp2.inputs[0]); Lk.new(zone,sp2.inputs[1])
    # colour: back towards steel blue-green, spots near-black
    dk=N.new('ShaderNodeMix'); dk.data_type='RGBA'; dk.blend_type='MULTIPLY'; Lk.new(back,dk.inputs['Factor']); Lk.new(base,dk.inputs[6]); dk.inputs[7].default_value=(0.11,0.17,0.2,1)
    spc=N.new('ShaderNodeMix'); spc.data_type='RGBA'; Lk.new(sp2.outputs[0],spc.inputs['Factor']); Lk.new(dk.outputs[2],spc.inputs[6]); spc.inputs[7].default_value=(0.02,0.02,0.025,1)
    Lk.new(spc.outputs[2],bs.inputs['Base Color'])
    # silver: metallic on the flanks (not on the back or spots), wet roughness
    met=N.new('ShaderNodeMath'); met.operation='MULTIPLY'; Lk.new(flank,met.inputs[0]); Lk.new(mr(sep.outputs['Z'],0.2,0.7,0.32,0.06),met.inputs[1])
    met2=N.new('ShaderNodeMath'); met2.operation='MULTIPLY'; Lk.new(met.outputs[0],met2.inputs[0]); Lk.new(mr(sp2.outputs[0],0,1,1,0),met2.inputs[1])
    Lk.new(met2.outputs[0],bs.inputs['Metallic'])
    Lk.new(mr(back,0,1,0.22,0.34),bs.inputs['Roughness'])
    bs.inputs['Coat Weight'].default_value=0.6; bs.inputs['Coat Roughness'].default_value=0.05
    if 'Thin Film Thickness' in bs.inputs: bs.inputs['Thin Film Thickness'].default_value=260.0; bs.inputs['Thin Film IOR'].default_value=1.4   # faint iridescence of the scales
if not os.environ.get('RAS_ORIGINAL_SKIN'): salmon_skin(L)
def make_lod(ratio=0.27):
    # simplified body for distant fish: same UVs and skeleton weights, so it still swims; ~1/3 of the points
    tmp=bpy.data.objects.new('lodtmp',body.data.copy()); sc.collection.objects.link(tmp)
    for vg in body.vertex_groups: tmp.vertex_groups.new(name=vg.name)
    md=tmp.modifiers.new('dec','DECIMATE'); md.ratio=ratio
    dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(tmp.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    me.name='body_LOD'; bpy.data.objects.remove(tmp); return me
LOD_MESH=make_lod(); LOD_FROM=float(os.environ.get('RAS_LOD_FROM','7'))
def matte_far_skin():
    # distant fish are a few pixels long: any sharp sun highlight on them reads as a blinking white speck.
    # Their simplified body gets a matte copy of the skin (no wet coat, no metal), as seen through that much water
    m=bpy.data.materials['Fish_Shd'].copy(); m.name='Fish_far'; b=m.node_tree.nodes['Principled BSDF']
    for k,v in (('Coat Weight',0.0),('Specular IOR Level',0.25)): b.inputs[k].default_value=v
    for k in ('Metallic',):
        for l in list(b.inputs[k].links): m.node_tree.links.remove(l)
        b.inputs[k].default_value=0.0
    for l in list(b.inputs['Roughness'].links): m.node_tree.links.remove(l)
    b.inputs['Roughness'].default_value=0.6
    for i in range(len(LOD_MESH.materials)): LOD_MESH.materials[i]=m
matte_far_skin()
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
def swim(a,phase,v,rate=1.0):
    a.animation_data_create(); tr=a.animation_data.nla_tracks.new(); st=tr.strips.new('swim',int(fr[0]),act)
    Fl=LOOP_S*24; cyc=(fr[1]-fr[0]); n_=max(1,round(Fl/(cyc*0.9/max(0.55,min(1.6,rate))))); st.scale=Fl/(cyc*n_); st.repeat=max(30,int((F+400)/max(1,fr[1]-fr[0])/st.scale)+2)                    # close to the authored speed: calm, not violent
    st.frame_start=fr[0]-phase
    st.use_animated_influence=True; st.influence=float(os.environ.get('RAS_TAIL','0.85')); st.keyframe_insert('influence',frame=1)   # tail-beat amplitude (1 = as authored)
arm.animation_data.action=None
# ---------------- depth layers: schools at different distances behind the screens + loners
# each layer has its own circuit (parallel to the screens, `behind` metres back) and does 1 lap in 90 s
def lead_fn(C,S_,LEN,phase_s,sgn=1,bob=0.25,laps=1):
    V=laps*LEN/LOOP_S; wb=2*math.pi*max(1,round(0.4*LOOP_S/(2*math.pi)))/LOOP_S
    def lead(t):
        s=(sgn*V*(t+T0+phase_s))%LEN; i=np.searchsorted(S_,s,side='right')-1; i=max(0,min(i,len(C)-1))
        a=C[i]; b=C[(i+1)%len(C)]; u=(s-S_[i])/max(S_[i+1]-S_[i],1e-6); p=a+(b-a)*u
        d=b-a; d=sgn*d/np.linalg.norm(d)*V
        p=p.copy(); p[2]+=bob*math.sin(wb*(t+T0)+phase_s)
        return p,d
    return lead
# (name, behind m, height offset m, direction, [(fish, phase s), ...], spread)
LAYERS=[
 ('cerca',  2.2,  -0.2,  1, [(12, 0.9),(10, 31.6),(10, 61.8)],                0.7),
 ('medio',  3.5,   0.0,  1, [(55, 7.7),(45, 33.3),(50, 54.2),(40, 76.9)],     1.3),
 ('lejos',  7.5,   0.7, -1, [(70, 17.9),(60, 42.9),(60, 63.6),(55, 84.6)],    1.6),   # swims the other way
 ('fondo', 15.0,  -0.4,  1, [(140, 2.2),(120, 30.0),(120, 59.4)],             2.4),   # big schools fading into the haze
 ('pared', 26.0,   0.6, -1, [(220, 25.1),(200, 66.1)],                        3.2),   # far wall of fish: RAS density
]
random.seed(11); rng=np.random.default_rng(3)
plan=[]
for name,beh,dz,sgn,schools,spr in LAYERS:
    C,S_,LEN=hg.circuit(behind=beh,dz=dz)
    for ns,ph in schools: plan.append((C,S_,LEN,ph,sgn,ns,spr,0.25,beh>=float(os.environ.get('RAS_STATIC_FROM','999')),1,beh>=LOD_FROM))
for k in range(12):                                   # loners: single salmon at random depths and heights
    C,S_,LEN=hg.circuit(behind=float(rng.uniform(1.8,9.0)),dz=float(rng.uniform(-1.0,1.2)))
    plan.append((C,S_,LEN,float(rng.uniform(0,90)),1 if k%3 else -1,1,1.0,0.6,False,1,False))
for k in range(6):                                  # close passes: big salmon gliding ~1.1-1.5 m behind the glass
    C,S_,LEN=hg.circuit(behind=float(rng.uniform(1.1,1.5)),dz=float(rng.uniform(-0.4,0.5)),clear=1.05,pad=0.5)
    plan.append((C,S_,LEN,float(rng.uniform(0,90)),1 if k%2 else -1,1,1.0,0.3,False,1,False))
# rotunda: fish milling behind the two round-room totems on their own short loops (laps chosen for ~0.6 m/s)
for beh,dz,ns,ph,sgn,spr in ((2.6,0.0,14,0.0,1,0.6),(4.5,0.4,18,40.0,-1,0.8),(3.4,-0.3,1,20.0,1,1.0)):
    C,S_,LEN=hg.local_loop(['totem_R1','totem_R2'],beh,dz)
    plan.append((C,S_,LEN,ph,sgn,ns,spr,0.2,False,max(1,round(0.6*LOOP_S/LEN)),False))
# kitchen screen: not part of the hall circuit (standalone loop, same look) - schools crossing it back and forth
for beh,dz,ns,ph,sgn,spr in ((2.4,-0.1,16,5.0,1,0.7),(4.2,0.3,30,35.0,-1,1.0),(7.0,0.5,45,62.0,1,1.4),(3.0,-0.4,1,15.0,-1,1.0)):
    C,S_,LEN=hg.local_loop(['cocina'],beh,dz,pad=3.0)
    plan.append((C,S_,LEN,ph,sgn,ns,spr,0.2,False,max(1,round(0.6*LOOP_S/LEN)),beh>=LOD_FROM))
if os.environ.get('FEWFISH'): plan=plan[:2]          # quick look-dev of the environment
def keep_behind_glass(P,margin=0.9,iters=16):
    # Each screen is a window whose near clip plane is the glass: a fish inside a screen's visible pyramid
    # (eye -> screen rectangle) closer than `margin` behind the glass would be sliced or float in the room.
    # Move it out by the shortest way (further back, or out of a side of the pyramid), with the correction
    # spread over time (dilate by magnitude, then gaussian) so it reads as a natural swerve, never a jump.
    F_,N_,_=P.shape; out=P.copy(); win=72; G=np.exp(-0.5*(np.arange(-30,31)/12.0)**2); G/=G.sum()
    for it in range(iters):
        tot=np.zeros_like(out)
        for s in hg.SC:
            c,n,t=s['c'],s['n'],s['t']; e=s['eye']; D=s['D']; up=np.array([0,0,1.0])
            rel=out-e; along=rel@(-n); d=along-D
            ok=along>0.05
            cx=(c-e)@t; cz=c[2]-e[2]
            ox=rel@t-cx*along/D; oz=rel[...,2]-cz*along/D                 # offset from the screen's centre line
            hx=(s['W']/2+0.6)*along/D; hz=(s['H']/2+0.6)*along/D          # pyramid half-size at that depth (+0.6 m body)
            inside=ok&(np.abs(ox)<hx)&(np.abs(oz)<hz)&(d<margin)
            if not inside.any(): continue
            back=np.clip(margin-d,0,None)
            side=hx-np.abs(ox); vert=hz-np.abs(oz)
            # pick the cheapest exit (vertical exits only a little favoured: fish should stay mostly level)
            cost=np.stack([back,side*1e6,vert*1.6],-1); k=cost.argmin(-1)   # no sideways exits: their side flips mid-crossing and cancels out
            vec=np.where((k==0)[...,None],back[...,None]*(-n),
                np.where((k==1)[...,None],(side+0.05)[...,None]*np.sign(ox)[...,None]*t,(vert+0.05)[...,None]*np.sign(oz)[...,None]*up))
            vec=np.where(inside[...,None],vec,0.0); tot+=vec
        if not np.abs(tot).any(): break
        mag=np.linalg.norm(tot,axis=-1)
        pad=np.pad(mag,((win//2,win//2),(0,0)),mode='wrap'); idx=np.lib.stride_tricks.sliding_window_view(pad,win,axis=0).argmax(-1)[:F_]
        rows=(np.arange(F_)[:,None]-win//2+idx)%F_
        dil=tot[rows,np.arange(N_)[None,:]]                                   # vector of the strongest need nearby in time
        sm=np.stack([np.stack([np.convolve(np.pad(dil[:,j,a],30,mode='wrap'),G,mode='valid') for a in range(3)],-1) for j in range(N_)],1)
        out=out+sm
    return out
def sliced_fish(P,margin=0.45):
    # fish that would still touch a glass after the correction (indices): they are left out of the school
    bad=np.zeros(P.shape[1],bool)
    for s in hg.SC:
        c,n,t=s['c'],s['n'],s['t']; e=s['eye']; D=s['D']; rel=P-e; along=rel@(-n); d=along-D
        ox=rel@t-((c-e)@t)*along/D; oz=rel[...,2]-(c[2]-e[2])*along/D
        m=(along>0.05)&(np.abs(ox)<(s['W']/2+0.4)*along/D)&(np.abs(oz)<(s['H']/2+0.4)*along/D)&(d<margin)
        bad|=m.any(0)
    return np.where(bad)[0]
print('PREP armando la escena: copiando salmones...',flush=True)
NT=sum(p[5] for p in plan); fish=[(root,arm)]
for i in range(NT-1): fish.append(dup_fish())
k=0
for q,(C,S_,LEN,ph,sgn,ns,spr,bob,far,laps,lod) in enumerate(plan):
    print('PREP simulando cardumen',q+1,'de',len(plan),'(',ns,'peces )',flush=True)
    P,Vt=simulate(lead_fn(C,S_,LEN,ph,sgn,bob,laps),F,ns,seed=5+q,spread=spr,loop=LOOP_S,darts=(2.5 if ns==1 else 1.2) if not far else 0.0)
    P=keep_behind_glass(P); drop=set(sliced_fish(P).tolist())
    if drop: print('DROPPED',len(drop),'fish of plan',q)
    for j in range(ns):
        r,a=fish[k]; k+=1
        if j in drop:
            for o in [r]+list(r.children_recursive): o.hide_render=True; o.hide_viewport=True
            continue
        r.scale=(0.7/L*random.uniform(0.78,1.22)*(1.15 if ns==1 else 1.0)*(1.45 if random.random()<0.04 else 1.0),)*3   # a few big broodstock
        if lod:                                       # distant fish: simplified body, no eyes (sub-pixel there)
            for o in r.children_recursive:
                if o.type=='MESH':
                    if len(o.data.vertices)==len(body.data.vertices): o.data=LOD_MESH
                    else: o.hide_render=True
        yw=None; bk=0.0; loc=np.zeros((F,3)); rot=np.zeros((F,3))
        for f in list(range(F))[-48:]:                 # prime the bank filter with the end of the loop
            v=Vt[f,j]; yaw=math.atan2(v[0],-v[1])
            if yw is not None: dy=(yaw-yw+math.pi)%(2*math.pi)-math.pi; bk=0.85*bk+0.15*max(-0.35,min(0.35,-dy*24*0.3))
            yw=yaw
        yw=None
        for f in range(F):
            v=Vt[f,j]; yaw=math.atan2(v[0],-v[1]); h=math.hypot(v[0],v[1]); pitch=max(-0.21,min(0.21,-math.atan2(v[2],h)))
            if yw is not None:
                dy=(yaw-yw+math.pi)%(2*math.pi)-math.pi; yaw=yw+dy; bk=0.85*bk+0.15*max(-0.5,min(0.5,-dy*24*0.45))
            yw=yaw; loc[f]=P[f,j]; rot[f]=(pitch,bk,yaw)
        # write all keys at once (keyframe_insert per frame is far too slow for 1300 fish x 2160 frames)
        r.animation_data_create(); ac=bpy.data.actions.new('swimpath'); r.animation_data.action=ac
        fr_=np.arange(1,F+1,dtype=float)
        for path,arr in (('location',loc),('rotation_euler',rot)):
            for ax in range(3):
                fc=ac.fcurves.new(path,index=ax); fc.keyframe_points.add(F)
                fc.keyframe_points.foreach_set('co',np.c_[fr_,arr[:,ax]].ravel())
                fc.update()
        if far:
            # 15-26 m away the tail beat is invisible: drop the skinning so all far fish share one static mesh
            # (Cycles instances them instead of rebuilding ~700 deformed meshes every frame)
            for o in r.children_recursive:
                if o.type=='MESH':
                    for md in [m for m in o.modifiers if m.type=='ARMATURE']: o.modifiers.remove(md)
        else:
            swim(a,random.randint(0,190),0,rate=float(np.linalg.norm(Vt[:,j],axis=-1).mean())/1.55)
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
LOOP=LOOP_S
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
    for v in bm.verts: v.co.z*=0.7
dm=bpy.data.materials.new('snow'); dm.use_nodes=True; dn=dm.node_tree; dn.nodes.remove(dn.nodes['Principled BSDF'])
trn=dn.nodes.new('ShaderNodeBsdfTransparent'); dsc=dn.nodes.new('ShaderNodeBsdfDiffuse'); dsc.inputs['Color'].default_value=(0.42,0.46,0.42,1)
dmx=dn.nodes.new('ShaderNodeMixShader'); dmx.inputs['Fac'].default_value=0.45; dn.links.new(trn.outputs[0],dmx.inputs[1]); dn.links.new(dsc.outputs[0],dmx.inputs[2])
dn.links.new(dmx.outputs[0],dn.nodes['Material Output'].inputs['Surface'])
fcoll=bpy.data.collections.new('Flakes'); sc.collection.children.link(fcoll)        # not hidden: hiding would hide the instances too
for q in range(16):
    f_=mk(f'Flake{q}',flake); f_.data.materials.append(dm); sc.collection.objects.unlink(f_); fcoll.objects.link(f_); f_.location=(0,-500,0); f_.visible_shadow=False
# tank current: RAS tanks circulate; salmon hold against it, so it runs opposite to the schools' travel
CUR=0.07
import bubbles; bubbles.LOOP=LOOP_S
by_={s['name']:s for s in hg.SC}; cs_=[by_[k]['c'] for k in hg.ORDER]
def travel(s):
    if s['name'] not in hg.ORDER: return s['t']                        # rotunda totems: local loops, either way
    i=hg.ORDER.index(s['name']); nx=np.array([*hg.VIA[s['name']][0],0.0]) if s['name'] in hg.VIA else cs_[(i+1)%len(cs_)]; d=nx-cs_[i-1]; d[2]=0; return s['t'] if np.dot(s['t'],d)>=0 else -s['t']
far_plumes=[]; bmat=bubbles.material(); bng=bubbles.group(bmat); sng=bubbles.snow_group(fcoll); brng=random.Random(21)
for i,s in enumerate(hg.SC):
    cur=-travel(s)*CUR; up=(s['c'][2]-ZF)/((ZS-ZF-0.15)/LOOP_S)          # seconds a bubble needs to reach screen height
    def base(p): q=p-cur*up; return (q[0],q[1],ZF+0.1)                 # start upstream so the leaning column crosses the screen
    beh=brng.uniform(0.35,1.0); p=s['c']-s['n']*beh+s['t']*brng.uniform(-0.35,0.35)*s['W']     # bubbles only read when close to the lens
    bubbles.plume(sc,bng,base(p),ZS-ZF-0.15,int(brng.uniform(500,800)),i*10,T0,spread_top=brng.uniform(0.3,0.55),sway=brng.uniform(0.1,0.2),size_min=0.0015,size_max=0.004,current=cur)
    if i%2==0:                                                          # a closer column with some coarse (5-7 mm) bubbles
        p=s['c']-s['n']*brng.uniform(1.5,3.0)+s['t']*brng.uniform(-0.35,0.35)*s['W']
        bubbles.plume(sc,bng,base(p),ZS-ZF-0.15,900,300+i,T0,spread_top=0.5,sway=0.2,size_min=0.0015,size_max=0.0035,current=cur)
    if i%3==0:                                                          # a distant curtain
        p=s['c']-s['n']*brng.uniform(14,22)+s['t']*brng.uniform(-4,4)
        far_plumes.append(bubbles.plume(sc,bng,base(p),ZS-ZF-0.15,2500,500+i,T0,spread_top=1.4,sway=0.4,current=cur))
    # marine snow drifting with the current through this screen's view
    dirc=cur/np.linalg.norm(cur); L=CUR*LOOP_S/1; ctr=s['c']-s['n']*0.2
    snow_ob=bubbles.snow(sc,sng,(ctr[0],ctr[1],s['c'][2]),math.atan2(dirc[1],dirc[0]),int(900*max(1,s['W']/2)),900+i,T0,L,1,9.0,s['H']+6)
    # local y must point away from the public (into the water): flip if needed
    yl=np.array([-dirc[1],dirc[0],0.0])
    if np.dot(yl,-s['n'])<0: snow_ob.scale=(1,-1,1)
    if os.environ.get('RAS_NOSNOW'): snow_ob.hide_render=True
if os.environ.get('RAS_NOBUB'):
    for o in sc.objects:
        if o.name.startswith('BubblePlume'): o.hide_render=True
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
    # AUTO tries every backend (NVIDIA RTX: OPTIX, older NVIDIA: CUDA, AMD: HIP, Intel Arc: ONEAPI, Mac: METAL)
    pr=bpy.context.preferences.addons['cycles'].preferences; want=os.environ['RAS_GPU'].upper()
    for typ in (['OPTIX','CUDA','HIP','ONEAPI','METAL'] if want=='AUTO' else [want]):
        try: pr.compute_device_type=typ
        except Exception: continue
        pr.get_devices(); gpus=[d for d in pr.devices if d.type==typ]
        if gpus:
            for d in pr.devices: d.use=(d.type==typ)
            sc.cycles.device='GPU'; print('GPU',typ,[d.name for d in gpus],flush=True); break
    else: print('GPU no encontrada: se usa el procesador (CPU)',flush=True)
sc.cycles.samples=int(os.environ.get('RAS_SAMPLES','24')); sc.cycles.use_denoising=True
sc.cycles.volume_step_rate=10; sc.cycles.max_bounces=8; sc.cycles.diffuse_bounces=1; sc.cycles.glossy_bounces=4; sc.cycles.transmission_bounces=6; sc.cycles.transparent_max_bounces=8; sc.cycles.volume_bounces=0
sc.render.use_motion_blur=not os.environ.get('RAS_NO_MBLUR'); sc.render.motion_blur_shutter=0.5
try:
  sc.use_nodes=True; ct=sc.node_tree; ct.nodes.clear()
  rl=ct.nodes.new('CompositorNodeRLayers'); co_=ct.nodes.new('CompositorNodeComposite')
  ld=ct.nodes.new('CompositorNodeLensdist'); ld.inputs['Dispersion'].default_value=0.012; ld.use_fit=True
  gl=ct.nodes.new('CompositorNodeGlare'); gl.name='GRADE_IN'; gl.glare_type='FOG_GLOW'; gl.quality='MEDIUM'; gl.threshold=0.95; gl.mix=-1.0; gl.size=8   # mix -1 = glow off (it softened the whole image)
  cb=ct.nodes.new('CompositorNodeColorBalance'); cb.correction_method='LIFT_GAMMA_GAIN'
  cb.lift=(1.0,1.01,1.0); cb.gamma=(0.98,1.01,1.0); cb.gain=(0.96,1.02,1.01)       # a touch of RAS green-teal
  bc=ct.nodes.new('CompositorNodeBrightContrast'); bc.inputs['Contrast'].default_value=7.0
  ct.links.new(rl.outputs['Image'],gl.inputs['Image']); ct.links.new(gl.outputs['Image'],cb.inputs['Image'])
  ct.links.new(cb.outputs['Image'],bc.inputs['Image']); ct.links.new(bc.outputs['Image'],ld.inputs['Image']); ct.links.new(ld.outputs['Image'],co_.inputs['Image'])   # vignette + grain in post (ffmpeg)
except Exception as e: print('compositor skipped:',e)
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Punchy'
sc.render.image_settings.file_format='PNG'
if os.environ.get('RAS_PROFILE'):
    import time as _t
    for f in (100,101,102,103):
        t0=_t.time(); sc.frame_set(f); dg=bpy.context.evaluated_depsgraph_get(); t1=_t.time()
        # what motion blur adds: two more scene evaluations per frame (shutter open/close)
        sc.frame_set(f,subframe=0.25); sc.frame_set(f,subframe=0.75); t2=_t.time()
        print('PROFILE frame',f,'scene update s',round(t1-t0,2),'| +motion blur steps s',round(t2-t1,2),flush=True)
    sys.exit(0)
if os.environ.get('RAS_LOOPCHECK'):
    # seam check: the jump from the last frame to the first must look like any other frame-to-frame step
    Fl=int(LOOP_S*24); roots=[r for r,a in fish if not r.hide_render]; arms=[a for r,a in fish if not r.hide_render]
    def snap(f):
        sc.frame_set(f); P=np.array([r.matrix_world.translation[:] for r in roots])
        B=np.array([[q for b in a.pose.bones[:6] for q in b.matrix.to_quaternion()] for a in arms[:200]]); return P,B
    P1,B1=snap(1); P2,B2=snap(2); Pl,Bl=snap(Fl); Pn,Bn=snap(Fl+1)
    print('LOOPCHECK fish step  normal',round(float(np.median(np.linalg.norm(P2-P1,axis=1))),3),'seam',round(float(np.median(np.linalg.norm(P1-Pl,axis=1))),3),'max seam',round(float(np.linalg.norm(P1-Pl,axis=1).max()),3),flush=True)
    print('LOOPCHECK tail pose  frame Fl+1 vs 1 (0 = identical):',round(float(np.abs(Bn-B1).max()),4),'| normal frame change',round(float(np.abs(B2-B1).max()),4),flush=True)
    sys.exit(0)
def _set(obj,attr,val):
    # setting names move between Blender versions: never let one missing option stop the render
    try:
        if hasattr(obj,attr): setattr(obj,attr,val)
    except Exception as e: print('skip',attr,e)
if os.environ.get('RAS_ENGINE','').upper()=='EEVEE':
    # EEVEE (real-time engine, GPU): seconds per frame instead of minutes. Same scene, adapted where EEVEE works
    # differently from Cycles.
    for eng in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
        try: sc.render.engine=eng; break
        except Exception: pass
    ee=sc.eevee; print('ENGINE',sc.render.engine,flush=True)
    _set(ee,'taa_render_samples',int(os.environ.get('RAS_SAMPLES','64')))
    _set(ee,'use_raytracing',True); _set(ee,'ray_tracing_method','SCREEN')
    _set(ee,'use_shadows',True); _set(ee,'shadow_ray_count',1); _set(ee,'shadow_step_count',4); _set(ee,'shadow_resolution_scale',0.5)
    # water: EEVEE fills the view with a world volume (froxels) - that is where it does haze and sun shafts well
    _set(ee,'volumetric_start',0.5); _set(ee,'volumetric_end',70.0); _set(ee,'volumetric_tile_size','8')
    _set(ee,'volumetric_samples',48); _set(ee,'volumetric_sample_distribution',0.85); _set(ee,'use_volumetric_shadows',True)
    _set(ee,'volumetric_ray_depth',8); _set(ee,'volumetric_light_clamp',0.0)
    # water stays a mesh volume (a world volume in EEVEE is infinite and absorbs all sun and sky light)
    _set(sun,'shadow_softness_factor',0.2); _set(sun,'volume_factor',1.0)
    # the gobo casts the caustic/shaft pattern: its alpha must count in shadows
    # v2: the alpha 'gobo' blocks the sun in EEVEE and the glass surface refracts into nothing (black):
    # drop both; EEVEE does not light the scene from an emissive plane, so the sky light comes from the world
    surf.hide_render=True; sky.hide_render=True; floor.hide_render=True   # EEVEE ignores 'no shadow' on these planes: they block the sun
    if os.environ.get('RAS_EEVEE_NOGOBO'): gobo.hide_render=True
    else:
        _set(gm,'use_transparent_shadow',True); _set(gm,'surface_render_method','DITHERED')   # caustic net -> light shafts
        # EEVEE caches shadows of objects that do not move; the gobo only changes its pattern, so nudge it by a
        # sub-millimetre every frame to force the shadow (and the shafts) to be recomputed
        for f_ in range(1,int(LOOP_S*24)+2):
            gobo.location.z=ZS-0.3+(0.0002 if f_%2 else 0.0); gobo.keyframe_insert('location',index=2,frame=f_)
    # the wet clear-coat is too sharp for EEVEE's sun highlight (reads as white dots): soften it
    try:
        mt=bpy.data.materials['Fish_Shd'].node_tree; fb=mt.nodes['Principled BSDF']
        fb.inputs['Coat Roughness'].default_value=0.4; fb.inputs['Coat Weight'].default_value=0.15
        fb.inputs['Specular IOR Level'].default_value=0.3
        # a broad, soft highlight instead of the same hot spot on every fish's belly
        for l in list(fb.inputs['Roughness'].links): mt.links.remove(l)
        fb.inputs['Roughness'].default_value=0.5
        ml=fb.inputs['Metallic'].links
        if ml:
            mm=mt.nodes.new('ShaderNodeMath'); mm.operation='MULTIPLY'; mm.inputs[1].default_value=0.45
            src=ml[0].from_socket; mt.links.remove(ml[0]); mt.links.new(src,mm.inputs[0]); mt.links.new(mm.outputs[0],fb.inputs['Metallic'])
    except Exception as e: print('skip coat',e)
    sun.angle=math.radians(9)                                # softer sun: no pin-point highlights in EEVEE
    wn=sc.world.node_tree; bg=wn.nodes['Background']; bg.inputs[1].default_value=1.0
    tco=wn.nodes.new('ShaderNodeTexCoord'); sz=wn.nodes.new('ShaderNodeSeparateXYZ'); wn.links.new(tco.outputs['Generated'],sz.inputs[0])
    ramp=wn.nodes.new('ShaderNodeValToRGB'); wn.links.new(sz.outputs['Z'],ramp.inputs[0]); E=ramp.color_ramp.elements
    E[0].position=0.25; E[0].color=(0.01,0.05,0.10,1); E[1].position=0.9; E[1].color=(0.45,0.7,0.9,1)
    mid=E.new(0.55); mid.color=(0.10,0.30,0.55,1)
    wn.links.new(ramp.outputs['Color'],bg.inputs['Color'])
    _set(sm,'use_raytrace_refraction',True); _set(sm,'surface_render_method','DITHERED'); _set(sm,'thickness_mode','SPHERE')
    # bubbles: EEVEE's glass on mm-sized spheres collapses to one pure-white pixel that flickers (the white grain).
    # Fake the optics instead: clear centre, soft silver rim from a facing falloff, never brighter than the water above
    bt=bmat.node_tree; bt.nodes.clear(); bo=bt.nodes.new('ShaderNodeOutputMaterial')
    tr=bt.nodes.new('ShaderNodeBsdfTransparent'); gl=bt.nodes.new('ShaderNodeEmission'); gl.inputs['Strength'].default_value=1.0     # rim glow, NOT a sun reflection (that is the white pixel)
    gl.inputs['Color'].default_value=(0.32,0.5,0.62,1); lw=bt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.35
    mr=bt.nodes.new('ShaderNodeMath'); mr.operation='MULTIPLY'; mr.inputs[1].default_value=0.45; bt.links.new(lw.outputs['Facing'],mr.inputs[0])
    bx=bt.nodes.new('ShaderNodeMixShader'); bt.links.new(mr.outputs[0],bx.inputs[0]); bt.links.new(tr.outputs[0],bx.inputs[1]); bt.links.new(gl.outputs[0],bx.inputs[2])
    bt.links.new(bx.outputs[0],bo.inputs['Surface']); _set(bmat,'surface_render_method','BLENDED')
    for o in far_plumes: o.hide_render=True                # 15-20 m away mm bubbles are sub-pixel: only aliasing sparkle, no image
    _set(dm,'surface_render_method','BLENDED')             # marine snow (transparent/translucent)
    vb=False
    if not os.environ.get('RAS_EEVEE_RENDER_MBLUR'):
        try:
            vl=sc.view_layers[0]; vl.use_pass_vector=True; vl.use_pass_z=True
            ct=sc.node_tree; rl_=[n for n in ct.nodes if n.bl_idname=='CompositorNodeRLayers'][0]
            ld_=[n for n in ct.nodes if n.bl_idname=='CompositorNodeLensdist'][0]
            vbn=ct.nodes.new('CompositorNodeVecBlur'); vbn.samples=16; vbn.factor=0.3; vbn.speed_max=16
            ct.links.new(rl_.outputs['Image'],vbn.inputs['Image']); ct.links.new(rl_.outputs['Depth'],vbn.inputs[1])
            ct.links.new(rl_.outputs['Vector'],vbn.inputs['Speed']); ct.links.new(vbn.outputs['Image'],ct.nodes['GRADE_IN'].inputs['Image'])
            sc.render.use_motion_blur=False; vb=True; print('MBLUR vector pass',flush=True)
        except Exception as e: print('vector blur unavailable, render motion blur:',e,flush=True)
    if not vb: _set(sc.render,'use_motion_blur',True); _set(sc.render,'motion_blur_shutter',0.5); _set(ee,'motion_blur_steps',1)
    _set(sc.render,'use_persistent_data',False)
FR=os.environ.get('RAS_FRAMES'); FA,FB=(int(FR.split('-')[0]),int(FR.split('-')[1])) if FR else (1,F)
ext='.png'
if os.environ.get('RAS_JPG'): sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=93; ext='.jpg'
if F>1 and os.environ.get('RAS_FRAMEMAJOR'):
    # frame by frame across all screens, keeping the synced scene (BVH) between cameras: much less overhead
    sc.render.use_persistent_data=True
    for f in range(FA,FB+1):
        todo=[(s,co) for s,co in cams if not (ONLY and s['name'] not in ONLY)
              and not os.path.exists(os.path.join(OUT,s['name'],f"{s['name']}_{f:04d}{ext}"))]
        if not todo: continue
        sc.frame_set(f)
        for s,co in todo:
            sc.camera=co; sc.render.resolution_x=max(2,int(s['res'][0]*SCALE)); sc.render.resolution_y=max(2,int(s['res'][1]*SCALE))
            os.makedirs(os.path.join(OUT,s['name']),exist_ok=True)
            sc.render.filepath=os.path.join(OUT,s['name'],f"{s['name']}_{f:04d}{ext}")
            bpy.ops.render.render(write_still=True)
        print('FRAME_DONE',f,flush=True)
    print('DONE'); sys.exit(0)
for s,co in cams:
    if ONLY and s['name'] not in ONLY: continue
    sc.frame_start=FA; sc.frame_end=FB
    sc.camera=co; sc.render.resolution_x=max(2,int(s['res'][0]*SCALE)); sc.render.resolution_y=max(2,int(s['res'][1]*SCALE))
    sc.render.filepath=os.path.join(OUT,s['name'],s['name']+'_') if F>1 else os.path.join(OUT,s['name']+'.png')
    sc.render.use_overwrite=False; sc.render.use_placeholder=True        # re-running resumes where it stopped
    bpy.ops.render.render(write_still=(F==1),animation=(F>1))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'hall.blend'))
print('DONE')
