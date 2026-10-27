# Microscope "camera look" for the egg renders, matched to a reference photo:
# 1) colour/contrast: per-channel histogram matching in LAB  2) uneven lamp: low-frequency illumination of the photo
# 3) lateral chromatic aberration + colour fringes  4) floating debris / micro bubbles  5) sensor grain, slight edge softness
# python3 micro_post.py RENDER.png REFERENCE.jpg OUT.jpg [seed]
import cv2, numpy as np, sys
src=cv2.imread(sys.argv[1]).astype(np.float32); ref=cv2.imread(sys.argv[2]); OUT=sys.argv[3]; rng=np.random.default_rng(int(sys.argv[4]) if len(sys.argv)>4 else 5)
H,W=src.shape[:2]; ref=cv2.resize(ref,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)
def hmatch(a,b):
    # map the value distribution of a onto b's (CDF matching), channel by channel
    out=np.empty_like(a)
    for c in range(a.shape[2]):
        av=a[...,c].ravel(); bv=np.sort(b[...,c].ravel())
        order=np.argsort(av,kind='stable'); ranks=np.empty_like(order); ranks[order]=np.arange(av.size)
        q=ranks/(av.size-1); out[...,c]=np.interp(q,np.linspace(0,1,bv.size),bv).reshape(a.shape[:2])
    return out
la=cv2.cvtColor(np.clip(src,0,255).astype(np.uint8),cv2.COLOR_BGR2LAB).astype(np.float32)
lb=cv2.cvtColor(ref.astype(np.uint8),cv2.COLOR_BGR2LAB).astype(np.float32)
m=la.copy(); m[...,0]=0.8*hmatch(la[...,:1],lb[...,:1])[...,0]+0.2*la[...,0]   # lightness: full distribution match
for c in (1,2):                                                     # colour: mean/spread only (CDF matching tinted the eggs)
    m[...,c]=(la[...,c]-la[...,c].mean())/(la[...,c].std()+1e-3)*lb[...,c].std()+lb[...,c].mean()
img=cv2.cvtColor(np.clip(m,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
# 2) uneven illumination: ratio of the photo's very low frequencies to the render's
s=max(W,H)/6; lo_r=cv2.GaussianBlur(ref,(0,0),s); lo_i=cv2.GaussianBlur(img,(0,0),s)
img=img*np.clip(lo_r/np.maximum(lo_i,1),0.85,1.15)
# 3) lateral chromatic aberration: red slightly larger, blue slightly smaller around the centre
def scale_ch(ch,k):
    M=cv2.getRotationMatrix2D((W/2,H/2),0,k); return cv2.warpAffine(ch,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
b,g,r=cv2.split(img); img=cv2.merge([scale_ch(b,0.9985),g,scale_ch(r,1.0015)])
# green/magenta fringes on strong edges (defocused phase rings of the chorion)
gray=cv2.cvtColor(np.clip(img,0,255).astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
lap=cv2.GaussianBlur(cv2.Laplacian(cv2.GaussianBlur(gray,(0,0),2.0),cv2.CV_32F),(0,0),2.5)
img[...,1]+=np.clip(lap,0,None)*0.9; img[...,0]+=np.clip(-lap,0,None)*0.6; img[...,2]+=np.clip(-lap,0,None)*0.6
# 4) debris and micro bubbles, mostly on the clear background between eggs
bg=(cv2.GaussianBlur(gray,(0,0),6)>np.percentile(gray,80)).astype(np.uint8)
yy,xx=np.nonzero(bg); n=int(W*H/45000)
for i in rng.choice(len(xx),size=min(n,len(xx)),replace=False):
    x,y=int(xx[i]),int(yy[i]); rr=rng.uniform(1.2,4.5)*W/2000
    if rng.random()<0.4:                                           # micro bubble: dark ring, bright core
        cv2.circle(img,(x,y),max(1,int(rr*1.6)),(70,70,75),max(1,int(rr*0.5)),cv2.LINE_AA)
    else:                                                          # debris speck
        cv2.circle(img,(x,y),max(1,int(rr)),tuple(float(v) for v in rng.uniform(60,120,3)),-1,cv2.LINE_AA)
img=cv2.GaussianBlur(img,(0,0),0.6)*0.35+img*0.65                   # soften the drawn specks a touch
# 5) edge softness (field curvature) + sensor grain
yv,xv=np.mgrid[0:H,0:W]; rad=np.sqrt(((xv-W/2)/(W/2))**2+((yv-H/2)/(H/2))**2)/1.414
soft=cv2.GaussianBlur(img,(0,0),1.6*W/2000); w=np.clip((rad-0.55)/0.45,0,1)[...,None]; img=img*(1-w)+soft*w
lum_noise=rng.normal(0,2.2,(H,W,1)); chroma=rng.normal(0,1.2,(H,W,3))
img=img+cv2.GaussianBlur((lum_noise+chroma).astype(np.float32),(0,0),0.6)
cv2.imwrite(OUT,np.clip(img,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,94]); print('ok',OUT)
