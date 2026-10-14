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
def _swing(arm,bone,child,target_a):
    # rotate pose bone about its head so the head->child-head vector points at target_a (armature space)
    pb=arm.pose.bones[bone]; h=pb.head.copy(); c=arm.pose.bones[child].head.copy()
    q=(c-h).rotation_difference(target_a-h)
    pb.matrix=Matrix.Translation(h)@q.to_matrix().to_4x4()@Matrix.Translation(-h)@pb.matrix
    bpy.context.view_layer.update()
def two_bone_ik(arm,up,lo,end,T_w,P_w):
    # analytic two-bone IK (the auto-rig bone axes/tails are unreliable, so work with joint positions)
    Mi=arm.matrix_world.inverted(); pb=arm.pose.bones
    S=pb[up].head.copy(); E0=pb[lo].head.copy(); W0=pb[end].head.copy()
    L1=(E0-S).length; L2=(W0-E0).length
    T=Mi@T_w; P=Mi@P_w
    d=T-S; D=max(1e-6,min(d.length,(L1+L2)*0.999)); u=d.normalized()
    a=(L1*L1-L2*L2+D*D)/(2*D); hgt=math.sqrt(max(0.0,L1*L1-a*a))
    pv=(P-S); pv=(pv-u*pv.dot(u)); pv=pv.normalized() if pv.length>1e-6 else Vector((0,0,-1))
    E=S+u*a+pv*hgt; W=S+u*D
    _swing(arm,up,lo,E); _swing(arm,lo,end,W)
def SCOOP_ROLL(F):
    keys=[(0,0),(214,0),(220,-25),(224,70),(230,95),(246,20),(266,0),(600,0)]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if a<=F<=b: t=(F-a)/(b-a); t=t*t*(3-2*t); return va+(vb-va)*t
    return 0
GRIP_IN=0.6; FIST_S=0.13; FIST_WRIST=0.10; GRIP_C=(-0.45,0.0,-0.03); GRIP_SIDE=-1.0
def apply_farmer(F):
    import throw_anim
    arm=bpy.data.objects.get('FARMER_RIG')
    if not arm: return
    if 'base_loc' not in arm: arm['base_loc']=list(arm.location)
    b0=Vector(arm['base_loc']); arm.location=b0+Vector((0,throw_anim.root_offset(F),0))
    pb=arm.pose.bones
    base=arm.location.copy()
    for bn in ('RightForeArm','RightHand'):
        for c in [c for c in pb[bn].constraints if c.type=='IK']: pb[bn].constraints.remove(c)
    if 'FOOT_L_TGT' not in bpy.data.objects:
        # pin the feet to the deck: two-bone leg IK so hips can hinge and drop with natural knee bend
        for pb_ in pb: pb_.rotation_mode='XYZ'; pb_.rotation_euler=(0,0,0); pb_.location=(0,0,0)
        bpy.context.view_layer.update()
        for side in ('Left','Right'):
            ft=arm.matrix_world@pb[side+'Foot'].head; kn=arm.matrix_world@pb[side+'Leg'].head
            t=bpy.data.objects.new('FOOT_%s_TGT'%side[0],None); bpy.context.scene.collection.objects.link(t); t.location=ft
            p=bpy.data.objects.new('KNEE_%s_POLE'%side[0],None); bpy.context.scene.collection.objects.link(p); p.location=kn+Vector((0,-0.6,0))
            c=pb[side+'Leg'].constraints.new('IK'); c.target=t; c.pole_target=p; c.chain_count=2; c.pole_angle=math.radians(-90)
    for b,r in throw_anim.pose_at(F).items():
        if b in ('RightArm','RightForeArm'): pb[b].rotation_euler=(0,0,0); continue   # driven by IK
        if b in pb: pb[b].rotation_mode='XYZ'; pb[b].rotation_euler=r
    pb['Hips'].location=(0,throw_anim.hip_drop(F),0)
    bpy.context.view_layer.update()
    T_w=base+Vector(throw_anim.hand_target(F))
    # clavicle follows the arm (a real shoulder shrugs/protracts when reaching) so the armpit does not balloon
    Mi=arm.matrix_world.inverted(); pbs=arm.pose.bones; C=pbs['RightShoulder'].head.copy(); A=pbs['RightArm'].head.copy(); T=Mi@T_w
    up=max(0.0,min(1.0,(T.z-A.z)/40.0+0.4))      # armature units are cm
    dirA=(A-C).normalized(); dirT=(T-C).normalized(); nd=dirA.lerp(dirT,0.28*up).normalized()
    _swing(arm,'RightShoulder','RightArm',C+nd*(A-C).length)
    two_bone_ik(arm,'RightArm','RightForeArm','RightHand',T_w,base+Vector(throw_anim.elbow_pole(F)))
    bpy.context.view_layer.update()
    import sys as _s
    fl=_s.modules.get('farmer_lib')
    if fl is None:
        _s.path.insert(0,S+'bt'); import farmer_lib as fl
    fist=bpy.data.objects.get('FIST')
    if fist is None:
        fl.attach_to_hand(bpy.data.objects['SCOOP'],arm,'RightHand',off=(0,0.06,0),rot=(0,0,0)); return
    # frame from joint positions (the auto-rig bone axes are unreliable): X back along the forearm, palm toward body/down
    bpy.context.view_layer.update(); pb=arm.pose.bones
    wr=arm.matrix_world@pb['RightHand'].head; el=arm.matrix_world@pb['RightForeArm'].head
    fwd=(wr-el).normalized(); ref=Vector((GRIP_IN,0.0,-1.0)).normalized()
    pn=(ref-fwd*ref.dot(fwd));
    if pn.length<1e-4: pn=Vector((0,-1,0))-fwd*fwd.y
    pn.normalize(); X=-fwd; Z=-pn; Y=Z.cross(X).normalized(); R=Matrix((X,Y,Z)).transposed().to_4x4()
    fist.matrix_world=Matrix.Translation(wr)@R@Matrix.Scale(FIST_S,4)@Matrix.Translation(Vector((-FIST_WRIST,0,0)))
    G=fist.matrix_world@Vector(GRIP_C)
    # scoop: handle (local Y, centre at y=0.06) through the fist across the palm, cup on the thumb side
    sY=Y*GRIP_SIDE; sZ=X.copy(); sX=sY.cross(sZ).normalized()
    Rs=Matrix((sX,sY,sZ)).transposed().to_4x4()
    Rs=Rs@Matrix.Rotation(math.radians(SCOOP_ROLL(F)),4,'Y')
    bpy.data.objects['SCOOP'].matrix_world=Matrix.Translation(G)@Rs@Matrix.Translation(Vector((0,-0.06,0)))
    fist.hide_render=bpy.data.objects['FARMER_BODY'].hide_render
