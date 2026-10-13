# Apply previs state for output frame F to the Blender film scene
import bpy, json, math
from mathutils import Matrix, Vector, Quaternion
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
C=Matrix.Rotation(math.radians(90),4,'X'); Ci=C.inverted()
def tm(e): return Matrix([e[0:4],e[4:8],e[8:12],e[12:16]]).transposed()
def ow(e): return C@tm(e)@Ci
def states(frames):
    want=set(frames); cur={}; out={}
    with open(S+'bt/dump.jsonl') as fh:
        for line in fh:
            d=json.loads(line)
            for k,v in d['mats'].items(): cur[int(k)]=v
            if d['F'] in want:
                d['all']=dict(cur); out[d['F']]=d
            if len(out)==len(want): break
    return out
class Shrimp:
    def __init__(self):
        self.act=bpy.data.actions[0] if bpy.data.actions else None
        self.rigs=sorted([o for o in bpy.data.objects if o.name.startswith('SHR_')],key=lambda o:o.name)
        self.ch=[]
        if self.act:
            for fc in self.act.fcurves: self.ch.append((fc, fc.data_path, fc.array_index))
    def pose(self,rig,t,P=7.0,D=1.0,fps=24):
        t=t%P
        if t<D: x=t/D; w=x*x*(3-2*x); ta,tb=t,t+P
        else: w=1.0; ta,tb=t,t
        pb=rig.pose.bones; vals={}
        for fc,dp,ix in self.ch:
            v=fc.evaluate(ta*fps)*w+fc.evaluate(tb*fps)*(1-w) if w<1 else fc.evaluate(ta*fps)
            vals.setdefault(dp,{})[ix]=v
        for dp,comp in vals.items():
            bone=dp.split('"')[1]; prop=dp.rsplit('.',1)[1]
            if bone not in pb: continue
            b=pb[bone]
            if prop=='rotation_quaternion':
                q=Quaternion([comp.get(i,0) for i in range(4)]); q.normalize(); b.rotation_mode='QUATERNION'; b.rotation_quaternion=q
            elif prop=='location': b.location=[comp.get(i,0) for i in range(3)]
            elif prop=='scale': b.scale=[comp.get(i,1) for i in range(3)]
def smooth_keys(K,F):
    # K: list of (frame, (x,y,z)) ; Catmull-Rom through keys, clamped
    if F<=K[0][0]: return Vector(K[0][1])
    if F>=K[-1][0]: return Vector(K[-1][1])
    for i in range(len(K)-1):
        if K[i][0]<=F<=K[i+1][0]:
            p0=Vector(K[max(0,i-1)][1]); p1=Vector(K[i][1]); p2=Vector(K[i+1][1]); p3=Vector(K[min(len(K)-1,i+2)][1])
            t=(F-K[i][0])/(K[i+1][0]-K[i][0]); t=t*t*(3-2*t)
            return 0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
# farmer faces -Y; local offsets (right=-X, forward=-Y, up=+Z) from the rig origin
HANDK=[(0,(-0.30,-0.22,0.98)),(196,(-0.30,-0.22,0.98)),(206,(-0.40,-0.05,0.74)),(212,(-0.40,-0.02,0.72)),(219,(-0.28,-0.22,1.10)),(226,(-0.18,-0.55,1.46)),(236,(-0.08,-0.42,1.88)),(262,(-0.22,-0.42,1.20)),(400,(-0.26,-0.30,1.02))]
SPINEK=[(0,(0,0,0)),(196,(0,0,0)),(206,(16,0,-6)),(212,(18,0,-8)),(219,(4,0,8)),(226,(-4,0,-12)),(236,(-2,0,-16)),(262,(2,0,-6)),(400,(0,0,0))]
def apply_farmer(F):
    arm=bpy.data.objects.get('FARMER_RIG')
    if not arm: return
    base=arm.location.copy(); h=smooth_keys(HANDK,F)
    bpy.data.objects['HAND_TGT'].location=base+h
    bpy.data.objects['ELBOW_POLE'].location=base+Vector((-0.75,0.35,1.0))
    sp=smooth_keys(SPINEK,F); pb=arm.pose.bones
    pb['Spine01'].rotation_euler=[math.radians(v) for v in sp]
    pb['LeftArm'].rotation_euler=(0,0,math.radians(28)); pb['LeftForeArm'].rotation_euler=(math.radians(12),0,0)
    bpy.context.view_layer.update()
    import importlib, sys as _s
    fl=_s.modules.get('farmer_lib')
    if fl is None:
        _s.path.insert(0,S+'bt'); import farmer_lib as fl
    fl.attach_to_hand(bpy.data.objects['SCOOP'],arm,'RightHand',off=(0,0.06,0),rot=(0,0,0))
