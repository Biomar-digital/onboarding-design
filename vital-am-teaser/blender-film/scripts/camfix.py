# Hand-built camera moves replacing two previs passages.
#  A (140-276) ONE continuous move: fast drone dive that decelerates as it reaches the farmer, carries the same momentum
#              into a full 360 orbit around him (ending behind him as he throws), then rides with the hero pellet
#              and hands back to the previs pellet ride at the waterline.
#  B (440-496) slow vertical rise from the shrimp toward the light; only after breaching it turns gently to the pack.
import math, json, os
from mathutils import Vector, Matrix, Quaternion
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
FARMER=Vector((0.0,9.82,1.05)); BAG=Vector((0.22,9.5,0.55))
def _ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def _look(P,T):
    return Matrix.Translation(P)@(T-P).normalized().to_track_quat('-Z','Y').to_matrix().to_4x4()
def _blend(A,B,w):
    if w<=0: return A
    if w>=1: return B
    return Matrix.Translation(A.translation.lerp(B.translation,w))@A.to_quaternion().slerp(B.to_quaternion(),w).to_matrix().to_4x4()
def _bez(p0,p1,p2,p3,t): u=1-t; return p0*u*u*u+p1*3*u*u*t+p2*3*u*t*t+p3*t*t*t
# ---------------- A ----------------
RIDE_FAR=1.4; RIDE_NEAR=0.12   # pellet ride distance (m)
R_ORB=2.4; H_ORB=1.85; PHI0=math.radians(-90)   # in front of him, over the water
F0,F1,F2,F3=140,178,232,332          # dive start, orbit start (behind him), orbit end (360 later), hand-off
W0,W1=0.150,0.082                    # orbit angular speed (rad/frame): enters fast, eases down; integral = 2*pi
def _omega(F): return W0+(W1-W0)*_ease((F-F1)/(F2-F1))
_TOT=sum(_omega(F1+(i+0.5)*(F2-F1)/400.0) for i in range(400))*(F2-F1)/400.0
def _orbit_phi(F):
    F=max(F1,min(F2,F)); n=max(1,int((F-F1)*8)); dt=(F-F1)/n
    acc=sum(_omega(F1+(i+0.5)*dt) for i in range(n))*dt
    return PHI0+2*math.pi*acc/_TOT
def _orbit_pos(phi,F):
    h=H_ORB+0.12*math.sin(phi*1.0)       # a gentle rise and fall around him
    return FARMER+Vector((R_ORB*math.cos(phi),R_ORB*math.sin(phi),h-FARMER.z))
# dive: cubic bezier from the hovering drone to the orbit entry, arriving tangent to the orbit (moving -X behind him)
D_P0=Vector((0.005,0.14,58.5)); D_P3=_orbit_pos(PHI0,F1)
D_P1=D_P0.lerp(D_P3,0.35); D_P2=D_P3+Vector((-1.1,-0.25,1.4))   # straight line; bends only into the orbit tangent at the end
def _bez_len_param(F):
    # speed profile: from the hover (~0.3 m/f) up to a fast dive and down to the orbit entry speed (R*W0), arc-length based
    import functools
    samples=[_bez(D_P0,D_P1,D_P2,D_P3,i/400) for i in range(401)]
    cum=[0.0]
    for i in range(400): cum.append(cum[-1]+(samples[i+1]-samples[i]).length)
    L=cum[-1]; T=F1-F0; v0=0.3; v1=R_ORB*W0
    A=2.0*(L-T*(v0+v1)/2.0)/T
    t=(F-F0)/T; s=T*(v0*t+(v1-v0)*t*t/2.0)+A*T*(t/2.0-math.sin(2*math.pi*t)/(4*math.pi))
    s=max(0.0,min(L,s)); k=max(i for i in range(401) if cum[i]<=s)
    if k>=400: return samples[400]
    f=(s-cum[k])/max(1e-9,cum[k+1]-cum[k]); return samples[k].lerp(samples[k+1],f)
TR=json.load(open(S+'bt/hero_pellet.json')) if os.path.exists(S+'bt/hero_pellet.json') else {}
REL=Vector((-0.36,9.32,1.25)); F_REL=218.0
TR_TO=320
TR_FROM=254   # previs 'hi[0]' is the same pellet only from here on (it swaps identity before)
CLOUD=json.load(open(S+'bt/feed_cloud.json')) if os.path.exists(S+'bt/feed_cloud.json') else {}
def _cloud(F):
    ks=sorted(int(k) for k in CLOUD); F=max(ks[0],min(ks[-1],F)); i=int(F); j=min(ks[-1],i+1)
    return Vector(CLOUD[str(i)]).lerp(Vector(CLOUD[str(j)]),F-i)
