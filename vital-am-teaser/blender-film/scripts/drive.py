# Apply previs state for output frame F to the Blender film scene
import bpy, json, math, os
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
            last=d
    for F in sorted(want):   # tail past the previs (END_HOLD frames): hold the last state, the camera only zooms in
        if F not in out and F>LAST_F:
            import copy as _cp
            e=_cp.deepcopy(out.get(LAST_F) or dict(last,all=dict(cur))); e['F']=F; e['f']=e['f']+(F-LAST_F)*0.5; out[F]=e
    return out
class Shrimp:
    def __init__(self):
        sw=[a for a in bpy.data.actions if 'Shrimp' in a.name]   # the client's swim clip (actions[0] became the farmer's after he was loaded)
        self.act=sw[0] if sw else (bpy.data.actions[0] if bpy.data.actions else None)
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
    keys=[(0,0),(600,0)]   # scoop stays mouth-up the whole time
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if a<=F<=b: t=(F-a)/(b-a); t=t*t*(3-2*t); return va+(vb-va)*t
    return 0
def SCOOP_PITCH(F):
    # degrees above (+) / below (-) the horizon for the shovel axis
    keys=[(0,-8),(198,-8),(204,-55),(209,-50),(214,-5),(219,2),(224,6),(232,4),(246,-8),(600,-8)]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if a<=F<=b: t=(F-a)/(b-a); t=t*t*(3-2*t); return va+(vb-va)*t
    return -8
def GRIP_ANG_AT(F):
    # wrist straightens through the throw: at full extension the scoop continues the arm
    keys=[(0,70),(214,70),(220,45),(224,10),(246,10),(266,70),(600,70)]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if a<=F<=b: t=(F-a)/(b-a); t=t*t*(3-2*t); return va+(vb-va)*t
    return 70
GRIP_ANG=70.0; GRIP_Y=0.025; GRIP_IN=0.6; FIST_S=0.13; FIST_WRIST=0.10; GRIP_C=(-0.45,0.0,-0.15); GRIP_SIDE=-1.0
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
    # dagger/ladle grip: the handle lies diagonally in the fist and the shovel points forward, continuing the forearm
    ga=math.radians(GRIP_ANG_AT(F)); sY=(-X*math.cos(ga)+Y*GRIP_SIDE*math.sin(ga)).normalized()
    # keep the feed in: the shovel stays nearly level while carrying / winding up, dips into the bucket while scooping
    hz=Vector((sY.x,sY.y,0)); hz=hz.normalized() if hz.length>1e-4 else Vector((0,-1,0))
    pz=SCOOP_PITCH(F); sY=(hz*math.cos(math.radians(pz))+Vector((0,0,math.sin(math.radians(pz))))).normalized()
    up=Vector((0,0,1)); sZ=(up-sY*up.dot(sY));
    if sZ.length<1e-4: sZ=Z.copy()
    sZ.normalize(); sX=sY.cross(sZ).normalized()
    Rs=Matrix((sX,sY,sZ)).transposed().to_4x4()
    Rs=Rs@Matrix.Rotation(math.radians(SCOOP_ROLL(F)),4,'Y')
    bpy.data.objects['SCOOP'].matrix_world=Matrix.Translation(G)@Rs@Matrix.Translation(Vector((0,-GRIP_Y,0)))
    fist.hide_render=bpy.data.objects['FARMER_BODY'].hide_render
    ld=bpy.data.objects.get('SCOOP_LOAD')
    if ld: ld.hide_render=fist.hide_render or not (209<=F<=223)   # loaded from the dip until the release
