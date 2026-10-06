# Higgsfield 3D Jutsu edit (rev 28 -> 29, refined on rev 29 -> 30): one continuous, smoothed camera that follows ONE hero pellet
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
FA,FS4=97,262                      # drone curve rebuilt from FA; hands over to CAM_S4 at FS4
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

# ---------- match cut, phone side: after the tap the camera rises to a top-down framing of the phone ----------
cam2=D.objects['CAM_S2_Phone']; ph=D.objects['PHONE_Root']; sc.frame_set(90)
PC=ph.matrix_world.translation.copy(); PL=(ph.matrix_world.to_3x3()@Vector((0,1,0))).normalized()   # phone long axis
H2=0.16/0.70/(2*math.tan(math.atan(18/cam2.data.lens)))                                          # phone = 70% of frame width
P2end=Vector((PC.x,PC.y,PC.z+H2)); RZ2=math.atan2(PL.y,PL.x)                                     # screen x along the phone
def ev2(i,f): return ev(cam2,'location',i,f)
rz_start=ev(cam2,'rotation_euler',2,86); RZ2=rz_start+wrap(RZ2-rz_start)
K2={0:[],1:[],2:[],'rx':[],'rz':[]}
for f in range(49,97):
    w=sm(86,96,f); p=Vector([ev2(i,f) for i in range(3)]).lerp(P2end,w)
    for i in range(3): K2[i].append((f,p[i]))
    K2['rx'].append((f,ev(cam2,'rotation_euler',0,f)*(1-w)+0.0*w)); K2['rz'].append((f,rz_start*(1-w)+RZ2*w if f>=86 else ev(cam2,'rotation_euler',2,f)))
for i in range(3): setkeys(cam2,'location',i,K2[i],'BEZIER')
setkeys(cam2,'rotation_euler',0,K2['rx'],'BEZIER'); setkeys(cam2,'rotation_euler',2,K2['rz'],'BEZIER')
hr=D.objects['HAND_Root']
for fc in (allfc(hr) if not hr.get('v10_retimed') else []):
    for kp in fc.keyframe_points:
        if kp.co[0]>86: kp.co[0]=86+(kp.co[0]-86)*0.55; kp.handle_left[0]=86+(kp.handle_left[0]-86)*0.55; kp.handle_right[0]=86+(kp.handle_right[0]-86)*0.55
    fc.update()
hr['v10_retimed']=1
# ---------- 3. camera ----------
def orig(f):
    p=Vector([ev(cam,'location',i,f) for i in range(3)]); return p, p+dirof(ev(cam,'rotation_euler',0,f),ev(cam,'rotation_euler',2,f))*6.0
def s4st(f):
    p=Vector([ev(s4,'location',i,f) for i in range(3)]); rx=ev(s4,'rotation_euler',0,f); rz=ev(s4,'rotation_euler',2,f); return p,rx,rz
sh_p=Vector((-2.4,11.2,2.9)); sh_t=Vector((-0.6,8.6,2.3)); RZ0=math.pi        # pond long axis (x) horizontal on screen     # over the farmer's shoulder
def chase(f):
    # beside and slightly behind the pellet, at its height: the pellet reads against the dawn sky and horizon
    a=PP(f); v=(PP(min(FL,f+1))-PP(max(F0,f-1)))
    vh=Vector((v.x,v.y,0.0))
    if vh.length<1e-6: vh=Vector((0,-1,0))
    vh.normalize(); side=vh.cross(Vector((0,0,1))).normalized()
    return a-vh*0.10+side*0.045+Vector((0,0,0.02)), a
S4P,S4X,S4Z=s4st(FS4); S4T=S4P+dirof(S4X,S4Z)*(S4P-PP(FS4)).length
CAM={}; DRZ={}
for f in range(FA,FS4+1):
    if f<=156:
        # match cut: opens straight down on the feeding pond (dark rectangle framed like the phone), then spirals down to the shoulder
        u=f; wpos=sm(99,156,u); wpos=wpos*wpos*(3-2*wpos)          # extra-soft ease
        P0=Vector((0.0,0.0,44.0)); p=P0.lerp(sh_p,wpos)
        p+=Vector((0,0,0))
        rx1,rz1=look(sh_p,sh_t); rz1=RZ0+wrap(rz1-RZ0)
        rx=0.002+(rx1-0.002)*sm(108,154,u); rz=RZ0+(rz1-RZ0)*sm(103,152,u)
        t=p+dirof(rx,rz)*10.0; DRZ[f]=rz
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
# while following the pellet, smooth relative to the pellet so it stays framed
REL={f:(CAM[f][0]-PP(f),CAM[f][1]-PP(f)) for f in CAM}
def smooth_rel(key,sig):
    out={}
    for f in CAM:
        acc=Vector(); ws=0.0
        for g in range(f-3*sig,f+3*sig+1):
            if g in REL and g>=150:
                w=math.exp(-0.5*((g-f)/sig)**2); acc+=REL[g][key]*w; ws+=w
        out[f]=PP(f)+acc/ws if ws>0 else CAM[f][key]
    return out