def set_mode(d):
    sc=bpy.context.scene; w=sc.world; nt=w.node_tree; sk=nt.nodes['SKY']; bg=nt.nodes['Background']
    sunv=Vector((d['sun'][0],-d['sun'][2],d['sun'][1])).normalized()
    if d['under']:   # one constant sun for every underwater shot (previs sun jumps 4 -> 25 deg at the s4/s5 cut)
        sunv=Vector((0.0,300.0,22.0)).normalized()
    elif d['shot']=='s5':   # golden low sun beside the bag (previs disc sits too high for a golden sky)
        k=max(0.0,min(1.0,(d['f']-318)/42.0)); el=math.radians(2.5+5.0*k); az=math.radians(-16)
        sunv=Vector((math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)))
    sk.sun_elevation=math.asin(max(-0.2,min(1,sunv.z))); sk.sun_rotation=math.atan2(sunv.x,sunv.y)+SUNROT_OFF
    room=d['room']; under=d['under']
    so=bpy.data.objects['SUN']
    lv=sunv if not under else Vector((sunv.x*0.5,sunv.y*0.5,1.2)).normalized()   # underwater: steeper key so light falls through the surface (dykes would shadow a 4 deg sun)
    so.rotation_euler=(-lv).to_track_quat('-Z','Y').to_euler()
    bg.inputs[1].default_value=0.03 if room else 0.27
    so.data.energy=0 if room else (10.0 if under else 3.2)
    bpy.data.objects['ROOM_WIN'].data.energy=22 if room else 0
    bpy.data.objects['PHONE_GLOW'].data.energy=0.5 if room else 0
    uo=bpy.data.objects['UW_FILL']; uo.data.energy=5.0 if under else 0
    if under:
        cm=sc.camera.matrix_world; fwd=(cm.to_3x3()@Vector((0,0,-1))).normalized(); uo.rotation_euler=(fwd+Vector((0,0,-0.4))).normalized().to_track_quat('-Z','Y').to_euler()
    bpy.data.objects['GOBO'].hide_render=not under
    for o in bpy.data.objects:
        if o.name.startswith(('GROUND_FAR','TREE_','PALM_FAR','WATER_VOLUME')): o.hide_render=room
    sc.node_tree.nodes['HAZE_AMT'].inputs[1].default_value=0.0 if (room or under) else 0.18
    sc.view_settings.exposure=0.95 if under else 0.0
    bf=bpy.data.objects['BAG_FILL']; f=d['f']; k=max(0,min(1,(f-334)/22.0)); bf.data.energy=60*k
    jb=bpy.data.objects['JS_BAG']; bf.location=jb.matrix_world.translation+Vector((0.4,-1.9,0.9)); bf.rotation_euler=(Vector((0,0,0.35))+jb.matrix_world.translation-bf.location).to_track_quat('-Z','Y').to_euler()