SUN_PEEK=0.007   # deepest the sun centre may sit behind the pack's silhouette edge (view units): its glow still spills round the edge, as in the approved frames
_BVH={}
def _sun_peek(sunv):
    # the slow push-in widens the pack on screen; where the pack would swallow the sun, slide it sideways (same screen height)
    # to the pack's right silhouette edge so it keeps peeking out. Frames where the sun is already visible are left untouched.
    from bpy_extras.object_utils import world_to_camera_view as w2c
    sc=bpy.context.scene; cam=sc.camera; bag=bpy.data.objects.get('JS_BAG')
    ms=[o for o in ([bag]+list(bag.children_recursive)) if o.type=='MESH'] if bag else []
    if not ms: return sunv
    from mathutils.bvhtree import BVHTree
    for o in ms:   # ray-test the pack alone (scene.ray_cast would stop at the invisible flags/scrims around it)
        if o.name not in _BVH: _BVH[o.name]=BVHTree.FromPolygons([v.co.copy() for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
    bpy.context.view_layer.update()
    P=cam.matrix_world.translation; tr,br,bl,tl=[cam.matrix_world@c for c in cam.data.view_frame(scene=sc)]
    def ray(u,v): return (bl.lerp(br,u).lerp(tl.lerp(tr,u),v)-P).normalized()
    def hidden(d):
        for o in ms:
            Mi=o.matrix_world.inverted()
            if _BVH[o.name].ray_cast(Mi@P,(Mi.to_3x3()@d).normalized())[0] is not None: return True
        return False
    if not hidden(sunv): return sunv
    s=w2c(sc,cam,P+sunv*1000.0); u=s.x
    while u<s.x+0.25 and hidden(ray(u,s.y)): u+=0.001
    return sunv if u-s.x<=SUN_PEEK else ray(u-SUN_PEEK,s.y)
def set_mode(d):
    sc=bpy.context.scene; w=sc.world; nt=w.node_tree; sk=nt.nodes['SKY']; bg=nt.nodes['Background']
    sunv=Vector((d['sun'][0],-d['sun'][2],d['sun'][1])).normalized()
    if d['under']:   # one constant sun for every underwater shot (previs sun jumps 4 -> 25 deg at the s4/s5 cut)
        sunv=Vector((0.0,300.0,22.0)).normalized()
    elif d['shot']=='s5':   # golden low sun beside the bag (previs disc sits too high for a golden sky)
        k=max(0.0,min(1.0,(d['F']-458)/131.0)); k=k*k*(3-2*k); el=math.radians(BAG_SUN_EL0+(BAG_SUN_EL1-BAG_SUN_EL0)*k); az=math.radians(BAG_SUN_AZ)   # orange sun rising right behind the pack (justifies the backlight)
        sunv=Vector((math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)))
        sunv=_sun_peek(sunv)
    sk.sun_elevation=math.asin(max(-0.2,min(1,sunv.z))); sk.sun_rotation=math.atan2(sunv.x,sunv.y)+SUNROT_OFF
    room=d['room']; under=d['under']
    so=bpy.data.objects['SUN']
    lv=sunv if not under else Vector((sunv.x*0.7,sunv.y*0.7,1.0)).normalized()   # slanted shafts read better than vertical ones   # underwater: steeper key so light falls through the surface (dykes would shadow a 4 deg sun)
    so.rotation_euler=(-lv).to_track_quat('-Z','Y').to_euler()
    bg.inputs[1].default_value=0.03 if room else 0.27
    so.data.energy=0 if room else (10.0 if under else 3.2)
    so.data.angle=math.radians(0.7 if under else 1.2)   # crisp sun under water: sharp shafts and caustic lines
    so.data.angle=math.radians(0.7 if under else 1.2)   # crisp sun under water so the caustic lines survive
    bpy.data.objects['ROOM_WIN'].data.energy=10 if room else 0
    sb=bpy.data.objects.get('ROOM_SUNBEAM')
    if sb:   # the sun comes up while the alarm rings: the ray fades in, then stays
        k=max(0.0,min(1.0,(d['F']-66)/22.0)); k=k*k*(3-2*k); sb.data.energy=(110*k) if room else 0
    hz=bpy.data.objects.get('ROOM_HAZE')
    if hz: hz.hide_render=not room
    bpy.data.objects['PHONE_GLOW'].data.energy=0.5 if room else 0
    uo=bpy.data.objects['UW_FILL']; uo.data.energy=5.0 if under else 0
    if under:
        cm=sc.camera.matrix_world; fwd=(cm.to_3x3()@Vector((0,0,-1))).normalized(); uo.rotation_euler=(fwd+Vector((0,0,-0.4))).normalized().to_track_quat('-Z','Y').to_euler()
    bpy.data.objects['GOBO'].hide_render=not under
    for o in bpy.data.objects:
        if o.name.startswith(('GROUND_FAR','TREE_','PALM_FAR','WATER_VOLUME','GRASS_')): o.hide_render=room
    sc.node_tree.nodes['HAZE_AMT'].inputs[1].default_value=0.0 if (room or under) else 0.18
    if d['shot']=='s5' and not under and not room:   # launch look: clear blue morning sky, brighter, less haze
        if 'col0' not in so: so['col0']=list(so.data.color)
        so.data.color=BAG_SUN_COL
        bg.inputs[1].default_value=BAG_SKY_BG; so.data.energy=BAG_SUN_E; sc.node_tree.nodes['HAZE_AMT'].inputs[1].default_value=BAG_HAZE
        if hasattr(sk,'dust_density'): sk.dust_density=BAG_DUST; sk.ozone_density=BAG_OZONE
    elif hasattr(sk,'dust_density'): sk.dust_density=1.0; sk.ozone_density=1.0
    if not (d['shot']=='s5' and not under and not room) and 'col0' in so: so.data.color=so['col0']
    sc.view_settings.exposure=(0.6 if d['shot']=='s1' else (0.85 if d['shot'] in ('s4','s5') else 0.85)) if under else 0.0
    if under and CAM_FIX and 442<=d['F']<=468:   # rising toward the bright surface: hold detail (no milky white-out)
        u_=max(0.0,min(1.0,(d['F']-442)/8.0))*(1.0-max(0.0,min(1.0,(d['F']-462)/6.0))); sc.view_settings.exposure-=RISE_DIM*u_
    if under:   # sky seen through the surface: clear blue overhead with warm sunrise colour, brighter
        sk.sun_elevation=math.radians(11); bg.inputs[1].default_value=0.24
    sb_=bpy.data.materials['MAT_Shrimp'] if 'MAT_Shrimp' in bpy.data.materials else None
    m0=bpy.data.objects['SHRM_000'].data.materials[0]; nn=m0.node_tree.nodes
    healthy=d['shot'] in ('s4','s5')
    if 'SHR_BSDF' in nn: nn['SHR_BSDF'].inputs['Emission Strength'].default_value=0.0 if healthy else 0.03
    if 'SHR_GLOW_STR' in nn: nn['SHR_GLOW_STR'].inputs[1].default_value=SHR_GLOW if healthy else 0.0
    if 'SHR_RIM' in nn: nn['SHR_RIM'].inputs[1].default_value=0.06 if healthy else 0.12
    # packaging teased with light: bag back-lit (silhouette), a narrow warm band of light reveals only the top / logo and creeps down slightly
    br=bpy.data.objects.get('BAG_REVEAL'); jb=bpy.data.objects['JS_BAG']
    if br:
        on=d['shot']=='s5' and not under
        br.data.energy=0.0
        _fl=bpy.data.objects.get('BAG_FLAG')
        if _fl: _fl.hide_render=True
        nf=bpy.data.objects.get('NEG_FILL')
        if nf:
            nf.hide_render=not on
            if on:
                if 'c' not in BAG_TOP:
                    cs=[c.matrix_world@Vector(v) for c in jb.children_recursive if c.type=='MESH' for v in c.bound_box]
                    BAG_TOP['z']=max(v.z for v in cs); BAG_TOP['c']=sum(cs,Vector())/len(cs)
                nf.location=BAG_TOP['c']; nf.rotation_euler=(0,0,0)
        if on:
            F=d['F']; k=max(0.0,min(1.0,(F-468)/14.0)); k=k*k*(3-2*k); slide=max(0.0,min(1.0,(F-470)/70.0))
            top=BAG_TOP.get('z'); 
            if top is None:
                cs=[c.matrix_world@Vector(v) for c in jb.children_recursive if c.type=='MESH' for v in c.bound_box]
                BAG_TOP['z']=max(v.z for v in cs); BAG_TOP['c']=sum(cs,Vector())/len(cs); top=BAG_TOP['z']
            c=BAG_TOP['c']; H=BAG_TOP.setdefault('h',None)
            if H is None:
                cs=[o.matrix_world@Vector(v) for o in jb.children_recursive if o.type=='MESH' for v in o.bound_box]
                BAG_TOP['h']=top-min(v.z for v in cs); BAG_TOP['ymin']=min(v.y for v in cs); H=BAG_TOP['h']
            # warm key from the front-left; a flag between light and bag casts a level shadow line that drops from the top
            # of the pack (100% in shade) to 30% below the top (70% still in shade) by the end of the shot
            br.location=Vector((c.x-0.35,c.y-1.5,top+0.18)); br.rotation_euler=(Vector((c.x,c.y,top-0.3*H))-br.location).to_track_quat('-Z','Y').to_euler()
            br.data.energy=BAG_KEY; br.data.shadow_soft_size=BAG_SOFT   # big source = soft shadow edge
            rev=max(0.0,min(1.0,(F-472)/60.0)); rev=rev*rev*(3-2*rev)
            e=top+0.02-0.32*H*rev                      # height of the shadow edge on the bag face
            face=Vector((c.x,BAG_TOP['ymin'],e)); Lp=br.location; a_=BAG_FLAG_D   # flag distance in front of the bag face (further = softer edge)
            t_=a_/max(1e-4,(face.y-Lp.y)); fz=e+(Lp.z-e)*t_; fy=face.y-a_
            fl=bpy.data.objects.get('BAG_FLAG')
            if fl: fl.hide_render=False; fl.rotation_euler=(math.radians(90),0,0); fl.location=(c.x,fy,fz-0.5)
            if fl and fl.data.materials[0].name!='MAT_FlagScrim':   # scrim, not a solid flag: the shaded lower pack keeps BAG_SCRIM of the key
                m=bpy.data.materials.new('MAT_FlagScrim'); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
                o_=nt.nodes.new('ShaderNodeOutputMaterial'); mx=nt.nodes.new('ShaderNodeMixShader'); tr=nt.nodes.new('ShaderNodeBsdfTransparent'); bk=nt.nodes.new('ShaderNodeBsdfDiffuse')
                bk.inputs['Color'].default_value=(0,0,0,1); mx.inputs[0].default_value=BAG_SCRIM
                nt.links.new(bk.outputs[0],mx.inputs[1]); nt.links.new(tr.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],o_.inputs['Surface'])
                fl.data.materials[0]=m
    bf=bpy.data.objects['BAG_FILL']; f=d['f']; k=max(0,min(1,(f-334)/22.0)); bf.data.energy=0.0*k   # no fill of fill: the bag reads as a back-lit silhouette
    jb=bpy.data.objects['JS_BAG']; bf.location=jb.matrix_world.translation+Vector((0.4,-1.9,0.9)); bf.rotation_euler=(Vector((0,0,0.35))+jb.matrix_world.translation-bf.location).to_track_quat('-Z','Y').to_euler()
