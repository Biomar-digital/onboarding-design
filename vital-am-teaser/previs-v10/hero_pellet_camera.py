# Higgsfield 3D Jutsu edit (rev 28 -> 29): one continuous, smoothed camera that follows ONE hero pellet
# from the scoop, through the air, into the water, and down to the shrimp that catches it mid-water (pellet UW_076).
import bpy, math
from mathutils import Vector
D=bpy.data; sc=bpy.context.scene
def allfc(o):
    ad=o.animation_data; r=[]
    if not ad or not ad.action: return r
    for L in ad.action.layers:
        for s in L.strips:
            for cb in s.channelbags: r+=list(cb.fcurves)
    return r
def findfc(o,path,idx):
    for fc in allfc(o):
        if fc.data_path==path and fc.array_index==idx: return fc
def ev(o,path,idx,f):
    fc=findfc(o,path,idx); return fc.evaluate(f) if fc else getattr(o,path.split('.')[-1])[idx]
def setkeys(o,path,idx,keys,interp='LINEAR'):
    fc=findfc(o,path,idx)
    if fc is None:
        try: o.keyframe_insert(path,index=idx,frame=keys[0][0])
        except TypeError: o.keyframe_insert(path,frame=keys[0][0])
        fc=findfc(o,path,idx)
    fc.keyframe_points.clear(); fc.keyframe_points.add(len(keys))
    for kp,(f,v,*ip) in zip(fc.keyframe_points,keys):
        kp.co=(f,v); kp.interpolation=ip[0] if ip else interp; kp.handle_left_type=kp.handle_right_type='AUTO_CLAMPED'
    fc.update()
def sm(a,b,x):
    t=min(1,max(0,(x-a)/(b-a))); return t*t*(3-2*t)
def wrap(a):
    while a>math.pi: a-=2*math.pi
    while a<-math.pi: a+=2*math.pi
    return a
def look(p,t):
    d=(t-p).normalized(); return math.acos(max(-1,min(1,-d.z))), math.atan2(-d.x,d.y)
def dirof(rx,rz): return Vector((-math.sin(rz)*math.sin(rx), math.cos(rz)*math.sin(rx), -math.cos(rx)))
cam=D.objects['CAM_S3_Drone']; s4=D.objects['CAM_S4_Follow_Feed']; pel=D.objects['FEED_Pellet_UW_076']
FA,FS4=112,262                      # drone curve rebuilt from FA; hands over to CAM_S4 at FS4
# ---------- 1. hero pellet in the air: a T1 pellet that lands close to where UW_076 is eaten ----------
air=[o for o in D.objects if o.name.startswith('FEED_Air_T1_')]
TR={o.name:{} for o in air}
for f in range(156,198):
    sc.frame_set(f)
    for o in air:
        if o.matrix_world.to_scale()[0]>1e-3: TR[o.name][f]=o.matrix_world.translation.copy()
END=Vector((ev(pel,'location',0,276),ev(pel,'location',1,276)))
best=None
for n,t in TR.items():
    if len(t)<15: continue
    fl=max(t); land=t[fl]
    if not (183<=fl<=192): continue
    d=(land.xy-END).length
    if best is None or d<best[0]: best=(d,n,fl)
_,HN,FL=best; A=TR[HN]; F0=min(A)
LAND=A[FL].copy(); LAND.z=0.0
# ---------- 2. UW_076 becomes the same pellet: enters where the hero pellet lands, sinks to the shrimp ----------
P_END=Vector((ev(pel,'location',0,276),ev(pel,'location',1,276),ev(pel,'location',2,276)))
ks={0:[],1:[],2:[]}
for f in range(FL,277):
    t=(f-FL)/(276-FL); e=1-(1-t)**1.6                         # sinks, slowing slightly as it nears the shrimp
    p=LAND.lerp(P_END,t); p.z=LAND.z+(P_END.z-LAND.z)*e
    for i in range(3): ks[i].append((f,p[i]))
for i in range(3):
    old=[(kp.co[0],kp.co[1]) for kp in findfc(pel,'location',i).keyframe_points if kp.co[0]>276]
    setkeys(pel,'location',i,ks[i]+old)
for i in range(3): setkeys(pel,'scale',i,[(1,0.0,'CONSTANT'),(FL,1.3,'CONSTANT'),(282,1.3,'LINEAR'),(306,0.26,'CONSTANT'),(307,0.0,'CONSTANT')],'CONSTANT')
hf=findfc(pel,'hide_render',0)
if hf: setkeys(pel,'hide_render',0,[(1,1.0,'CONSTANT'),(FL,0.0,'CONSTANT'),(307,1.0,'CONSTANT')],'CONSTANT')
def PP(f):                                                    # hero pellet position for any frame
    if f<=FL: return A[max(F0,min(FL,f))].copy()
    return Vector([ev(pel,'location',i,f) for i in range(3)])
# ---------- 3. camera ----------
def orig(f):
    p=Vector([ev(cam,'location',i,f) for i in range(3)]); return p, p+dirof(ev(cam,'rotation_euler',0,f),ev(cam,'rotation_euler',2,f))*6.0
