# Screen-recording edit: windows format + time remap + zoom + highlights.
# python3 edit.py SRC_DIR TASKBAR OUT.mp4 [preview_times]
import sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
SRC,TB,OUT=sys.argv[1:4]; ONLY=sys.argv[4] if len(sys.argv)>4 else None
W,H,FPS=1920,1080,30; T0=4.5                     # first extracted frame = src 4.5 s
tb=Image.open(TB).convert('RGB')
ORANGE=(221,105,40)
def src_frame(ts):
    k=int(round((ts-T0)*FPS))+1; k=max(1,min(345,k))
    a=np.asarray(Image.open(f'{SRC}/f{k:04d}.jpg').convert('RGB'))
    top=a[148:927]; fill=np.repeat(a[926:927],1032-len(top),0)
    im=Image.fromarray(np.concatenate([top,fill])); out=Image.new('RGB',(W,H)); out.paste(im,(0,0)); out.paste(tb,(0,1032)); return out
# segments: (src_start, src_end, speed)
SEG=[(4.6,5.3,1.0),(5.3,11.1,1.8),(11.1,12.5,1.0),(12.5,13.4,3.0),(13.4,13.7,1.0),(13.7,15.9,1.0)]
bounds=[];t=0
for a,b,s in SEG: d=(b-a)/s; bounds.append((t,t+d,a,s)); t+=d
DUR=t
def remap(t):
    for t0,t1,a,s in bounds:
        if t<t1: return a+(t-t0)*s
    return SEG[-1][1]
def out_t(src):                                   # output time at which a src time plays
    for t0,t1,a,s in bounds:
        if a<=src<=a+(t1-t0)*s: return t0+(src-a)/s
ease=lambda x:(lambda x:x*x*(3-2*x))(min(1,max(0,x)))
# boxes in formatted coordinates (src y - 148)
SEARCH=(806,48,1106,79); RESULT=(803,84,1111,114); CLICK=(873,100)
t_type=out_t(5.3); t_res=out_t(11.15); t_click=out_t(12.45); t_form=out_t(13.7)
def box_glow(img,box,alpha):
    if alpha<=0: return img
    x0,y0,x1,y1=box; pad=6
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((x0-pad,y0-pad,x1+pad,y1+pad),radius=10,outline=ORANGE+(int(255*alpha),),width=4)
    glow=lay.filter(ImageFilter.GaussianBlur(6))
    base=img.convert('RGBA'); base.alpha_composite(glow); base.alpha_composite(lay)
    # soft tint inside
    tint=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(tint).rounded_rectangle((x0-pad,y0-pad,x1+pad,y1+pad),radius=10,fill=ORANGE+(int(28*alpha),))
    base.alpha_composite(tint); return base.convert('RGB')
def ring(img,c,p):
    if not 0<p<1: return img
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for k in (0,0.35):
        q=p-k
        if 0<q<1:
            r=8+34*ease(q); a=int(230*(1-q))
            d.ellipse((c[0]-r,c[1]-r,c[0]+r,c[1]+r),outline=ORANGE+(a,),width=4)
    base=img.convert('RGBA'); base.alpha_composite(lay); return base.convert('RGB')
def zoom_params(t):
    zin=ease((t-t_type-0.15)/0.7); zout=ease((t-t_click-0.25)/0.8)
    z=1+1.25*zin*(1-zout); return z,(956,150)
def render(t):
    im=src_frame(remap(t))
    # search bar highlight while typing, then the result row before/at the click
    a1=ease((t-t_type-0.5)/0.3)*(1-ease((t-t_res)/0.25))
    a2=ease((t-t_res-0.1)/0.3)*(1-ease((t-t_click-0.15)/0.2))
    im=box_glow(im,SEARCH,a1); im=box_glow(im,RESULT,a2)
    im=ring(im,CLICK,(t-(t_click-0.5))/0.9)
    z,(cx,cy)=zoom_params(t)
    if z>1.001:
        cw,ch=W/z,H/z; x0=min(max(cx-cw/2,0),W-cw); y0=min(max(cy-ch/2,0),H-ch)
        im=im.resize((W,H),Image.LANCZOS,box=(x0,y0,x0+cw,y0+ch))
    return im
print('duration',round(DUR,2),'type',round(t_type,2),'res',round(t_res,2),'click',round(t_click,2),'form',round(t_form,2))
if ONLY:
    for x in ONLY.split(','): render(float(x)).save(f'{OUT}_{x}.jpg',quality=88)
    sys.exit()
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
p.stdin.close(); p.wait(); print('ok',OUT)
