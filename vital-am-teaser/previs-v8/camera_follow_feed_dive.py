import bpy, math
from mathutils import Vector, Euler
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
def setkeys(o,path,idx,keys):
    fc=findfc(o,path,idx)
    if fc is None:
        try: o.keyframe_insert(path,index=idx,frame=keys[0][0])
        except TypeError: o.keyframe_insert(path,frame=keys[0][0])
        fc=findfc(o,path,idx)
    fc.keyframe_points.clear(); fc.keyframe_points.add(len(keys))
    for kp,(f,v) in zip(fc.keyframe_points,keys):
        kp.co=(f,v); kp.interpolation='BEZIER'; kp.handle_left_type=kp.handle_right_type='AUTO_CLAMPED'
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
cam=D.objects['CAM_S3_Drone']; s4=D.objects['CAM_S4_Follow_Feed']
T0,T1,TS=142,236,212   # blend start, hand-off to CAM_S4, start of the underwater turn
def orig(f):
    p=Vector([ev(cam,'location',i,f) for i in range(3)]); rx=ev(cam,'rotation_euler',0,f); rz=ev(cam,'rotation_euler',2,f)
    return p, p+dirof(rx,rz)*6.0
def s4st(f):
    return Vector([ev(s4,'location',i,f) for i in range(3)]), ev(s4,'rotation_euler',0,f), ev(s4,'rotation_euler',2,f)
# centroid of the second scoop throw (T1), the one the camera chases
t1=[o for o in D.objects if o.name.startswith('FEED_Air_T1_')]
P={o.name:{} for o in t1}
for f in range(156,196):
    sc.frame_set(f)
    for o in t1:
        if o.matrix_world.to_scale()[0]>1e-3: P[o.name][f]=o.matrix_world.translation.copy()
S=[n for n in P if all(f in P[n] for f in range(163,185))]
def cen(f):
    acc=Vector()
    for n in S:
        ks=[k for k in P[n] if k<=f]; acc+=P[n][max(ks)] if ks else P[n][min(P[n])]
    return acc/len(S)
C={f:cen(f) for f in range(156,196)}
land=next(f for f in range(170,196) if C[f].z<0.06); fl=list(range(159,land+1)); L=C[land].copy(); L.z=0.0
sh_p=Vector((-2.6,11.0,2.7)); sh_t=Vector((-0.5,8.4,2.3))   # over the farmer's shoulder at the throw
def chase(f):
    f2=min(max(f,min(fl)),land); c=C[f2]; k=sm(163,178,f)
    off=Vector((-0.45,0.95,0.35)).lerp(Vector((-0.06,0.30,0.10)),k)
    lead=Vector((0,-0.20,-0.06))*(1-k)
    return c+off, c+lead
UWs=[]
for o in D.objects:
    if o.name.startswith('FEED_Pellet_UW'):
        z=findfc(o,'location',2)
        if not z: continue
        st=next((f for f in range(170,240) if z.evaluate(f)<-0.01),None)
        if st and 184<=st<=206 and (Vector((ev(o,'location',0,st),ev(o,'location',1,st)))-L.xy).length<0.6: UWs.append((o,st))
def U(f):
    ps=[Vector([ev(o,'location',i,f) for i in range(3)]) for o,st in UWs]
    return sum(ps,Vector())/len(ps) if ps else L.copy()
pre={}
for f in range(T0,TS+1):
    if f<=160:
        a=orig(f); w=sm(T0,160,f); p=a[0].lerp(sh_p,w); t=a[1].lerp(sh_t,w)
    elif f<=168:
        b=chase(f); w=sm(160,168,f); p=sh_p.lerp(b[0],w); t=sh_t.lerp(b[1],w)
    elif f<=land:
        p,t=chase(f)
    else:   # punch through the surface and look down into the falling feed
        b=chase(land); w=sm(land,land+8,f); u=U(f)
        p=b[0].lerp(u+Vector((0.03,0.30,0.08)),w); t=b[1].lerp(u+Vector((0.0,-0.05,-0.14)),w)
    pre[f]=(p,)+look(p,t)
# unwrap yaw
prev=ev(cam,'rotation_euler',2,T0-1); keys={}
for f in range(T0,TS+1):
    p,rx,rz=pre[f]; rz=prev+wrap(rz-prev); prev=rz; keys[f]=[p,rx,rz]
# underwater: hermite into CAM_S4's pose and velocity at T1, with a downward dip while the yaw turns
p0,rx0,rz0=keys[TS]; pm,rxm,rzm=keys[TS-1]
v0=(p0-pm); vx0=rx0-rxm; vz0=rz0-rzm
p1,rx1,rz1=s4st(T1); q,rxq,rzq=s4st(T1+1); v1=(q-p1); vx1=rxq-rx1; vz1=rzq-rz1
rz1=rz0+wrap(rz1-rz0)
N=T1-TS
def herm(a,b,va,vb,t):
    h00=2*t**3-3*t*t+1; h10=t**3-2*t*t+t; h01=-2*t**3+3*t*t; h11=t**3-t*t
    return a*h00+va*N*h10+b*h01+vb*N*h11
for f in range(TS+1,T1+1):
    t=(f-TS)/N
    p=herm(p0,p1,v0,v1,t); rx=herm(rx0,rx1,vx0,vx1,t)-0.15*math.sin(math.pi*t)**2
    rz=rz0+(rz1-rz0)*sm(0,1,t)
    keys[f]=[p,rx,rz]
# keep the original drone keys before the blend, then per-frame keys
for idx in range(3):
    old=[(kp.co[0],kp.co[1]) for kp in findfc(cam,'location',idx).keyframe_points if kp.co[0]<T0-6]
    mid=[(f,ev(cam,'location',idx,f)) for f in range(T0-6,T0)]
    setkeys(cam,'location',idx,old+mid+[(f,keys[f][0][idx]) for f in range(T0,T1+1)])
for idx,j in ((0,1),(2,2)):
    old=[(kp.co[0],kp.co[1]) for kp in findfc(cam,'rotation_euler',idx).keyframe_points if kp.co[0]<T0-6]
    mid=[(f,ev(cam,'rotation_euler',idx,f)) for f in range(T0-6,T0)]
    setkeys(cam,'rotation_euler',idx,old+mid+[(f,keys[f][j]) for f in range(T0,T1+1)])
setkeys(cam,'rotation_euler',1,[(97,0.0),(T1,0.0)])
cam.data.lens=24
setkeys(cam.data,'lens',0,[(97,24),(TS,24),(T1,32)])
cam.data.clip_start=0.02
for m in sc.timeline_markers:
    if m.camera==s4: m.frame=T1
    if m.name.startswith('S4'): m.name='S4_underwater_feeding'
    if m.name.startswith('S3'): m.name='S3_drone_follow_feed_dive'
cross=[f for f in range(T0,T1) if keys[f][0].z>=0 and keys[f+1][0].z<0]
result=dict(nU=len(UWs),L=[round(v,2) for v in L],cross=cross,
            k=[(f,[round(v,2) for v in keys[f][0]],round(keys[f][1],2),round(keys[f][2],2)) for f in range(142,237,6)],
            markers=[(m.name,m.frame) for m in sc.timeline_markers])
