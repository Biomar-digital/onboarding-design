import numpy as np, hallgeo as hg, sys, json
def lead_pts(C,S_,LEN,ph,sgn,spr,t):
    V=LEN/90; out=[]
    for off in np.linspace(-4*spr,4*spr,9):
        s=(sgn*V*(t+ph)+off)%LEN; i=np.searchsorted(S_,s,side='right')-1; i=min(i,len(C)-1); out.append(C[i])
    return out
def visible(s,p):
    e=s['eye']; d=p-e; n=s['n']; den=np.dot(d,-n)
    if den<=0: return False
    D=np.dot(s['c']-e,-n); 
    if np.dot(d,-n)<D: return False
    q=e+d*(D/den)-s['c']; return abs(np.dot(q,s['t']))<s['W']/2+0.3 and abs(q[2])<s['H']/2+0.2
def cover(plan):
    T=np.arange(0,90,0.5); res={s['name']:0 for s in hg.SC}
    for t in T:
        for s in hg.SC:
            if any(visible(s,p) for pl in plan for p in lead_pts(*pl,t)): res[s['name']]+=1
    return {k:round(v/len(T),2) for k,v in res.items()}
