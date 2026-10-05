# Higgsfield 3D Jutsu edit (rev 27 -> 28): feed is eaten in the water column. Pellets sink slowly and never reach the floor;
# the hero shrimp lifts 10 cm and catches its pellet mid-water; S4/S5 cameras follow; collision pass re-run (from previs-v7).
import bpy, math, random
from mathutils import Vector, Matrix
random.seed(5)
D=bpy.data; sc=bpy.context.scene
def allfc(o):
    ad=o.animation_data
    if not ad or not ad.action: return []
    r=[]
    for L in ad.action.layers:
        for s in L.strips:
            for cb in s.channelbags: r+=list(cb.fcurves)
    return r
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
def wrap(a):
    while a>math.pi: a-=2*math.pi
    while a<-math.pi: a+=2*math.pi
    return a

# ---------- feed is eaten in the water column: pellets never reach the pond floor ----------
def sm(a,b,x):
    t=min(1,max(0,(x-a)/(b-a))); return t*t*(3-2*t)
rng=random.Random(11)
pel=D.objects['FEED_Pellet_UW_076']
n_sink=0
for o in D.objects:
    if not o.name.startswith('FEED_Pellet_UW') or o is pel: continue
    fz=findfc(o,'location',2,False)
    if not fz: continue
    k0=fz.keyframe_points[0].co; st,z0=k0[0],k0[1]
    depth=min(1.22,rng.uniform(0.0062,0.0075)*(360-st))          # slow sink, ends >= 28 cm above the floor
    setkeys(o,'location',2,[(st,z0),(360,z0-depth)])
    for path,idx in (('scale',0),('scale',1),('scale',2),('hide_render',0)):
        fc=findfc(o,path,idx,False)
        if not fc: continue
        pts=[(kp.co[0],kp.co[1]) for kp in fc.keyframe_points]
        keep=[]
        for f,v in pts:
            keep.append((f,v,'CONSTANT'))
            if (path=='scale' and v>0 and f>=st-1) or (path=='hide_render' and v==0 and f>=st-1): break
        setkeys(o,path,idx,keep,'CONSTANT')
    n_sink+=1
LIFT=0.10
PZ=-1.499+LIFT
fz=findfc(pel,'location',2,False); k0=fz.keyframe_points[0].co
setkeys(pel,'location',2,[(k0[0],k0[1]),(276,PZ),(282,PZ+0.017)])
hero=D.objects['SHRIMP_05_Rig']
for idx,fn in ((2,lambda f,v: v+LIFT*sm(252,274,f)),):
    fc=findfc(hero,'location',idx,False); vals=[(f,fn(f,fc.evaluate(f))) for f in range(1,361)]
    setkeys(hero,'location',idx,vals)
fc=findfc(hero,'rotation_euler',1,False)
setkeys(hero,'rotation_euler',1,[(f,fc.evaluate(f)*(1-sm(266,276,f))) for f in range(1,361)])
cam4=D.objects['CAM_S4_Follow_Feed']; cam5=D.objects['CAM_S5_Reveal']
for cam,rng_f,off in ((cam4,range(181,301),lambda f: LIFT*sm(248,272,f)),(cam5,range(289,361),lambda f: LIFT*(1-sm(289,306,f)))):
    fc=findfc(cam,'location',2,False); vals=[(f,fc.evaluate(f)+off(f)) for f in rng_f]
    setkeys(cam,'location',2,vals,'BEZIER')
_FC.clear()
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
cam4=D.objects['CAM_S4_Follow_Feed']; cam5=D.objects['CAM_S5_Reveal']; pel=D.objects['FEED_Pellet_UW_076']
CORR={}
for f in range(262,301):
    sc.frame_set(f); c=(cam4 if f<=288 else cam5).matrix_world.translation.copy()
    p=Vector((ev(pel,'location',0,f),ev(pel,'location',1,f),ev(pel,'location',2,f)))
    CORR[f]=(c,p)
def keepout(f):
    if f not in CORR: return
    c,p=CORR[f]
    for a in AG:
        if a['pin']: continue
        q1,q2=caps(a)
        for q in (q1,q2,a['pos']):
            d=p-c; t=max(0.0,min(0.92,(q-c).dot(d)/d.dot(d))); cl=c+d*t; v=q-cl; L=v.length; R=(0.07+0.30*(1.0-t))*min(1.0,(f-261)/10.0,(301-f)/6.0)
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
result=dict(agents=len(AG),frames_with_overlap=len(report),first=report[:12],corridor_frames=len(CORR))
result['sunk']=n_sink; result['pel076_z']=[round(ev(pel,'location',2,f),3) for f in (200,250,276,290)]; result['hero_z']=[round(ev(hero,'location',2,f),3) for f in (250,262,274,290)]
