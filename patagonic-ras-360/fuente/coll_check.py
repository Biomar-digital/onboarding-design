# Finds fish of DIFFERENT schools that pass through each other while visible on a screen.
import numpy as np, sys
from scipy.spatial import cKDTree
import hallgeo as hg
d=np.load(sys.argv[1]); P=d['P']; own=d['owner']; R=float(sys.argv[2]) if len(sys.argv)>2 else 0.3
def vis(s,X,maxd=10.0):
    c,n,t=s['c'],s['n'],s['t']; e=s['eye']; D=s['D']; rel=X-e; along=rel@(-n); dd=along-D
    ox=rel@t-((c-e)@t)*along/D; oz=rel[...,2]-(c[2]-e[2])*along/D
    return (along>0.05)&(np.abs(ox)<(s['W']/2)*along/D)&(np.abs(oz)<(s['H']/2)*along/D)&(dd>0)&(dd<maxd)
rep={}
for f in range(0,P.shape[0],2):
    X=P[f]
    for s in hg.SC:
        m=vis(s,X)
        idx=np.where(m)[0]
        if len(idx)<2: continue
        tr=cKDTree(X[idx]); pr=tr.query_pairs(R,output_type='ndarray')
        if len(pr)==0: continue
        a=idx[pr[:,0]]; b=idx[pr[:,1]]; x=own[a]!=own[b]
        for i,j in zip(a[x],b[x]):
            k=(s['name'],min(own[i],own[j]),max(own[i],own[j])); rep.setdefault(k,[]).append(f)
for k,v in sorted(rep.items(),key=lambda kv:-len(kv[1])):
    print(k,'pair-hits',len(v),'frames %d-%d'%(min(v),max(v)))