SUNROT_OFF=0.0
USE_DOF=False
BAG_WIDEN=0.3
H_OFFSET=json.load(open(S+'bt/h_offset.json')) if os.path.exists(S+'bt/h_offset.json') else {}
SHR_FEED_SPEED=1.6   # healthy/feeding shrimp: livelier swim cycle
RIPPLE_W=0.2; RIPPLE_GAIN=0.015; PEL_UNDER_DARK=0.45   # splash shot: ripple crest visibility, pellet tone under water
RISE_DIM=0.0
BAG_SUN_EL0=3.0; BAG_SUN_EL1=11.5; BAG_SUN_COL=(1.0,0.62,0.32); BAG_SUN_AZ=1.5; BAG_SKY_BG=0.45; BAG_SUN_E=5.5; BAG_HAZE=0.04; BAG_DUST=0.2; BAG_OZONE=4.0   # final pack shot: early-morning clear sky
CAM_FIX=False   # hand-built camera for the farmer orbit and the rise to the pack (camfix.py)
EAT_XY=0.35; EAT_R=0.07   # feeding: pellets reaching a shrimp (or below the shrimp layer) are eaten
LAST_F=541; END_HOLD=48; END_ZOOM=0.16   # 2 s tail after the previs, slow zoom-in on the pack
BAG_SOFT=0.3; BAG_FLAG_D=0.45
BAG_KEY=90.0     # warm key on the pack top
BAG_SCRIM=0.03   # light let through the flag: lower pack 85% dark, not black
SHR_GLOW=0.0   # subtle warm inner glow on the trunk walls (healthy shots)
SHRL_W=0.0   # watts: a subtle inner glow spread through the shell
try: PUSH={'c':Vector(json.load(open(S+'bt/push.json'))['c'])}
except Exception: PUSH={}
PUSH_DIST=0.55; PUSH_MM=38.0; PUSH_HOLD=438
def PUSH_W(F):
    keys=[(0,0),(338,0),(425,1),(438,1),(462,0),(600,0)]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if a<=F<=b: t=(F-a)/(b-a); t=t*t*(3-2*t); return va+(vb-va)*t
    return 0