RP=smooth_rel(0,3); RT=smooth_rel(1,3)
for f in CAM:
    u=sm(156,168,f); SP[f]=SP[f].lerp(RP[f],u); ST[f]=ST[f].lerp(RT[f],u)
for f in CAM:
    k=min(sm(FA,FA+4,f),1-sm(FS4-10,FS4,f))                   # pin the ends to the original/S4 poses
    CAM[f]=(CAM[f][0].lerp(SP[f],k),CAM[f][1].lerp(ST[f],k))
prev=RZ0; R={}
for f in range(FA,FS4+1):
    rx,rz=look(*CAM[f]); rz=prev+wrap(rz-prev)
    if f in DRZ:                                              # near top-down the yaw from look() is ill-conditioned: use the designed yaw
        b=sm(146,156,f); rz=DRZ[f]+wrap(rz-DRZ[f])*b
    prev=rz; R[f]=(rx,rz)
R[FS4]=(S4X,R[FS4-1][1]+wrap(S4Z-R[FS4-1][1])); CAM[FS4]=(S4P,CAM[FS4][1])
for idx in range(3):
    old=[(kp.co[0],kp.co[1]) for kp in findfc(cam,'location',idx).keyframe_points if kp.co[0]<FA]
    setkeys(cam,'location',idx,old+[(f,CAM[f][0][idx]) for f in range(FA,FS4+1)],'BEZIER')
for idx,j in ((0,0),(2,1)):
    old=[(kp.co[0],kp.co[1]) for kp in findfc(cam,'rotation_euler',idx).keyframe_points if kp.co[0]<FA]
    setkeys(cam,'rotation_euler',idx,old+[(f,R[f][j]) for f in range(FA,FS4+1)],'BEZIER')
setkeys(cam.data,'lens',0,[(97,24),(156,24),(176,35),(194,35),(FS4,32)],'BEZIER')   # gentle push-in on the pellet
for m in sc.timeline_markers:
    if m.camera==s4: m.frame=FS4
# motion report: max linear speed (m/frame) and angular speed (deg/frame)
sp=max((CAM[f+1][0]-CAM[f][0]).length for f in range(FA,FS4))
ang=max(math.degrees(dirof(*R[f]).angle(dirof(*R[f+1]))) for f in range(FA,FS4))
cross=[f for f in range(FA,FS4) if CAM[f][0].z>=0 and CAM[f+1][0].z<0]
dmin=min((CAM[f][0]-PP(f)).length for f in range(171,FL+1))
hres=dict(phone_cam=[round(v,3) for v in P2end]+[round(RZ2,3)],land_f=FL,land=[round(v,2) for v in LAND],cross=cross,max_speed=round(sp,3),max_turn_deg=round(ang,2),chase_dist=round(dmin,3))

# ================= re-run the no-overlap pass with the camera corridor along the new path =================

import random
random.seed(5)
_FC={}
def findfc(o,path,idx,cache=True):
    key=(o.name,path,idx)
    if cache and key in _FC: return _FC[key]
    r=None
    for fc in allfc(o):
        if fc.data_path==path and fc.array_index==idx: r=fc; break
    if cache: _FC[key]=r
    return r
def setkeys(o,path,idx,keys,interp='LINEAR'):
    fc=findfc(o,path,idx,False)
    if fc is None:
        try: o.keyframe_insert(path,index=idx,frame=keys[0][0])
        except TypeError: o.keyframe_insert(path,frame=keys[0][0])
        fc=findfc(o,path,idx,False)
    fc.keyframe_points.clear(); fc.keyframe_points.add(len(keys))
    for kp,(f,v,*ip) in zip(fc.keyframe_points,keys):
        kp.co=(f,v); kp.interpolation=ip[0] if ip else interp
        kp.handle_left_type=kp.handle_right_type='AUTO_CLAMPED'
    fc.update()
def ev(o,path,idx,f,default=0.0):
    fc=findfc(o,path,idx); return fc.evaluate(f) if fc else default
from mathutils import Matrix
BOT=-1.5; FRONT,BACK,RAD=0.056,-0.081,0.0118; GAP=0.004
AG=[]
for o in D.objects:
    if (o.name.startswith('SHRIMP_') and o.name.endswith('_Rig') and o.name[7:9].isdigit()) or (o.name.startswith('SHRIMP_Swarm_') and o.type=='MESH'):
        AG.append(dict(o=o,s=o.scale[0],pin=False))
def state(a,f):
    o=a['o']; return Vector((ev(o,'location',0,f),ev(o,'location',1,f),ev(o,'location',2,f))),ev(o,'rotation_euler',2,f),ev(o,'rotation_euler',1,f)
hero=D.objects['SHRIMP_05_Rig']
for a in AG:
    if a['o'] is hero: a['pin']=True
def caps(a):
    c=Matrix.Rotation(a['yaw'],3,'Z')@Matrix.Rotation(a['pitch'],3,'Y')
    fwd=c@Vector((1,0,0))
    return a['pos']+fwd*FRONT*a['s'], a['pos']+fwd*BACK*a['s']
