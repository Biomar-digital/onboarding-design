# Post: dissolve phone->drone (118-131 from 117), water drops on the lens as the camera leaves the water, encode.
import sys, os, math, random, shutil, subprocess
import numpy as np
from PIL import Image, ImageFilter
SRC,OUT,MP4=sys.argv[1],sys.argv[2],sys.argv[3]
EXIT=465; DUR=22
os.makedirs(OUT,exist_ok=True)
a117=Image.open(f'{SRC}/f0117.jpg').convert('RGB'); W,H=a117.size; sc=W/960
random.seed(3)
drops=[]
while len(drops)<16:
    x=random.uniform(0,W)
    if 0.33*W<x<0.67*W: continue          # keep the bag clear
    r=random.uniform(6,24)*sc; drops.append([x,random.uniform(-0.1*H,H),r,random.uniform(0.2,1.6)*sc*(r/(20*sc)),random.uniform(0,6)])
def lens_drops(img,t,k):
    a=np.asarray(img).astype(np.float32); out=a.copy(); yy,xx=np.mgrid[0:H,0:W]
    blur=np.asarray(img.filter(ImageFilter.GaussianBlur(2.5*sc))).astype(np.float32)
    # thin water film right after breaking the surface: soft blur fading out
    film=max(0.0,1-t/7.0); out=out*(1-0.8*film)+blur*0.8*film
    for x0,y0,r,vy,ph in drops:
        y=y0+vy*t*t*0.6; x=x0+math.sin(ph+t*0.15)*1.5*sc; rr=r*(1-0.35*t/DUR)
        x1,x2=int(max(0,x-rr)),int(min(W,x+rr+1)); y1,y2=int(max(0,y-rr*1.25)),int(min(H,y+rr*1.25+1))
        if x1>=x2 or y1>=y2: continue
        dx=(xx[y1:y2,x1:x2]-x)/rr; dy=(yy[y1:y2,x1:x2]-y)/(rr*1.25); d2=dx*dx+dy*dy; m=d2<1
        if not m.any(): continue
        # a drop is a tiny lens: inverted, magnified view of what is behind it
        sx=np.clip((x-dx*rr*0.55).astype(int),0,W-1); sy=np.clip((y-dy*rr*0.55*1.25).astype(int),0,H-1)
        refr=a[sy,sx]*0.92; edge=np.clip((d2-0.6)/0.4,0,1)[...,None]
        col=refr*(1-0.18*edge)
        hl=np.exp(-(((dx+0.35)**2+(dy+0.4)**2)/0.02))[...,None]*70
        col=col+hl; blk=out[y1:y2,x1:x2]; al=(m[...,None]*k*0.8)
        out[y1:y2,x1:x2]=blk*(1-al)+col*al
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8))
n=len([f for f in os.listdir(SRC) if f.endswith('.jpg')])
for F in range(1,n+1):
    src=f'{SRC}/f{F:04d}.jpg'; dst=f'{OUT}/f{F:04d}.jpg'
    if 118<=F<=131:
        t=(F-117)/15; t=t*t*(3-2*t); Image.blend(a117,Image.open(src).convert('RGB'),t).save(dst,quality=94)
    elif EXIT<=F<EXIT+DUR:
        t=F-EXIT; k=1.0 if t<DUR-8 else (DUR-t)/8.0
        lens_drops(Image.open(src).convert('RGB'),t,k).save(dst,quality=94)
    else: shutil.copy(src,dst)
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','24','-i',f'{OUT}/f%04d.jpg','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart',MP4],check=True)
print('POST_OK',n)