def s4st(f):
    p=Vector([ev(s4,'location',i,f) for i in range(3)]); rx=ev(s4,'rotation_euler',0,f); rz=ev(s4,'rotation_euler',2,f); return p,rx,rz
sh_p=Vector((-2.4,11.2,2.9)); sh_t=Vector((-0.6,8.6,2.3))     # over the farmer's shoulder
def chase(f):
    a=PP(f); v=(PP(min(FL,f+1))-PP(max(F0,f-1)))
    if v.length<1e-6: v=Vector((0,-1,0))
    v.normalize(); side=v.cross(Vector((0,0,1))).normalized()
    return a-v*0.17+Vector((0,0,0.06))+side*0.04, a+v*0.05
S4P,S4X,S4Z=s4st(FS4); S4T=S4P+dirof(S4X,S4Z)*(S4P-PP(FS4)).length
CAM={}
for f in range(FA,FS4+1):
    if f<=156:
        o=orig(f); w=sm(FA,156,f); p=o[0].lerp(sh_p,w); t=o[1].lerp(sh_t,w)
    elif f<=176:
        c=chase(max(f,F0+2)); w=sm(156,176,f); p=sh_p.lerp(c[0],w); t=sh_t.lerp(c[1],w)
    elif f<=FL+2:
        p,t=chase(min(f,FL))
        if f>FL: p=p+Vector((0,0,-0.05*(f-FL)))               # punch through the surface right behind the pellet
    else:
        # orbit over the sinking pellet from the chase side to the S4 side, pulling back to reveal the shrimp
        c0,_=chase(FL); r0=c0+Vector((0,0,-0.10))-PP(FL); r1=S4P-PP(FS4)
        def sph(r): return math.atan2(r.y,r.x), math.asin(max(-1,min(1,r.z/r.length))), r.length
        a0,e0,d0=sph(r0); a1,e1,d1=sph(r1); a1=a0+wrap(a1-a0)
        w=sm(FL+2,FS4,f); az=a0+(a1-a0)*w; el=e0+(e1-e0)*w+0.55*math.sin(math.pi*w); d=d0*(d1/d0)**w
        r=Vector((math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)))*d
        p=PP(f)+r; t=PP(f).lerp(S4T,sm(FS4-22,FS4,f))
    CAM[f]=(p,t)
# gaussian smoothing of position and look target (ends pinned)
def smooth(key,sig):
    out={}
    for f in CAM:
        acc=Vector(); ws=0.0
        for g in range(f-3*sig,f+3*sig+1):
            if g in CAM:
                w=math.exp(-0.5*((g-f)/sig)**2); acc+=CAM[g][key]*w; ws+=w
        out[f]=acc/ws
    return out
SP=smooth(0,5); ST=smooth(1,7)
for f in CAM:
    k=min(sm(FA,FA+16,f),1-sm(FS4-10,FS4,f))                   # pin the ends to the original/S4 poses
    CAM[f]=(CAM[f][0].lerp(SP[f],k),CAM[f][1].lerp(ST[f],k))
prev=ev(cam,'rotation_euler',2,FA-1); R={}
for f in range(FA,FS4+1):
    rx,rz=look(*CAM[f]); rz=prev+wrap(rz-prev); prev=rz; R[f]=(rx,rz)
R[FS4]=(S4X,R[FS4-1][1]+wrap(S4Z-R[FS4-1][1])); CAM[FS4]=(S4P,CAM[FS4][1])
for idx in range(3):
    old=[(kp.co[0],kp.co[1]) for kp in findfc(cam,'location',idx).keyframe_points if kp.co[0]<FA]
    setkeys(cam,'location',idx,old+[(f,CAM[f][0][idx]) for f in range(FA,FS4+1)],'BEZIER')
for idx,j in ((0,0),(2,1)):
    old=[(kp.co[0],kp.co[1]) for kp in findfc(cam,'rotation_euler',idx).keyframe_points if kp.co[0]<FA]
    setkeys(cam,'rotation_euler',idx,old+[(f,R[f][j]) for f in range(FA,FS4+1)],'BEZIER')
setkeys(cam.data,'lens',0,[(97,24),(200,24),(FS4,32)],'BEZIER')
for m in sc.timeline_markers:
    if m.camera==s4: m.frame=FS4
# motion report: max linear speed (m/frame) and angular speed (deg/frame)
sp=max((CAM[f+1][0]-CAM[f][0]).length for f in range(FA,FS4))
ang=max(math.degrees(dirof(*R[f]).angle(dirof(*R[f+1]))) for f in range(FA,FS4))
cross=[f for f in range(FA,FS4) if CAM[f][0].z>=0 and CAM[f+1][0].z<0]
dmin=min((CAM[f][0]-PP(f)).length for f in range(171,FL+1))
hres=dict(hero_air=HN,land_f=FL,land=[round(v,2) for v in LAND],cross=cross,max_speed=round(sp,3),max_turn_deg=round(ang,2),chase_dist=round(dmin,3))