def set_mode(d):
    sc=bpy.context.scene; w=sc.world; nt=w.node_tree; sk=nt.nodes['SKY']; bg=nt.nodes['Background']
    sunv=Vector((d['sun'][0],-d['sun'][2],d['sun'][1])).normalized()
    if d['shot']=='s5':   # golden low sun beside the bag (previs disc sits too high for a golden sky)
        k=max(0.0,min(1.0,(d['f']-318)/42.0)); el=math.radians(2.5+5.0*k); az=math.radians(-16)
        sunv=Vector((math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)))
    sk.sun_elevation=math.asin(max(-0.2,min(1,sunv.z))); sk.sun_rotation=math.atan2(sunv.x,sunv.y)+SUNROT_OFF
    room=d['room']; under=d['under']
    so=bpy.data.objects['SUN']
    lv=sunv if not under else Vector((sunv.x*0.5,sunv.y*0.5,1.2)).normalized()   # underwater: steeper key so light falls through the surface (dykes would shadow a 4 deg sun)
    so.rotation_euler=(-lv).to_track_quat('-Z','Y').to_euler()
    bg.inputs[1].default_value=0.03 if room else 0.27
    so.data.energy=0 if room else (8.0 if under else 3.2)
    bpy.data.objects['ROOM_WIN'].data.energy=22 if room else 0
    bpy.data.objects['PHONE_GLOW'].data.energy=0.5 if room else 0
    uo=bpy.data.objects['UW_FILL']; uo.data.energy=3.5 if under else 0
    if under:
        cm=sc.camera.matrix_world; fwd=(cm.to_3x3()@Vector((0,0,-1))).normalized(); uo.rotation_euler=(fwd+Vector((0,0,-0.4))).normalized().to_track_quat('-Z','Y').to_euler()
    bpy.data.objects['GOBO'].hide_render=not under
    for o in bpy.data.objects:
        if o.name.startswith(('GROUND_FAR','TREE_','PALM_FAR','WATER_VOLUME')): o.hide_render=room
    sc.node_tree.nodes['HAZE_AMT'].inputs[1].default_value=0.0 if (room or under) else 0.18
    sc.view_settings.exposure=0.55 if under else 0.0
    bf=bpy.data.objects['BAG_FILL']; f=d['f']; k=max(0,min(1,(f-334)/22.0)); bf.data.energy=60*k
    jb=bpy.data.objects['JS_BAG']; bf.location=jb.matrix_world.translation+Vector((0.4,-1.9,0.9)); bf.rotation_euler=(Vector((0,0,0.35))+jb.matrix_world.translation-bf.location).to_track_quat('-Z','Y').to_euler()
SUNROT_OFF=0.0
def apply(d, shrimp, pel_scale=0.8):
    sc=bpy.context.scene; idx=json.loads(sc['idxmap']); vis=d['vis']
    for k,name in idx.items():
        o=bpy.data.objects.get(name)
        if o is None: continue
        i=int(k); m=d['all'].get(i)
        if m: o.matrix_world=ow(m)
        if name not in ('FARMER_Root','FARMER_Scoop_Load','FARMER_Feed_Bucket'):
            o.hide_render = vis[i]!='1'
            for c in o.children_recursive: c.hide_render=o.hide_render
    fv=d['vis'][[k for k,v in idx.items() if v=='FARMER_Root'][0] and int([k for k,v in idx.items() if v=='FARMER_Root'][0])]=='1' and d['shot'] in ('s3','s4')
    for n in ('FARMER_RIG','FARMER_BODY','SCOOP','BUCKET_FEED','BUCKET_BODY'):
        o=bpy.data.objects.get(n)
        if o:
            o.hide_render=not fv
            for c in o.children_recursive: c.hide_render=not fv
    if fv: apply_farmer(d['F'])
    hn=bpy.data.objects.get('HAND_NEW')
    if hn:
        hs=bpy.data.objects['HAND_Skin']; hn.hide_render=hs.hide_render; hs.hide_render=True; bpy.data.objects['HAND_Forearm_Sleeve'].hide_render=True
    set_mode(d)
    cam=sc.camera; cam.matrix_world=C@tm(d['cam']); cam.data.lens=d['mm']
    cam.data.clip_start=0.005 if d['room'] or d['under'] else 0.03; cam.data.clip_end=2000
    # client shrimp
    for rig,(v,m,t) in zip(shrimp.rigs,d['shr']):
        on=bool(v); rig.hide_render=not on
        for ch in rig.children: ch.hide_render=not on
        if on: rig.matrix_world=ow(m); shrimp.pose(rig,t)
    for r in shrimp.rigs[len(d['shr']):]:
        r.hide_render=True
        for ch in r.children: ch.hide_render=True
    # pellets: hi (client pellet geometry), lo (spheres in previs -> pellet here)
    pool=[bpy.data.objects['PEL_%03d'%i] for i in range(700)]; j=0
    for e in d['inst']['hi']:
        if j>=700: break
        pool[j].matrix_world=ow(e)@Matrix.Scale(pel_scale,4); pool[j].hide_render=False; j+=1
    for e in d['inst']['lo']:
        if j>=700: break
        pool[j].matrix_world=ow(e)@Matrix.Scale(0.002*pel_scale,4); pool[j].hide_render=False; j+=1
    for q in pool[j:]: q.hide_render=True
    for kind,key,n in (('BUB','bub',80),('DROP','drop',160),('RING','ring',40)):
        L=d['inst'][key]
        for i in range(n):
            o=bpy.data.objects['%s_%03d'%(kind,i)]
            if i<len(L): o.matrix_world=ow(L[i]); o.hide_render=False
            else: o.hide_render=True
