# Smooth the previs camera (positions + orientation + lens) inside shots: removes the frame-to-frame jitter
# of the realtime previs capture and the stop-and-go between camera segments. Sigma varies per frame.
import json, math, numpy as np
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
cams={}; shot={}
for line in open(S+'bt/dump.jsonl'):
    d=json.loads(line); cams[d['F']]=(np.array(d['cam']).reshape(4,4).T, d['mm']); shot[d['F']]=d['shot']
def q_from(R):
    t=R.trace()
    if t>0: s=math.sqrt(t+1)*2; return np.array([0.25*s,(R[2,1]-R[1,2])/s,(R[0,2]-R[2,0])/s,(R[1,0]-R[0,1])/s])
    i=np.argmax([R[0,0],R[1,1],R[2,2]])
    if i==0: s=math.sqrt(1+R[0,0]-R[1,1]-R[2,2])*2; return np.array([(R[2,1]-R[1,2])/s,0.25*s,(R[0,1]+R[1,0])/s,(R[0,2]+R[2,0])/s])
    if i==1: s=math.sqrt(1+R[1,1]-R[0,0]-R[2,2])*2; return np.array([(R[0,2]-R[2,0])/s,(R[0,1]+R[1,0])/s,0.25*s,(R[1,2]+R[2,1])/s])
    s=math.sqrt(1+R[2,2]-R[0,0]-R[1,1])*2; return np.array([(R[1,0]-R[0,1])/s,(R[0,2]+R[2,0])/s,(R[1,2]+R[2,1])/s,0.25*s])
def R_from(q):
    w,x,y,z=q/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def sigma(F):
    if 100<=F<=117: return 3.0                         # phone turn
    if 119<=F<=250: return 7.0                         # drone: approach + orbit
    if 250<F<=262: return 7.0*(262-F)/12.0             # taper into the pellet follow
    return 0.0
out={}
FARMER=np.array([0.0,1.2,-9.82])   # three coords (x, y up, z=-blender y)
PLANE={'s2':0.548,'s3':0.8}
for F in range(1,542):
    s=sigma(F)
    if s<=0.05: continue
    sh=shot[F]; Rn=int(3*s)+1; ws=[]; ps=[]; qs=[]; ms=[]; valid=set()
    q0=q_from(cams[F][0][:3,:3])
    for G in range(F-Rn,F+Rn+1):
        if G not in cams or shot[G]!=sh or (sh=='s2' and G<100) : continue
        if sh=='s3' and G<119: continue
        w=math.exp(-0.5*((G-F)/s)**2); M,mm=cams[G]; q=q_from(M[:3,:3]); q=q if np.dot(q,q0)>=0 else -q
        valid.add(G); ws.append(w); ps.append(M[:3,3]); qs.append(q); ms.append(mm)
    ws=np.array(ws)/sum(ws); p=(np.array(ps)*ws[:,None]).sum(0); q=(np.array(qs)*ws[:,None]).sum(0); mm=float((np.array(ms)*ws).sum())
    R=R_from(q)
    # keep the subject framed: aim the smoothed position at a smoothed look-target (point the original camera looked at)
    ts=[]
    for G,w in zip([G for G in range(F-Rn,F+Rn+1) if G in valid],ws):
        M0=cams[G][0]; fwd=-M0[:3,2]; Y0=PLANE.get(sh,0.8); D=(M0[1,3]-Y0)/(-fwd[1]) if fwd[1]<-0.05 else 40.0
        if sh=='s3' and G>=186: D=np.linalg.norm(M0[:3,3]-FARMER)
        ts.append(M0[:3,3]+fwd*D)
    tgt=(np.array(ts)*ws[:,None]).sum(0); z=p-tgt; z/=np.linalg.norm(z); up=R[:,1]; x=np.cross(up,z); x/=np.linalg.norm(x); y=np.cross(z,x)
    R=np.stack([x,y,z],1)
    M=np.eye(4); M[:3,:3]=R; M[:3,3]=p
    out[F]=[list(M.T.reshape(16)),mm]
json.dump(out,open(S+'bt/cam_smooth.json','w')); print(len(out))
# report speed profile
prev=None; sp=[]
for F in range(119,263):
    p=np.array(out[F][0][12:15]) if F in out else cams[F][0][:3,3]
    if prev is not None: sp.append('%d:%.2f'%(F,np.linalg.norm(p-prev)))
    prev=p
print(' '.join(sp))