def segdist(p1,q1,p2,q2):
    d1=q1-p1; d2=q2-p2; r=p1-p2; aa=d1.dot(d1); e=d2.dot(d2); f=d2.dot(r)
    c=d1.dot(r); b=d1.dot(d2); den=aa*e-b*b
    s=max(0,min(1,(b*f-c*e)/den)) if den>1e-12 else 0.0
    t=(b*s+f)/e if e>1e-12 else 0.0
    if t<0: t=0; s=max(0,min(1,-c/aa))
    elif t>1: t=1; s=max(0,min(1,(b-c)/aa))
    c1=p1+d1*s; c2=p2+d2*t; return (c2-c1).length,c1,c2
CELL=0.17
def resolve(maxit=20):
    for it in range(maxit):
        grid={}
        for idx,a in enumerate(AG):
            k=(int(math.floor(a['pos'].x/CELL)),int(math.floor(a['pos'].y/CELL)),int(math.floor(a['pos'].z/CELL)))
            grid.setdefault(k,[]).append(idx)
        moved=False; C=[caps(a) for a in AG]
        for (gx,gy,gz),lst in grid.items():
            nb=[]
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    for dz in (-1,0,1): nb+=grid.get((gx+dx,gy+dy,gz+dz),[])
            for i in lst:
                for j in nb:
                    if j<=i: continue
                    a,b=AG[i],AG[j]
                    d,c1,c2=segdist(C[i][0],C[i][1],C[j][0],C[j][1])
                    mn=RAD*(a['s']+b['s'])+GAP
                    if d<mn:
                        n=c2-c1
                        if n.length<1e-9: n=Vector((math.cos(i+j),math.sin(i+j),0.0))
                        n.normalize(); push=(mn-d)*0.52
                        wa=0.0 if a['pin'] else (0.5 if not b['pin'] else 1.0)
                        wb=0.0 if b['pin'] else (0.5 if not a['pin'] else 1.0)
                        a['pos']-=n*push*wa*2; b['pos']+=n*push*wb*2; moved=True
        for a in AG:
            fl=BOT+0.0178*a['s']
            if a['pos'].z<fl: a['pos'].z=fl
        if not moved: return it
    return maxit
cam3=D.objects['CAM_S3_Drone']; cam4=D.objects['CAM_S4_Follow_Feed']; cam5=D.objects['CAM_S5_Reveal']; pel=D.objects['FEED_Pellet_UW_076']
CORR={}
for f in range(206,301):
    sc.frame_set(f); c=(cam3 if f<262 else (cam4 if f<=288 else cam5)).matrix_world.translation.copy()
    p=Vector((ev(pel,'location',0,f),ev(pel,'location',1,f),ev(pel,'location',2,f)))
    CORR[f]=(c,p)
def keepout(f):
    if f not in CORR: return
    c,p=CORR[f]
    for a in AG:
        if a['pin']: continue
        q1,q2=caps(a)
        for q in (q1,q2,a['pos']):
            d=p-c; t=max(0.0,min(0.92,(q-c).dot(d)/d.dot(d))); cl=c+d*t; v=q-cl; L=v.length; R=(0.07+0.30*(1.0-t))*min(1.0,(f-205)/10.0,(301-f)/6.0)
            if L<R:
                n=v.normalized() if L>1e-6 else Vector((0,0,1)); a['pos']+=n*(R-L)
for a in AG:
    a['corr']=Vector((0,0,0)); a['K']={'x':[],'y':[],'z':[]}
report=[]
for f in range(1,361):
    for a in AG:
        p,y,pt=state(a,f); a['base']=p; a['pos']=p+a['corr']; a['yaw']=y; a['pitch']=pt
    for _ in range(3):
        keepout(f); resolve(20 if f>1 else 80)
    C=[caps(a) for a in AG]; nover=0
    for i in range(len(AG)):
        for j in range(i+1,len(AG)):
            if (AG[i]['pos']-AG[j]['pos']).length>0.30: continue
            d,_,_=segdist(C[i][0],C[i][1],C[j][0],C[j][1])
            if d<0.0095*(AG[i]['s']+AG[j]['s']): nover+=1
    if nover: report.append((f,nover))
    for a in AG:
        a['corr']=(a['pos']-a['base'])*0.94
        K=a['K']; K['x'].append((f,a['pos'].x)); K['y'].append((f,a['pos'].y)); K['z'].append((f,a['pos'].z))
_FC.clear()
for a in AG:
    o=a['o']; K=a['K']
    setkeys(o,'location',0,K['x']); setkeys(o,'location',1,K['y']); setkeys(o,'location',2,K['z'])
    # rotations re-sampled every frame too, so in-between frames match the collision check exactly
    for idx in (1,2):
        fc=findfc(o,'rotation_euler',idx,False)
        if fc: 
            vals=[(f,fc.evaluate(f)) for f in range(1,361)]
            setkeys(o,'rotation_euler',idx,vals)
sc.frame_set(1)
result=dict(cam=hres,agents=len(AG),frames_with_overlap=len(report),first=report[:12],corridor_frames=len(CORR))
