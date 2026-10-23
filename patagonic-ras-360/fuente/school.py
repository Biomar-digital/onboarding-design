# Smooth schooling: each fish keeps a slot in an elongated formation that follows a lead path,
# with slow per-fish wander, soft separation, limited turn rate and low-passed heading.
import numpy as np, math
def simulate(lead, F, NS, seed=5, fps=24, warm=144, sub=4, spread=1.0):
    rng=np.random.default_rng(seed); dt=1/fps/sub
    # slots in the school frame: x along travel, y across (depth), z up
    slot=np.c_[rng.uniform(-4.0,4.0,NS)*spread, rng.uniform(-2.0,2.0,NS)*spread, rng.normal(0,0.3,NS)*spread]
    # slow wander: 3 sines per axis per fish (periods 3-7 s)
    wf=rng.uniform(2*math.pi/7,2*math.pi/3,(NS,3,3)); wp=rng.uniform(0,6.28,(NS,3,3)); wa=np.array([0.6,0.5,0.15])
    spd_f=rng.uniform(2*math.pi/8,2*math.pi/4,NS); spd_p=rng.uniform(0,6.28,NS)
    def frame(t):
        p,v=lead(t); h=v/np.linalg.norm(v); side=np.cross([0,0,1],h); side/=np.linalg.norm(side)
        return p,v,h,side
    t0=-warm/fps; p,v,h,side=frame(t0)
    P=p+slot[:,:1]*h+slot[:,1:2]*side+slot[:,2:3]*np.array([0,0,1]); V=np.tile(v,(NS,1))
    outP=[];outV=[]; Vs=V.copy()
    for k in range(-warm*sub, F*sub):
        t=k*dt; p,v,h,side=frame(t)
        wob=(wa*np.sin(wf*t+wp).sum(2)/3)
        tgt=p+(slot[:,:1]+wob[:,:1])*h+(slot[:,1:2]+wob[:,1:2])*side+(slot[:,2:3]+wob[:,2:3])*np.array([0,0,1])
        d=P[:,None,:]-P[None,:,:]; dist=np.linalg.norm(d,axis=2)+np.eye(NS)*99
        rep=np.clip(1.2-dist,0,None)[:,:,None]*d/np.maximum(dist[:,:,None],1e-3)
        corr=0.35*(tgt-P)+0.8*rep.sum(1)
        cn=np.linalg.norm(corr,axis=1,keepdims=True); corr=corr*np.minimum(1,0.25/np.maximum(cn,1e-6))   # settle into place gently
        desired=v*(1+0.12*np.sin(spd_f*t+spd_p))[:,None]+corr
        desired[:,2]*=0.5
        # limited acceleration and turn rate
        dv=desired-V; acc=np.linalg.norm(dv,axis=1,keepdims=True); amax=0.9
        dv=dv*np.minimum(1,amax/np.maximum(acc,1e-6))
        Vn=V+dv*dt
        hd0=V/np.linalg.norm(V,axis=1,keepdims=True); hd1=Vn/np.linalg.norm(Vn,axis=1,keepdims=True)
        ang=np.arccos(np.clip((hd0*hd1).sum(1),-1,1)); maxang=math.radians(35)*dt
        lim=ang>maxang
        if lim.any():
            a=maxang/ang[lim]; hd=hd0[lim]*(1-a)[:,None]+hd1[lim]*a[:,None]; hd/=np.linalg.norm(hd,axis=1,keepdims=True)
            Vn[lim]=hd*np.linalg.norm(Vn[lim],axis=1,keepdims=True)
        V=Vn; P=P+V*dt
        Vs=Vs+(V-Vs)*(dt/0.35)                      # low-passed velocity for the body orientation
        if k>=0 and k%sub==0: outP.append(P.copy()); outV.append(Vs.copy())
    return np.array(outP),np.array(outV)
