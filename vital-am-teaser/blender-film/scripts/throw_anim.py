# Natural feed throw: FK poses keyed per bone, time-aware cubic Hermite (no stop-and-go),
# kinetic-chain lag (torso leads, upper arm, forearm, wrist follow).
import math
# bone: list of (frame, (x,y,z) degrees). Axes measured on this rig (farmer faces -Y):
#  Spine X+ bend forward, Y+ twist right shoulder forward, Z+ side-bend to his right
#  Arm X+ raise forward, Z- raise sideways; ForeArm X+ bend elbow; Head X+ look down, Y turn
# arms hang along the body at RightArm Z=+25 / LeftArm Z=-25 (model comes in A-pose)
IDLE={'Hips':(0,0,0),'Spine01':(3,0,0),'Spine02':(2,0,0),'RightArm':(8,0,22),'RightForeArm':(42,0,0),'RightHand':(0,0,0),
      'LeftArm':(5,0,-24),'LeftForeArm':(12,0,0),'Head':(6,0,0),'neck':(2,0,0)}
DIP={'Hips':(40,-8,0),'Spine01':(10,-6,12),'Spine02':(4,-4,3),'RightArm':(45,0,25),'RightForeArm':(20,0,0),'RightHand':(-10,0,0),
     'LeftArm':(20,0,-18),'LeftForeArm':(25,0,0),'Head':(-8,-8,0),'neck':(-4,0,0)}
LIFT={'Hips':(16,-10,0),'Spine01':(4,-10,2),'Spine02':(2,-8,0),'RightArm':(25,0,18),'RightForeArm':(55,0,0),'RightHand':(0,0,0),
      'LeftArm':(10,0,-20),'LeftForeArm':(18,0,0),'Head':(2,-6,0),'neck':(1,0,0)}
WIND={'Hips':(4,-18,0),'Spine01':(2,-16,0),'Spine02':(0,-10,0),'RightArm':(-32,0,20),'RightForeArm':(25,0,0),'RightHand':(15,0,0),
      'LeftArm':(25,0,-16),'LeftForeArm':(30,0,0),'Head':(0,12,0),'neck':(0,6,0)}
REL={'Hips':(8,14,0),'Spine01':(6,12,0),'Spine02':(3,8,0),'RightArm':(98,0,8),'RightForeArm':(8,0,0),'RightHand':(-20,0,0),
     'LeftArm':(-18,0,-20),'LeftForeArm':(20,0,0),'Head':(-6,-8,0),'neck':(-2,-4,0)}
FOLLOW={'Hips':(10,22,0),'Spine01':(8,18,0),'Spine02':(4,12,0),'RightArm':(112,0,16),'RightForeArm':(14,0,0),'RightHand':(-28,0,0),
        'LeftArm':(-22,0,-18),'LeftForeArm':(18,0,0),'Head':(-4,-10,0),'neck':(-2,-4,0)}
SETTLE={'Hips':(3,6,0),'Spine01':(3,4,0),'Spine02':(2,3,0),'RightArm':(45,0,18),'RightForeArm':(45,0,0),'RightHand':(-6,0,0),
        'LeftArm':(4,0,-24),'LeftForeArm':(12,0,0),'Head':(3,-4,0),'neck':(1,0,0)}
KEYS=[(0,IDLE),(196,IDLE),(205,DIP),(209,DIP),(214,LIFT),(219,WIND),(224,REL),(231,FOLLOW),(246,SETTLE),(266,IDLE),(600,IDLE)]
LAG={'Hips':-1.5,'Spine01':-1.0,'Spine02':-0.5,'neck':0.0,'Head':0.5,'RightArm':0.5,'RightForeArm':1.5,'RightHand':2.5,'LeftArm':1.0,'LeftForeArm':2.0}
def _hermite(ts,vs,t):
    n=len(ts)
    if t<=ts[0]: return vs[0]
    if t>=ts[-1]: return vs[-1]
    i=max(k for k in range(n-1) if ts[k]<=t)
    t0,t1=ts[i],ts[i+1]; p0,p1=vs[i],vs[i+1]
    def slope(k):
        if k==0 or k==n-1: return 0.0
        a=(vs[k]-vs[k-1])/(ts[k]-ts[k-1]); b=(vs[k+1]-vs[k])/(ts[k+1]-ts[k])
        if a*b<=0: return 0.0          # flatten at extremes: no overshoot, natural hold at dip/peak
        return 2*a*b/(a+b)             # harmonic mean (monotone, Fritsch-Carlson)
    m0,m1=slope(i),slope(i+1); h=t1-t0; s=(t-t0)/h
    h00=2*s**3-3*s**2+1; h10=s**3-2*s**2+s; h01=-2*s**3+3*s**2; h11=s**3-s**2
    return h00*p0+h10*h*m0+h01*p1+h11*h*m1
def pose_at(F):
    out={}
    ts=[k[0] for k in KEYS]
    for b in IDLE:
        t=F-LAG.get(b,0.0)
        out[b]=tuple(math.radians(_hermite(ts,[k[1][b][c] for k in KEYS],t)) for c in range(3))
    # breathing / weight micro-motion so the idle is never frozen
    br=math.sin(F/24*2*math.pi*0.25)
    s=list(out['Spine02']); s[0]+=math.radians(0.8*br); out['Spine02']=tuple(s)
    return out
def hip_drop(F):
    # hips lower (cm, bone units) when bending to the bucket and loading into the throw
    ts=[k[0] for k in KEYS]; vs={0:0,196:0,205:-30,209:-30,214:-12,219:-4,224:-3,231:-4,246:-1,266:0,600:0}
    return _hermite(ts,[vs[t] for t in ts],F-1.5)
def root_offset(F):
    # weight shifts forward (-Y) into the throw and back
    ts=[0,214,219,225,236,260,600]; vs=[0,0,0.04,-0.07,-0.05,0,0]
    return _hermite(ts,vs,F)
# ---- right arm by IK: hand target + explicit elbow pole, in the farmer's root frame
# (x: + = his left, -X = his right; y: -Y = forward; z: up from the feet)
HAND={0:(-0.24,-0.20,0.92),196:(-0.24,-0.20,0.92),205:(-0.42,-0.24,0.44),209:(-0.42,-0.24,0.42),214:(-0.33,-0.16,0.82),
      219:(-0.40,0.26,0.92),224:(-0.36,-0.50,1.16),231:(-0.04,-0.64,1.24),246:(-0.22,-0.36,1.00),266:(-0.24,-0.20,0.92),600:(-0.24,-0.20,0.92)}
POLE={0:(-0.34,0.30,0.95),196:(-0.34,0.30,0.95),205:(-0.70,0.05,0.85),209:(-0.70,0.05,0.85),214:(-0.55,0.25,0.95),
      219:(-0.40,0.65,1.05),224:(-0.62,-0.05,0.95),231:(-0.40,-0.20,0.90),246:(-0.38,0.20,0.85),266:(-0.34,0.30,0.95),600:(-0.34,0.30,0.95)}
def _vec_at(D,F,lag):
    ts=sorted(D); return tuple(_hermite(ts,[D[t][c] for t in ts],F-lag) for c in range(3))
def hand_target(F): return _vec_at(HAND,F,1.0)
def elbow_pole(F): return _vec_at(POLE,F,1.0)