def _track(F):
    last=min(TR_TO,max(int(k) for k in TR))
    if F>=last:   # previs swaps the hi[0] identity after this: keep sinking at the last velocity
        a=Vector(TR[str(last)]); b=Vector(TR[str(last-4)]); return a+(a-b)/4.0*(F-last)
    if F>=TR_FROM:
        a=Vector(TR[str(int(F))]); b=Vector(TR.get(str(int(F)+1),TR[str(int(F))])); return a.lerp(b,F-int(F))
    a=Vector(TR[str(TR_FROM)]); v=Vector(TR[str(TR_FROM+1)])-a; return a+v*(F-TR_FROM)
def hero(F):
    """what the camera follows: the real feed cloud leaving the scoop, handing over to the hero pellet as it separates"""
    return _cloud(F).lerp(_track(F),_ease((F-244)/12.0))
def cam_A(F,prev_M=None):
    if F<F1:
        P=_bez_len_param(F); k=_ease((F-F0)/(F1-F0))
        T=(P+Vector((0,0.3,-10))).lerp(FARMER+Vector((0,0,0.2)),k)       # looking down the drop, then straight at him
        return _look(P,T),25.0
    phi=_orbit_phi(min(F,F2))
    if F>F2: x_=min(F-F2,12.0); phi+=W1*(x_-x_*x_/24.0)   # keeps the orbit's last angular speed and lets it die out
    P=_orbit_pos(phi,F)
    k=_ease((F-214)/24.0); tgt=(FARMER+Vector((0,0,0.1))).lerp(hero(F),k)
    if F>=F_REL:
        # ride with the pellet from in front of it: it flies toward the lens with the farmer behind it, down to the water
        h=hero(F); Fv=max(230.0,min(F,266.0)); v=hero(Fv+3)-hero(Fv-3); vh=Vector((v.x,v.y,0)); dh=vh.normalized() if vh.length>1e-6 else Vector((0,-1,0))
        ahead=2.4+(0.30-2.4)*_ease((F-224)/16.0)+(RIDE_NEAR-0.30)*_ease((F-248)/14.0)   # dives into the feed spray, then locks on the hero pellet (macro)
        P_ride=h+dh*ahead+Vector((0,0,0.03))
        P=P.lerp(P_ride,_ease((F-222)/14.0))
    L=25.0+1.0*_ease((F-F1)/20.0)+20.0*_ease((F-232)/26.0)
    return _look(P,tgt),L
# ---------------- B ----------------
B_P500=Vector((0.312,6.597,0.373)); B_ANCHOR=Vector((0.064,5.262,-0.786)); B_ANCHOR_DIR=Vector((0.725,0.669,0.165)).normalized()
def cam_B(F,M0=None):
    u=_ease((F-440)/44.0); z=B_ANCHOR.z+(0.36-B_ANCHOR.z)*u        # straight up, slowly; breaks the surface ~F463
    P=Vector((B_ANCHOR.x,B_ANCHOR.y,z))
    u2=max(0.0,min(1.0,(F-462)/38.0)); s2=-0.73*u2**3+1.73*u2**2        # ease in, leave at the previs dolly speed
    P=P+Vector((B_P500.x-B_ANCHOR.x,B_P500.y-B_ANCHOR.y,0))*s2
    hd=Vector((B_ANCHOR_DIR.x,B_ANCHOR_DIR.y,0)).normalized()
    pitch=math.radians(10+30*_ease((F-440)/16.0)-30*_ease((F-458)/12.0))   # tilt up toward the light, level out at the surface
    turn=_ease((F-466)/26.0)                                              # only after the breach: turn to the pack
    tobag=(BAG-P); hb=Vector((tobag.x,tobag.y,0)).normalized(); h2=hd.lerp(hb,turn).normalized()
    pitch=pitch*(1-turn)+math.atan2(BAG.z+0.1-P.z,Vector((tobag.x,tobag.y)).length)*turn
    f=Vector((h2.x*math.cos(pitch),h2.y*math.cos(pitch),math.sin(pitch)))
    return _look(P,P+f)
RISE_ON=False   # the client kept the original previs rise to the pack
def override(F,cam,prev_M,prev_L,pel=None):
    if F0<=F<=F3:
        M,L=cam_A(F,prev_M); w=_ease((F-F0)/6.0)   # rides the pellet down to the cut at 333
        return _blend(prev_M,M,w),prev_L+(L-prev_L)*w
    if RISE_ON and 440<=F<=500:
        M=cam_B(F); w=_ease((F-440)/6.0)*(1.0-_ease((F-494)/6.0))
        return _blend(prev_M,M,w),None
    return None