BAG_TOP={}
try: CAM_SMOOTH=json.load(open(S+'bt/cam_smooth.json'))
except Exception: CAM_SMOOTH={}
try: S1_OFFSET=json.load(open(S+'bt/s1_offset.json'))
except Exception: S1_OFFSET={}
try: S1_BASE=json.load(open(S+'bt/s1_base.json'))
except Exception: S1_BASE={}
try: SHR_HIDE_S1=set(json.load(open(S+'bt/shr_hide_s1.json')))
except Exception: SHR_HIDE_S1=set()
try: SHR_KEEP=set(json.load(open(S+'bt/shr_keep.json')))
except Exception: SHR_KEEP=set(range(999))
def bubbles(d):
    # Real air: a short trail of tiny bubbles behind each pellet that just went in, and a plunge cloud when the
    # camera dives. (The previs scattered ~700 identical bubbles through the whole volume.)
    import random
    F=d['F']; out=[]
    if not d['under'] or F<272: return out
    cam=bpy.context.scene.camera.matrix_world
    import splash as _sp
    age=F-279
    pels={j:ow(e).translation for j,e in enumerate(d['inst']['hi'])}
    if d['shot']=='s3': out+=_sp.cavity(F,pels,S)
    for j,e in enumerate(d['inst']['hi']):
        pa=_sp.cross_age(F,j,S); pa=age if pa is None else pa
        decay=max(0.0,1.0-pa/30.0)
        if decay<=0 or pa<1.0: continue
        p=pels[j]
        if p.z>-0.004: continue
        rr=random.Random(j*7+1); n=int(round(6*decay*rr.uniform(0.5,1.0)))
        for k in range(1,n+1):
            ph=F*0.8+j*2.3+k*1.7; rise=0.0045*k*(1+0.12*pa)
            q=p+Vector((0.0012*math.sin(ph),0.0012*math.cos(ph*1.3),rise))
            if q.z>-0.002: continue
            r=0.00032*rr.uniform(0.6,1.3)*(1-0.08*k)
            out.append(Matrix.Translation(q)@Matrix.Diagonal((r*(1+0.1*math.sin(ph)),r*(1+0.1*math.cos(ph)),r*0.85,1)))
    if 0<=age<16:   # camera plunge
        rr=random.Random(99); f=1.0-age/16.0
        for k in range(int(70*f)+8):
            x=rr.uniform(-1,1); y=rr.uniform(-0.6,0.9); z=rr.uniform(0.14,0.6); r=rr.uniform(0.0004,0.0016)
            loc=cam@Vector((x*z*0.55,y*z*0.4+0.012*age*(0.6+r*500),-z))
            loc.z=min(loc.z+0.004*age,-0.003); ph=F*1.1+k
            out.append(Matrix.Translation(loc)@Matrix.Diagonal((r*(1+0.12*math.sin(ph)),r*(1+0.12*math.cos(ph)),r*0.8,1)))
    return out[:800]
