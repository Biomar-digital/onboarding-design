# Builds the Vital AM bag texture: places the pack art (PDF page 1 rendered at 100 dpi -> hi-1.png)
# into the UV area of the SmartCare mockup and keeps a soft version of its baked bag shading (glbtex0.jpg).
from PIL import Image, ImageFilter
import numpy as np
O=np.asarray(Image.open('glbtex0.jpg').convert('RGB')).astype(np.float32)/255
L=O.mean(2); mx=O.max(2); mn=O.min(2); sat=(mx-mn)/(mx+1e-4)
cream=(sat<0.12)&(L>0.6)
orange=(O[...,0]>O[...,2]+0.25)&(sat>0.45)
valid=cream|orange
base=np.where(cream, np.median(L[cream]), np.median(L[orange]))
D=np.where(valid, L/base, 1.0)
# fill invalid (text/icons) with blurred valid shading
def box(a,r,ax):
  r=max(1,int(r)); p=np.pad(a,[(r+1,r) if i==ax else (0,0) for i in range(2)],mode='edge')
  c=np.cumsum(p,axis=ax); n=a.shape[ax]
  hi=np.take(c,range(2*r+1,2*r+1+n),axis=ax); lo=np.take(c,range(0,n),axis=ax)
  return (hi-lo)/(2*r+1)
def blur(a,r):
  a=a.astype(np.float32)
  for _ in range(3): a=box(box(a,r/1.7,0),r/1.7,1)
  return a
w=valid.astype(np.float32)
Df=blur(D*w,12)/np.maximum(blur(w,12),1e-3)
D=np.where(valid,D,Df)
# soften the cream/orange boundary step and clamp
D=blur(D,30); D=1+0.5*(D/np.median(D[valid])-1)
D=np.clip(D,0.55,1.25)
# --- build Vital AM art in UV rect
art=Image.open('hi-1.png').convert('RGB').crop((335,0,2107,2560))
u0,u1,v0,v1=600,1467,254,1735
W=u1-u0; aw,ah=W,round(2560*W/1772)
art=art.resize((aw,ah),Image.LANCZOS)
top=130
canvas=Image.new('RGB',(2048,2048),(38,67,125))
canvas.paste(art,(u0,v0+top))
# bottom fill: mirror the bottom band of the art
rem=(v1+40)-(v0+top+ah)
if rem>0:
  full=Image.open('hi-1.png').convert('RGB')
  strip=full.crop((0,1200,335,2560)).resize((round(335*W/1772),round(1360*W/1772)),Image.LANCZOS)
  sw,sh=strip.size
  for x in range(u0,u1,sw): canvas.paste(strip.crop((0,0,sw,rem)),(x,v0+top+ah))
# extend sideways a bit for edge bleed
c=np.asarray(canvas).astype(np.float32)/255
c[:, :u0]=c[:, u0:u0+1]; c[:, u1:]=c[:, u1-1:u1]
out=np.clip(c*D[...,None],0,1)
# lift highlights (specular sheen) where shading >1
Image.fromarray((out*255).astype(np.uint8)).save('vital_front.jpg',quality=92)
Image.fromarray((np.clip(D/1.25,0,1)*255).astype(np.uint8)).save('shading.png')
print('art',aw,ah,'rem',rem)
