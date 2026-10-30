# Simulates every school exactly as hall.py does (same plan, seeds, glass avoidance, drops) and caches positions.
import numpy as np, math, random, os, sys
import hallgeo as hg
from school import simulate
src=open('hall.py').read()
ns={'np':np,'hg':hg,'math':math,'random':random,'os':os,'LOOP_S':90.0,'T0':0.0,'LOD_FROM':7.0}
exec(src[src.index('def lead_fn'):src.index("if os.environ.get('FEWFISH')")],ns)
exec(src[src.index('def keep_behind_glass'):src.index('print(\'PREP armando')],ns)
plan=ns['plan']; lead_fn=ns['lead_fn']; kbg=ns['keep_behind_glass']; sliced=ns['sliced_fish']
F=2160; Ps=[]; Vs=[]; owner=[]
for q,(C,S_,LEN,ph,sgn,n_,spr,bob,far,laps,lod) in enumerate(plan):
    P,V=simulate(lead_fn(C,S_,LEN,ph,sgn,bob,laps),F,n_,seed=5+q,spread=spr,loop=90.0,darts=(2.5 if n_==1 else 1.2) if not far else 0.0)
    P=kbg(P); Ps.append(P); Vs.append(V); owner+= [q]*n_; print('plan',q,n_,'fish',flush=True)
P=np.concatenate(Ps,1); V=np.concatenate(Vs,1); owner=np.array(owner)
if len(sys.argv)>2:
    from avoid import avoid_schools
    P,V=avoid_schools(P,V,owner)
keepall=[]; o=0
for q in range(len(Ps)):
    n_=Ps[q].shape[1]; Q=kbg(P[:,o:o+n_]); P[:,o:o+n_]=Q; drop=set(sliced(Q).tolist()); keepall+=[o+j for j in range(n_) if j not in drop]; o+=n_
P=P[:,keepall]; owner=owner[keepall]
np.savez_compressed(sys.argv[1],P=P.astype(np.float32),owner=owner)