SUNROT_OFF=0.0
try: CAM_SMOOTH=json.load(open(S+'bt/cam_smooth.json'))
except Exception: CAM_SMOOTH={}
try: SHR_KEEP=set(json.load(open(S+'bt/shr_keep.json')))
except Exception: SHR_KEEP=set(range(999))
def bubbles(d):
    # Real air: a short trail of tiny bubbles behind each pellet that just went in, and a plunge cloud when the
    # camera dives. (The previs scattered ~700 identical bubbles through the whole volume.)
    import random
    F=d['F']; out=[]
    if not d['under'] or F<279: return out
    cam=bpy.context.scene.camera.matrix_world
    age=F-279; decay=max(0.0,1.0-age/30.0)
    for j,e in enumerate(d['inst']['hi']):
        if decay<=0: break
        p=ow(e).translation
        if p.z>-0.004: continue
        rr=random.Random(j*7+1); n=int(round(6*decay*rr.uniform(0.5,1.0)))
        for k in range(1,n+1):
            ph=F*0.8+j*2.3+k*1.7; rise=0.0045*k*(1+0.12*age)
            q=p+Vector((0.0012*math.sin(ph),0.0012*math.cos(ph*1.3),rise))
            if q.z>-0.002: continue
            r=0.00032*rr.uniform(0.6,1.3)*(1-0.08*k)
            out.append(Matrix.Translation(q)@Matrix.Diagonal((r*(1+0.1*math.sin(ph)),r*(1+0.1*math.cos(ph)),r*0.85,1)))
    if age<16:   # camera plunge
        rr=random.Random(99); f=1.0-age/16.0
        for k in range(int(70*f)+8):
            x=rr.uniform(-1,1); y=rr.uniform(-0.6,0.9); z=rr.uniform(0.14,0.6); r=rr.uniform(0.0004,0.0016)
            loc=cam@Vector((x*z*0.55,y*z*0.4+0.012*age*(0.6+r*500),-z))
            loc.z=min(loc.z+0.004*age,-0.003); ph=F*1.1+k
            out.append(Matrix.Translation(loc)@Matrix.Diagonal((r*(1+0.12*math.sin(ph)),r*(1+0.12*math.cos(ph)),r*0.8,1)))
    return out[:800]
SPLIT=list(range(274,285))+list(range(458,469))   # waterline frames: rendered twice (air / under), joined in post
def fix_set(d):
    # the HF hut replaces the shed: follow the previs shed position, keep the proxy shed + roof hidden
    sh=bpy.data.objects['SET_Farm_Shed']; hut=bpy.data.objects.get('HF_HUT')
    if hut: hut.location=(sh.matrix_world.translation.x,sh.matrix_world.translation.y,sh.matrix_world.translation.z-1.2); hut.hide_render=d['room']
    for n in ('SET_Farm_Shed','SET_Farm_Shed_Roof','POND_Plankton_Specks'):   # previs specks read as white balls; MOTES replace them
        o=bpy.data.objects.get(n)
        if o: o.hide_render=True
    # bag shot: no palm fronds hanging into the top of the frame
    cam=bpy.context.scene.camera
    if d['under']:   # one constant sun for every underwater shot (previs sun jumps 4 -> 25 deg at the s4/s5 cut)
        sunv=Vector((0.0,300.0,22.0)).normalized()
    elif d['shot']=='s5':
        for o in bpy.data.objects:
            if o.name.startswith('coconut_palm'):
                v=o.matrix_world.translation-cam.matrix_world.translation
                if v.length<22: o.hide_render=True
    # phone: the 6:30 placeholder reads upright once the camera has turned onto the screen
    # phone -> pond match cut: start the drone tighter so the pond has the width of the phone screen, then open up
    F=d['F']
    if 118<=F<=146:
        k=(F-118)/28.0; k=k*k*(3-2*k); cam.data.lens*=MATCH_ZOOM*(1-k)+k; cam.data.shift_y=MATCH_SHY*(1-k)
    else: cam.data.shift_y=0.0
