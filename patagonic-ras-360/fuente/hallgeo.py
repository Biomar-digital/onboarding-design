# Hall geometry taken from the floor plan (image px -> metres via the 26.4 m dimension line).
# x = east, y = north, z = up; origin at the front banner.
import numpy as np, math
PX=26.4/350.0
def m(X,Y): return np.array([(X-761)*PX, -(Y-229)*PX])
# name, plan endpoints (image px), point on the public side, width, height, bottom height, resolution
SCREENS=[
 ('banner_frontal',  (761,190),(761,268), (800,229), 4.0,1.0, 3.0, (1344,366)),
 ('totem_N1',        (845,189),(869,189), (857,229), 1.0,3.0, 0.0, (336,1008)),
 ('totem_N2',        (902,189),(926,189), (914,229), 1.0,3.0, 0.0, (336,1008)),
 ('totem_N3',        (969,189),(993,189), (981,229), 1.0,3.0, 0.0, (336,1008)),
 ('totem_N4',        (1031,189),(1055,189),(1043,229),1.0,3.0, 0.0, (336,1008)),
 ('concava',         (1072,184),(1116,248),(1040,240),6.0,5.0, 0.3, (2016,1680)),
 ('cocina',          (1342,380),(1416,325),(1300,330),4.0,2.0, 1.5, (1344,672)),
 ('totem_R1',        (1207,397),(1243,420),(1205,455),1.0,2.0, 0.0, (336,672)),
 ('totem_R2',        (1222,505),(1245,472),(1205,455),1.0,2.0, 0.0, (336,672)),
 ('banner_lateral',  (782,274),(962,274), (872,240), 8.0,1.0, 3.0, (2688,336)),
]
EYE_H=1.7
def screen(s):
    name,a,b,inside,W,H,z0,res=s
    A,B=m(*a),m(*b); c=(A+B)/2; t=(B-A)/np.linalg.norm(B-A)
    n=np.array([-t[1],t[0]]);
    if np.dot(m(*inside)-c,n)<0: n=-n                       # n points to the public side
    zc=z0+H/2
    D=max(4.0,1.1*max(W,H))                                  # viewer stands D metres in front of the screen
    eye=np.array([c[0]+n[0]*D,c[1]+n[1]*D,EYE_H])
    return dict(name=name,c=np.array([c[0],c[1],zc]),t=np.array([t[0],t[1],0.0]),n=np.array([n[0],n[1],0.0]),W=W,H=H,res=res,eye=eye,D=D)
SC=[screen(s) for s in SCREENS]
# swim circuit: 3.5 m behind each screen (inside the water), in this order, closed loop, smoothed
ORDER=['banner_frontal','totem_N1','totem_N2','totem_N3','totem_N4','concava','cocina','totem_R2','totem_R1','banner_lateral']
BEHIND=3.5
def circuit(n=2000):
    by={s['name']:s for s in SC}
    pts=[]; cs=[by[k]['c'] for k in ORDER]
    for i,k in enumerate(ORDER):
        s=by[k]; d=cs[(i+1)%len(cs)]-cs[i-1]; t=s['t'] if np.dot(s['t'],d)>=0 else -s['t']   # travel direction along the screen
        h=max(s['W']/2,1.0); z=min(max(s['c'][2],1.2),3.6)
        for u in (-h,h):                                   # two points: the path runs parallel behind every screen
            p=s['c']-s['n']*BEHIND+t*u; p=p.copy(); p[2]=z; pts.append(p)
    P=np.array(pts); N=len(P)
    # closed Catmull-Rom
    out=[]
    for i in range(N):
        p0,p1,p2,p3=P[i-1],P[i],P[(i+1)%N],P[(i+2)%N]
        for u in np.linspace(0,1,n//N,endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u**3))
    C=np.array(out); seg=np.linalg.norm(np.diff(np.vstack([C,C[:1]]),axis=0),axis=1); L=seg.sum()
    s=np.concatenate([[0],np.cumsum(seg)])
    return C,s,L