SPLIT=list(range(274,285))+list(range(458,469))   # waterline frames: rendered twice (air / under), joined in post
GRADES={   # lift, gamma, gain per look
 'room':((0.97,0.99,1.05),(1.0,0.99,0.98),(1.05,1.0,0.93)),
 'pond':((0.99,0.99,1.0),(1.0,0.99,0.96),(1.08,1.0,0.90)),
 'under':((0.90,0.93,0.94),(0.97,0.98,0.98),(1.05,1.07,1.06)),   # more contrast: deeper shadows, brighter water
 'bag':((0.99,0.99,1.0),(1.0,0.99,0.98),(1.08,1.03,1.0))}   # brighter, neutral-cool morning (was warm/dark dusk look)
def animate_fx(d):
    import math as _m
    F=d['F']; sc=bpy.context.scene; cam=sc.camera
    gm=bpy.data.materials.get('MAT_Gobo')
    if gm:
        n=gm.node_tree.nodes
        for nd in n:
            if nd.name.startswith('CAUSTIC_H_'): nd.inputs['W'].default_value=F*0.03
        if 'GOBO_SHAFT' in n: n['GOBO_SHAFT'].inputs['W'].default_value=F*0.012
    wm=bpy.data.materials.get('MAT_Pond_Water_Surface')
    if wm:
        for i,sp in enumerate((0.02,0.06,0.12)):
            nd=wm.node_tree.nodes.get('WAVE_%d'%i)
            if nd: nd.inputs['W'].default_value=F*sp
    # depth of field on the close underwater / pellet shots, focused on the subject nearest the view axis
    dof=cam.data.dof; dof.use_dof=False
    if USE_DOF and d['shot']=='s3' and F>=255:   # disabled: focus pulls missed the pellet and blurred the frame
        cm=cam.matrix_world; P=cm.translation; fwd=(cm.to_3x3()@Vector((0,0,-1))).normalized(); best=None
        cands=[o.matrix_world.translation for o in bpy.data.objects if o.name.startswith('PEL_') and not o.hide_render]
        for q in cands:
            v=q-P; dist=v.dot(fwd)
            if dist<0.08: continue
            off=(v-fwd*dist).length/dist
            if off<0.22 and (best is None or dist<best): best=dist
        if best:
            dof.use_dof=True; dof.focus_distance=best; dof.aperture_fstop=2.0 if cam.data.lens>40 else 2.8
    key='room' if d['room'] else ('under' if d['under'] else ('bag' if d['shot']=='s5' else 'pond'))
    g=sc.node_tree.nodes.get('GRADE')
    if g: g.lift,g.gamma,g.gain=GRADES[key]
