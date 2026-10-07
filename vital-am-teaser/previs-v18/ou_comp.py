# over/under composite: above-water pass on top; below a moving wavy waterline the under-water pass, shifted so its own
# horizon (the edge of the surface seen from below) sits on the waterline -> no bright band under the line
import json, sys
import numpy as np
from PIL import Image
out=sys.argv[1]; m=json.load(open('ou_under/map.json'))
for F,y in m:
    a=np.asarray(Image.open(f'ou_above/p{F:04d}.jpg'),float); u=np.asarray(Image.open(f'ou_under/p{F:04d}.jpg'),float)
    H,W,_=a.shape
    rows=u[:, W//4:3*W//4].mean(axis=(1,2)); dif=rows[1:int(H*0.9)]-rows[:int(H*0.9)-1]
    hz=int(np.argmin(dif))+1                         # sharpest bright->dark step = under-water horizon
    base=(y+0.12)/0.24*H
    shift=int(round(base-hz)); us=np.empty_like(u)
    if shift>=0: us[shift:]=u[:H-shift]; us[:shift]=u[0]
    else: us[:H+shift]=u[-shift:]; us[H+shift:]=u[-1]
    xs=np.arange(W); line=base+5*np.sin(xs/37.0+F*0.4)+3*np.sin(xs/13.0-F*0.7)
    ys=np.arange(H)[:,None]; t=np.clip((ys-line[None,:])/6.0+0.5,0,1)[...,None]
    img=a*(1-t)+us*t
    edge=np.exp(-((ys-line[None,:])/2.2)**2)[...,None]; img=img*(1-0.35*edge)+255*0.35*edge
    Image.fromarray(np.clip(img,0,255).astype(np.uint8)).save(f'{out}/p{F:04d}.jpg',quality=92)
print('over/under frames',len(m))
