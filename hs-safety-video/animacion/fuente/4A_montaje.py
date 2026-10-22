# 4A: phone full -> split (computer | phone) -> computer expands -> zoom into blank laptop screen.
# python3 assemble.py phone.mp4 typing.mp4 zoom.mp4 out.mp4 [phone_cx] [comp_cx]
import sys, subprocess, numpy as np
P,T,Z,OUT=sys.argv[1:5]
PCX=float(sys.argv[5]) if len(sys.argv)>5 else 0.5     # subject centre (fraction of width) to keep in the half panel
CCX=float(sys.argv[6]) if len(sys.argv)>6 else 0.5
W,H,FPS=1920,1080,24
def read(p):
    raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-vf',f'scale={W}:{H},fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,H,W,3)
ph,ty,zo=read(P),read(T),read(Z)
def pp(clip,t):                       # ping-pong so short clips can cover longer holds
    n=len(clip); i=int(round(t*FPS)); k=i%(2*n-2); return clip[k if k<n else 2*n-2-k]
ease=lambda x:(lambda x:x*x*(3-2*x))(min(1,max(0,x)))
def panel(fr,w,cx):                   # crop a w-wide window around cx
    x0=int(round(min(max(cx*W-w/2,0),W-w))); return fr[:,x0:x0+w]
# optional: quads json of the zoom clip + the screen image inserted into it (the zoom then lands on that image)
QJ=sys.argv[7] if len(sys.argv)>7 else None
SCR=np.asarray(__import__('PIL.Image',fromlist=['Image']).open(sys.argv[8]).convert('RGB').resize((W,H))) if len(sys.argv)>8 else np.full((H,W,3),255,np.uint8)
if QJ:
    import json; q=np.array(json.load(open(QJ))[-1]); sx0,sy0=q.min(0); sx1,sy1=q.max(0)
else:
    last=zo[-1].astype(int); m=last.min(2)>238; ys,xs=np.nonzero(m)
    sx0,sx1,sy0,sy1=np.percentile(xs,2),np.percentile(xs,98),np.percentile(ys,2),np.percentile(ys,98)
print('screen',sx0,sx1,sy0,sy1)
T1,T2,T3,T4,END=4.0,4.8,9.5,10.3,15.0
DIV=6
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-c:v','libx264','-crf','16','-preset','slow','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
for i in range(int(END*FPS)):
    t=i/FPS
    if t<T1: f=pp(ph,t)
    elif t<T4:
        if t<T2: w=int(round(W/2*ease((t-T1)/(T2-T1))))
        elif t<T3: w=W//2
        else: w=int(round(W/2+W/2*ease((t-T3)/(T4-T3))))
        # typing clip runs backwards so it lands on its start frame (= zoom clip's start frame) at T3;
        # the zoom clip then takes over and keeps running while the panel expands, so there is no blend
        comp=pp(ty,max(0,T3-t)) if t<T3 else zo[min(int((t-T3)*FPS),len(zo)-1)]
        f=np.empty((H,W,3),np.uint8)
        if w>0: f[:,:w]=panel(comp,w,CCX if w<W else .5)
        if w<W: f[:,w:]=panel(pp(ph,t),W-w,PCX)
        if 0<w<W: f[:,max(0,w-DIV//2):w+DIV//2]=255
    else:
        tz=t-T3; f=zo[min(int(tz*FPS),len(zo)-1)]
        zs=END-0.7                    # last 0.7 s: digital push into the white screen
        if t>zs:
            a=ease((t-zs)/0.6); cw=W+(sx1-sx0-(0 if QJ else 40)-W)*a; ch=cw*H/W
            cx=W/2+((sx0+sx1)/2-W/2)*a; cy=H/2+((sy0+sy1)/2-H/2)*a
            x0=int(max(0,min(cx-cw/2,W-cw))); y0=int(max(0,min(cy-ch/2,H-ch)))
            from PIL import Image
            f=np.asarray(Image.fromarray(f).crop((x0,y0,x0+int(cw),y0+int(ch))).resize((W,H),Image.LANCZOS))
            k=ease((a-0.6)/0.4) if a>0.6 else 0          # settle exactly on the flat screen image
            f=(f*(1-k)+SCR*k).astype(np.uint8)
            if a>=0.999: f=SCR
    p.stdin.write(np.ascontiguousarray(f).tobytes())
p.stdin.close(); p.wait(); print('ok',OUT)
