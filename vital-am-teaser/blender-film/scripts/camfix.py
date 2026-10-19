# Hand-built camera moves replacing two previs passages:
#  A (140-262) drone crane-down onto the farmer, one continuous ~110 deg orbit ending over his right shoulder,
#              then over the shoulder toward the landing pellets, handing back to the previs pellet shot at 262.
#  B (440-490) from the healthy shrimp, one diagonal rise toward the dock/bag, breaching the surface with the
#              pack centred, carrying the same momentum into the previs bag shot.
import math
from mathutils import Vector, Matrix, Quaternion
FARMER=Vector((0.0,9.82,1.05)); BAG=Vector((0.22,9.5,0.55)); LAND=Vector((0.35,5.6,0.25))
def _ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def _cr(keys,F):
    """time-aware Catmull-Rom through (frame, value) keys; values are Vectors or floats; no per-key easing (no stop-and-go)"""
    ts=[k[0] for k in keys]
    if F<=ts[0]: return keys[0][1]
    if F>=ts[-1]: return keys[-1][1]
    i=max(j for j in range(len(ts)-1) if ts[j]<=F)
    t0,t1=ts[i],ts[i+1]; p0,p1=keys[i][1],keys[i+1][1]
    def tan(j):
        if j==0 or j==len(ts)-1: return p1*0 if not isinstance(p1,float) else 0.0
        return (keys[j+1][1]-keys[j-1][1])/(ts[j+1]-ts[j-1])
    m0,m1=tan(i),tan(i+1); h=t1-t0; s=(F-t0)/h
    h00=2*s**3-3*s**2+1; h10=s**3-2*s**2+s; h01=-2*s**3+3*s**2; h11=s**3-s**2
    return p0*h00+m0*(h*h10)+p1*h01+m1*(h*h11)
def _look(P,T,roll=0.0):
    f=(T-P).normalized(); q=f.to_track_quat('-Z','Y')
    if roll: q=q@Quaternion((0,0,1),roll)
    return Matrix.Translation(P)@q.to_matrix().to_4x4()
def _drift(F,amp_p=0.006,amp_a=0.0012):
    # gentle gimbal float: a few incommensurate sines
    dp=Vector((math.sin(F*0.071)+0.5*math.sin(F*0.173+1.1),math.sin(F*0.063+2.0)+0.5*math.sin(F*0.151),math.sin(F*0.089+0.7)*0.7))*amp_p
    da=Vector((math.sin(F*0.057+0.3),math.sin(F*0.081+1.7),0))*amp_a
    return dp,da
# ---- A: crane + orbit + over-the-shoulder
def _orbit(phi,R,h): return FARMER+Vector((R*math.cos(math.radians(phi)),R*math.sin(math.radians(phi)),h-FARMER.z))
POS_A=[(140,Vector((0.005,0.14,58.5))),(152,Vector((-0.05,0.4,50.0))),(164,Vector((-0.35,1.6,32.0))),(176,Vector((-0.8,3.5,15.0))),
       (188,Vector((-1.35,5.4,6.2))),(198,Vector((-1.62,6.45,2.75)))]
# orbit from front-right (phi=-110) through his right profile (phi=-180) to behind the right shoulder (phi=-215)
for F in range(206,250,4):
    u=_ease((F-200)/50.0); phi=-118-90*u; R=3.5-1.5*u; h=2.0-0.05*u
    POS_A.append((F,_orbit(phi,R,h)))
# then chase the feed out over the water and come down to the waterline where the hero pellet lands (previs from ~274)
POS_A+= [(254,Vector((-0.8,9.4,2.1))),(262,Vector((-0.12,7.45,1.75))),(270,Vector((0.39,5.9,0.96))),(278,Vector((0.49,5.51,-0.018)))]
TGT_A=[(140,Vector((0.0,1.2,0.0))),(156,Vector((0.0,4.0,0.0))),(172,Vector((0.0,7.6,0.3))),(196,FARMER+Vector((0,0,0.15))),
       (218,FARMER+Vector((0,-0.3,0.1))),(250,Vector((0.2,7.0,1.2))),(262,Vector((1.0,3.2,1.25))),(276,Vector((0.49+0.537*3,5.51-0.799*3,-0.018-0.27*3)))]   # past 244 the target is the hero pellet itself
LENS_A=[(140,25.0),(180,24.0),(200,26.0),(240,28.0),(262,38.0),(272,50.0)]
def cam_A(F,pel=None):
    P=_cr(POS_A,F); T=_cr(TGT_A,F); L=_cr(LENS_A,F)
    if pel is not None and F>246: T=T.lerp(pel,0.6*_ease((F-246)/8.0)*(1.0-_ease((F-254)/6.0)))   # lean toward the feed cloud, never lock on a single pellet
    dp,da=_drift(F,0.012 if F<200 else 0.006)
    M=_look(P+dp,T+da*((T-P).length))
    return M,L
# ---- B: rise from the shrimp to the pack
POS_B=[(440,None),(448,Vector((0.0,5.32,-0.66))),(456,Vector((-0.02,5.38,-0.36))),(462,Vector((0.0,5.46,-0.08))),
       (466,Vector((0.03,5.56,0.06))),(474,Vector((0.08,5.78,0.17))),(482,Vector((0.13,6.0,0.25))),(490,Vector((0.2,6.2,0.31)))]
TGT_B=[(440,None),(450,BAG+Vector((0,0,0.35))),(470,BAG+Vector((0,0,0.1))),(490,BAG)]
def cam_B(F,M0):
    P0=M0.translation.copy(); f0=(M0.to_3x3()@Vector((0,0,-1))).normalized()
    pk=[(f,(v if v is not None else P0)) for f,v in POS_B]; tk=[(f,(v if v is not None else P0+f0*3.0)) for f,v in TGT_B]
    P=_cr(pk,F); T=_cr(tk,F); dp,da=_drift(F,0.004)
    return _look(P+dp,T+da*((T-P).length))
def override(F,cam,prev_M,prev_L,pel=None):
    """returns (matrix, lens|None) or None; blends in/out of the previs camera"""
    if 140<=F<=276:
        M,L=cam_A(F,pel); w=_ease((F-140)/6.0)*(1.0-_ease((F-268)/8.0))
        return _blend(prev_M,M,w),prev_L+(L-prev_L)*w
    if 440<=F<=490:
        M=cam_B(F,_look(B_ANCHOR,B_ANCHOR+B_ANCHOR_DIR))
        w=_ease((F-440)/8.0)*(1.0-_ease((F-484)/6.0))
        return _blend(prev_M,M,w),None
    return None
B_ANCHOR=Vector((0.064,5.262,-0.786)); B_ANCHOR_DIR=Vector((0.725,0.669,0.165))   # push-in camera at its hold (frame ~438)
def _blend(A,B,w):
    if w<=0: return A
    if w>=1: return B
    qa=A.to_quaternion(); qb=B.to_quaternion(); P=A.translation.lerp(B.translation,w)
    return Matrix.Translation(P)@qa.slerp(qb,w).to_matrix().to_4x4()
