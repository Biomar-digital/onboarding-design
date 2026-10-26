# Verifies over the whole minute that no fish (near/mid layers + loners) enters a screen's visible pyramid
# closer than 0.45 m behind the glass, and that the correction has no jumps.
import numpy as np, math
import hallgeo as hg
from school import simulate
src=open('hall.py').read(); ns={'np':np,'hg':hg,'math':math}
exec(src[src.index('def keep_behind_glass'):src.index('NT=sum(p[5] for p in plan);')],ns)
exec(src[src.index('def lead_fn'):src.index('random.seed(11)')].replace('T0','0.0'),ns)
LAYERS=ns['LAYERS']; lead_fn=ns['lead_fn']; kbg=ns['keep_behind_glass']
def inpyr(s,P,margin):
    c,n,t=s['c'],s['n'],s['t']; e=s['eye']; D=s['D']; rel=P-e; along=rel@(-n); d=along-D
    ox=rel@t-((c-e)@t)*along/D; oz=rel[...,2]-(c[2]-e[2])*along/D
    m=(along>0.05)&(np.abs(ox)<(s['W']/2+0.4)*along/D)&(np.abs(oz)<(s['H']/2+0.4)*along/D)&(d<margin)
    return m,d
F=1440; rng=np.random.default_rng(3); plan=[]
for name,beh,dz,sgn,schools,spr in LAYERS:
    C,S_,LEN=hg.circuit(behind=beh,dz=dz)
    for n_,ph in schools: plan.append((name,C,S_,LEN,ph,sgn,n_,spr,0.25,1))
for k in range(12):
    C,S_,LEN=hg.circuit(behind=float(rng.uniform(1.8,9.0)),dz=float(rng.uniform(-1.0,1.2)))
    plan.append(('suelto',C,S_,LEN,float(rng.uniform(0,90)),1 if k%3 else -1,1,1.0,0.6,1))
for beh,dz,ns_,ph,sgn,spr in ((2.6,0.0,14,0.0,1,0.6),(4.5,0.4,18,40.0,-1,0.8),(3.4,-0.3,1,20.0,1,1.0)):
    C,S_,LEN=hg.local_loop(['totem_R1','totem_R2'],beh,dz); plan.append(('rotonda',C,S_,LEN,ph,sgn,ns_,spr,0.2,max(1,round(0.6*90/LEN))))
b0=b1=0; acc_hi=0; per={}
for q,(name,C,S_,LEN,ph,sgn,n_,spr,bob,laps) in enumerate(plan):
    if name in ('fondo','pared'): continue
    P,V=simulate(lead_fn(C,S_,LEN,ph,sgn,bob,laps),F,n_,seed=5+q,spread=spr); Q=kbg(P)
    for s in hg.SC:
        m0,_=inpyr(s,P,0.45); m1,d1=inpyr(s,Q,0.45); b0+=int(m0.sum()); b1+=int(m1.sum())
        if m1.any(): per[(q,name,s['name'])]=(int(m1.sum()),round(float(d1[m1].min()),2))
    acc=np.linalg.norm(np.diff(Q,2,axis=0),axis=-1)*24*24; acc_hi=max(acc_hi,float(np.percentile(acc,99.9)))
print('fish-frames inside a visible pyramid <0.45 m behind the glass  before:',b0,' after:',b1,'  accel p99.9:',round(acc_hi,2),'m/s2')
for k,v in per.items(): print(k,v)