def fix_set(d):
    # the HF hut replaces the shed: follow the previs shed position, keep the proxy shed + roof hidden
    sh=bpy.data.objects['SET_Farm_Shed']; hut=bpy.data.objects.get('HF_HUT')
    if hut: hut.location=(sh.matrix_world.translation.x,sh.matrix_world.translation.y,sh.matrix_world.translation.z-1.2); hut.hide_render=d['room']
    for n in ('SET_Farm_Shed','SET_Farm_Shed_Roof','POND_Plankton_Specks','PHONE_Ring_Pulse'):   # previs specks read as white balls; MOTES replace them
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
    # the single orange stop button: pops away when the finger presses it
    btn=bpy.data.objects.get('PHONE_Stop_Button')
    if btn and d['shot']=='s2':
        F=d['F']; k=max(0.0,min(1.0,(F-TAP_F)/4.0))
        if k>=1.0: btn.hide_render=True
        elif k>0: btn.matrix_world=btn.matrix_world@Matrix.Scale(1.0-0.85*k*k,4)
    # phone -> pond match cut: start the drone tighter so the pond has the width of the phone screen, then open up
    F=d['F']
    if 118<=F<=146:
        k=(F-118)/28.0; k=k*k*(3-2*k); cam.data.lens*=MATCH_ZOOM*(1-k)+k; cam.data.shift_y=MATCH_SHY*(1-k)
    else: cam.data.shift_y=0.0