MATCH_ZOOM=1.35; MATCH_SHY=0.03
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
    for n in ('FARMER_RIG','FARMER_BODY','SCOOP','FIST','BUCKET_FEED','BUCKET_BODY'):
        o=bpy.data.objects.get(n)
        if o:
            o.hide_render=not fv
            for c in o.children_recursive: c.hide_render=not fv
    if fv: apply_farmer(d['F'])
    hn=bpy.data.objects.get('HAND_NEW')
    if hn:
        hs=bpy.data.objects['HAND_Skin']; hn.hide_render=hs.hide_render; hs.hide_render=True; bpy.data.objects['HAND_Forearm_Sleeve'].hide_render=True
    cm,mm=CAM_SMOOTH.get(str(d['F']),(d['cam'],d['mm']))
    cam=sc.camera; cam.matrix_world=C@tm(cm); cam.data.lens=mm
    cz=cam.matrix_world.translation.z
    fo=d.get('force')
    if fo=='air':      # above-water half of a waterline (split) frame
        d['under']=False; t=cam.matrix_world.copy(); t.translation.z=max(cz,0.008); cam.matrix_world=t
    elif fo=='under' or d['under'] or (not d['room'] and cz<0.004):   # never sit in the thin layer between the volume top and the surface
        d['under']=True; t=cam.matrix_world.copy(); t.translation.z=min(cz,-0.018); cam.matrix_world=t
    cam.data.clip_start=0.005 if d['room'] or d['under'] else 0.03; cam.data.clip_end=2000
    set_mode(d)
    fix_set(d)
    # client shrimp
    for si,(rig,(v,m,t)) in enumerate(zip(shrimp.rigs,d['shr'])):
        on=bool(v) and (d['F']<279 or si in SHR_KEEP); rig.hide_render=not on
        for ch in rig.children: ch.hide_render=not on
        if on: rig.matrix_world=ow(m); shrimp.pose(rig,t)
    for r in shrimp.rigs[len(d['shr']):]:
        r.hide_render=True
        for ch in r.children: ch.hide_render=True
    # pellets: hi (client pellet geometry), lo (spheres in previs -> pellet here)
    pool=[o for o in bpy.data.objects if o.name.startswith('PEL_') and o.name!='PEL_SRC']; j=0
    for e in d['inst']['hi']:
        if j>=len(pool): break
        pool[j].matrix_world=ow(e)@Matrix.Scale(pel_scale,4); pool[j].hide_render=False; j+=1
    for e in d['inst']['lo']:
        if j>=len(pool): break
        pool[j].matrix_world=ow(e)@Matrix.Scale(0.002*pel_scale,4); pool[j].hide_render=False; j+=1
    for q in pool[j:]: q.hide_render=True
    mo=bpy.data.objects.get('MOTES')
    if mo: mo.hide_render=not d['under']; mo.location=(0.0006*d['F'],0.0002*d['F'],0.0004*d['F'])
    crowns=[o for o in bpy.data.objects if o.name.startswith('CROWN_')]; nc=0
    for kind,key,n in (('BUB','bub',800),('DROP','drop',900),('RING','ring',400)):
        L=bubbles(d) if kind=='BUB' else d['inst'][key]
        for i in range(n):
            o=bpy.data.objects.get('%s_%03d'%(kind,i))
            if o is None: break
            if i<len(L):
                M=L[i] if kind=='BUB' else ow(L[i])
                if kind=='RING':   # ripples fade as they spread; a crown rises on the youngest ones
                    sr=Vector((L[i][0],L[i][1],L[i][2])).length; f=max(0.0,min(1.0,1.15-(sr-0.003)/0.006)); o.color=(f,f,f,1)
                    a=(sr-0.0028)/0.0018
                    if a<1.0 and nc<len(crowns):
                        h=0.009*max(0.0,math.sin(math.pi*max(0.0,min(1.0,a*0.85+0.15))))
                        if h>0.0006:
                            cr=crowns[nc]; cr.matrix_world=M@Matrix.Diagonal((0.9,0.9,h,1)); cr.hide_render=False; nc+=1
                o.matrix_world=M; o.hide_render=False
            else: o.hide_render=True
    for cr in crowns[nc:]: cr.hide_render=True
