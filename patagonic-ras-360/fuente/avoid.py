# Schools are simulated one by one, so two of them can swim straight through each other where their paths cross.
# This pass looks at all fish together and, wherever fish of different schools come closer than R, pushes them
# apart sideways/vertically (never along their own heading, so nobody brakes or speeds up). The push is spread
# over time with the same wrap-around smoothing as the glass avoidance, so the loop stays seamless.
import numpy as np

def close_pairs(X,R):
    # all pairs (i<j) closer than R, numpy only (Blender's Python has no scipy): uniform grid of cell size R
    c=np.floor(X/R).astype(np.int64); c-=c.min(0); M=c.max(0)+3
    key=lambda q: ((q[:,0]+1)*M[1]+(q[:,1]+1))*M[2]+(q[:,2]+1)
    k0=key(c); order=np.argsort(k0,kind='stable'); sk=k0[order]
    A=[];B=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for dz in (-1,0,1):
                kt=key(c+np.array([dx,dy,dz])); lo=np.searchsorted(sk,kt,'left'); hi=np.searchsorted(sk,kt,'right')
                cnt=hi-lo
                if cnt.sum()==0: continue
                ii=np.repeat(np.arange(len(X)),cnt); jj=order[np.repeat(lo,cnt)+(np.arange(cnt.sum())-np.repeat(np.cumsum(cnt)-cnt,cnt))]
                A.append(ii); B.append(jj)
    a=np.concatenate(A); b=np.concatenate(B); m=a<b; a,b=a[m],b[m]
    d=np.linalg.norm(X[a]-X[b],axis=1); m=d<R
    return np.stack([a[m],b[m]],1)
def avoid_schools(P, V, owner, R=0.6, iters=9, win=48, sigma=10.0):
    F,N,_=P.shape; out=P.copy()
    G=np.exp(-0.5*(np.arange(-3*int(sigma),3*int(sigma)+1)/sigma)**2); G/=G.sum(); hw=len(G)//2
    vh=V/np.maximum(np.linalg.norm(V,axis=-1,keepdims=True),1e-6)
    for it in range(iters):
        tot=np.zeros_like(out); hits=0
        for f in range(F):
            X=out[f]; pr=close_pairs(X,R)
            if len(pr)==0: continue
            a,b=pr[:,0],pr[:,1]; m=owner[a]!=owner[b]; a,b=a[m],b[m]
            if len(a)==0: continue
            hits+=len(a); d=X[a]-X[b]; dist=np.linalg.norm(d,axis=1,keepdims=True); u=d/np.maximum(dist,1e-6)
            u[dist[:,0]<1e-4]=np.array([0,0,1.0])
            push=0.5*(R-dist)*u
            pa=push-(push*vh[f,a]).sum(1,keepdims=True)*vh[f,a]; pb=-push-(-push*vh[f,b]).sum(1,keepdims=True)*vh[f,b]
            np.add.at(tot[f],a,pa); np.add.at(tot[f],b,pb)
        print('avoid_schools iter',it,'close pairs',hits,flush=True)
        if hits==0: break
        mag=np.linalg.norm(tot,axis=-1)
        pad=np.pad(mag,((win//2,win//2),(0,0)),mode='wrap'); idx=np.lib.stride_tricks.sliding_window_view(pad,win,axis=0).argmax(-1)[:F]
        rows=(np.arange(F)[:,None]-win//2+idx)%F; dil=tot[rows,np.arange(N)[None,:]]
        padd=np.concatenate([dil[-hw:],dil,dil[:hw]],0)
        sm=np.zeros_like(dil)
        for k,g in enumerate(G): sm+=g*padd[k:k+F]
        out=out+1.4*sm
    dV=(np.roll(out-P,-1,0)-np.roll(out-P,1,0))*0.5*24.0      # heading follows the swerve
    return out, V+dV