TAP_F=101; MATCH_ZOOM=1.35; MATCH_SHY=0.03
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
    F=d['F']; w=PUSH_W(F)
    if w>0 and PUSH.get('c') is not None:
        # push in toward the healthy shrimp; from the hold on, keep that offset while the previs camera rises, fading it out before the surface
        M=cam.matrix_world.copy(); P0=M.translation.copy(); fwd=(M.to_3x3()@Vector((0,0,-1))).normalized()
        tgt=PUSH['c']
        if F<=PUSH_HOLD:
            dirv=(tgt-P0); P1=tgt-dirv.normalized()*PUSH_DIST; P=P0.lerp(P1,w); look=(tgt-P).normalized()
        else:
            if 'off' not in PUSH:
                c0=CAM_SMOOTH.get(str(PUSH_HOLD),None)
                Mh=C@tm(c0[0]) if c0 else M
                ph=Mh.translation; PUSH['off']=(tgt-(tgt-ph).normalized()*PUSH_DIST)-ph
            P=P0+PUSH['off']*w; look=(tgt-P).normalized().lerp(fwd,1-w).normalized()
        f2=fwd.lerp(look,w).normalized()
        q=f2.to_track_quat('-Z','Y'); cam.matrix_world=Matrix.Translation(P)@q.to_matrix().to_4x4(); cam.data.lens=mm*(1-w)+PUSH_MM*w
    import camfix
    pel_=(sum((ow(e).translation for e in d['inst']['hi']),Vector())/len(d['inst']['hi'])) if d['inst']['hi'] else None   # feed-cloud centre
    ov=camfix.override(F,cam,cam.matrix_world.copy(),cam.data.lens,pel_) if CAM_FIX else None
    if ov:
        cam.matrix_world=ov[0]
        if ov[1] is not None: cam.data.lens=ov[1]
        if 440<=F<=490 and not d.get('force') and not d['room']: d['under']=cam.matrix_world.translation.z<0.0
        if 262<=F<=332 and not d.get('force') and not d['room']: d['under']=cam.matrix_world.translation.z<0.0   # pellet ride crosses the surface with the pellet
    if d['shot']=='s5' and F>=455:   # final bag shot: open the frame up a little (more air around the pack)
        kk=max(0.0,min(1.0,(F-455)/15.0)); kk=kk*kk*(3-2*kk); cam.data.lens*=1.0-BAG_WIDEN*kk
    if F>LAST_F:   # extra 2 s at the end: a very slow push into the pack (eases in from the stopped camera)
        u=min(1.0,(F-LAST_F)/float(END_HOLD)); cam.data.lens*=1.0+END_ZOOM*u*u*(3-2*u)
    cz=cam.matrix_world.translation.z
    fo=d.get('force')
    if fo=='air':      # above-water half of a waterline (split) frame
        d['under']=False; t=cam.matrix_world.copy(); t.translation.z=max(cz,0.008); cam.matrix_world=t
    elif fo=='under' or d['under'] or (not d['room'] and cz<0.004):   # never sit in the thin layer between the volume top and the surface
        d['under']=True; t=cam.matrix_world.copy(); t.translation.z=min(cz,-0.018); cam.matrix_world=t
    cam.data.clip_start=0.005 if d['room'] or d['under'] else 0.03; cam.data.clip_end=2000
    set_mode(d)
    fix_set(d)
    animate_fx(d)
    # client shrimp
    for si,(rig,(v,m,t)) in enumerate(zip(shrimp.rigs,d['shr'])):
        on=bool(v) and ((d['F']<279 and si not in SHR_HIDE_S1) or (d['F']>=279 and si in SHR_KEEP)); rig.hide_render=not on
        for ch in rig.children: ch.hide_render=not on
        sl=bpy.data.objects.get(rig.name.replace('SHR_','SHRL_'))
        if sl: sl.data.energy=SHRL_W if (on and d['shot'] in ('s4','s5') and d['under']) else 0.0
        if on:
            F=d['F']
            if F<61 and str(si) in S1_BASE:
                # tired shrimp: suspended a few cm above the bottom, drifting slowly with the water, gentle bob/sway, no turning
                import random as _r
                rr=_r.Random(si); M=ow(S1_BASE[str(si)])
                lift=rr.uniform(0.03,0.09); ph=rr.uniform(0,6.28)
                dx=0.0006*F+0.004*math.sin(F*0.03+ph); dz=lift+0.007*math.sin(F*0.09+ph)
                sway=Matrix.Rotation(math.radians(3.0*math.sin(F*0.05+ph)),4,'Z')
                loc=M.translation+Vector((dx,0.0,dz))+Vector(S1_OFFSET.get(str(si),(0,0,0))); R=M.to_3x3().to_4x4()   # per-shrimp nudge so none sit glued together
                rig.matrix_world=Matrix.Translation(loc)@sway@R
                shrimp.pose(rig,F/24.0*0.55+(si*0.731)%7.0)   # tired: 55% speed, each shrimp at its own phase
            else:
                rig.matrix_world=Matrix.Translation(Vector(H_OFFSET.get(str(si),(0,0,0))))@ow(m); shrimp.pose(rig,F/24.0*(SHR_FEED_SPEED if d['shot'] in ('s4','s5') else 1.0)+(si*0.731)%7.0)   # feeding shrimp move faster; own phase; nudged so none overlap on screen
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
    if d['under'] and d['shot'] in ('s4','s5'):   # healthy shrimp eat everything: no pellet gets past the shrimp line
        R=[r.matrix_world.translation for r in shrimp.rigs if not r.hide_render]
        if R:
            zmin=sorted(r.z for r in R)[len(R)//2]   # away from any shrimp: the middle of the shrimp layer
            for q in pool[:j]:
                p_=q.matrix_world.translation; near=[r for r in R if (r.x-p_.x)**2+(r.y-p_.y)**2<EAT_XY**2]
                line=(min(r.z for r in near) if near else zmin)
                if p_.z<line-0.01 or any(p_.z<r.z+0.03 and (r-p_).length<EAT_R for r in near): q.hide_render=True
    mo=bpy.data.objects.get('MOTES')
    if mo: mo.hide_render=not d['under']; mo.location=(0.0006*d['F'],0.0002*d['F'],0.0004*d['F'])
    crowns=[o for o in bpy.data.objects if o.name.startswith('CROWN_')]; nc=0
    if crowns:
        import splash as _sp; _sp.smooth_crown(crowns[0].data)
    rmat=bpy.data.materials.get('MAT_Ripple')
    if rmat and not rmat.get('water_ok'):   # ripple crests: clear refracting water (was a dark fresnel line)
        b_=[x for x in rmat.node_tree.nodes if x.type=='BSDF_PRINCIPLED'][0]
        b_.inputs['Base Color'].default_value=(0.9,0.97,0.94,1); b_.inputs['Transmission Weight'].default_value=1.0
        b_.inputs['Roughness'].default_value=0.03; b_.inputs['IOR'].default_value=1.333; rmat['water_ok']=1
        for x in rmat.node_tree.nodes:
            if x.type=='MATH' and x.operation=='MULTIPLY' and abs(x.inputs[1].default_value-1.0)<1e-6 and not x.inputs[1].links: x.inputs[1].default_value=RIPPLE_W
    pm_=bpy.data.objects['PEL_000'].active_material
    if pm_ and pm_.use_nodes:   # same brown pellet above and below the surface (under water it read beige)
        rp_=[x for x in pm_.node_tree.nodes if x.type=='VALTORGB']
        if rp_:
            k_=PEL_UNDER_DARK if d['under'] else 1.0; e_=rp_[0].color_ramp.elements
            e_[0].color=(0.13*k_,0.07*k_,0.035*k_,1); e_[1].color=(0.30*k_,0.18*k_,0.09*k_,1)
    wmat=bpy.data.materials.get('MAT_Pond_Water_Surface')
    if wmat:
        import splash as _sp
        _sp.build_ripples(wmat); _sp.set_ripples(wmat,d['F'],bpy.context.scene.camera.matrix_world.translation,S,RIPPLE_GAIN if d['shot']=='s3' else 0.0)
    sp_drops=sp_crowns=None
    if d['shot']=='s3' and not d['under']:
        import splash as _sp
        sp_drops,sp_crowns=_sp.splash(d['F'],bpy.context.scene.camera.matrix_world.translation,S)
    for kind,key,n in (('BUB','bub',800),('DROP','drop',900),('RING','ring',400)):
        L=bubbles(d) if kind=='BUB' else (sp_drops if (kind=='DROP' and sp_drops is not None) else d['inst'][key])
        if kind=='RING' and d['shot']=='s3': L=[]   # s3 ripples live in the water surface shader now
        for i in range(n):
            o=bpy.data.objects.get('%s_%03d'%(kind,i))
            if o is None: break
            if i<len(L):
                M=L[i] if (kind=='BUB' or (kind=='DROP' and sp_drops is not None)) else ow(L[i])
                if kind=='RING':   # ripples fade as they spread; a crown rises on the youngest ones
                    sr=Vector((L[i][0],L[i][1],L[i][2])).length; f=max(0.0,min(1.0,1.15-(sr-0.003)/0.006)); o.color=(f,f,f,1)
                    a=(sr-0.0028)/0.0018
                    if sp_crowns is None and a<1.0 and nc<len(crowns):
                        h=0.009*max(0.0,math.sin(math.pi*max(0.0,min(1.0,a*0.85+0.15))))
                        if h>0.0006:
                            cr=crowns[nc]; cr.matrix_world=M@Matrix.Diagonal((0.9,0.9,h,1)); cr.hide_render=False; nc+=1
                o.matrix_world=M; o.hide_render=False
            else: o.hide_render=True
    if sp_crowns:
        for M in sp_crowns:
            if nc>=len(crowns): break
            crowns[nc].matrix_world=M; crowns[nc].hide_render=False; nc+=1
    for cr in crowns[nc:]: cr.hide_render=True
