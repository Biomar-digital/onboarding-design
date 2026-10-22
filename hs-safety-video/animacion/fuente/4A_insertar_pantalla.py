# Track the blank laptop screen in a clip and insert a still (perspective-warped) into it.
# python3 screen_insert.py clip.mp4 still.png out.mp4 quads.json
import sys, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
CLIP,STILL,OUT,QJ=sys.argv[1:5]
W,H,FPS=1920,1080,24
raw=subprocess.run(['ffmpeg','-v','error','-i',CLIP,'-vf',f'scale={W}:{H}:flags=lanczos,fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
frames=np.frombuffer(raw,np.uint8).reshape(-1,H,W,3)
still=Image.open(STILL).convert('RGB')
sw,sh=still.size
def coeffs(dst,src):
    # PIL PERSPECTIVE maps output (dst) pixel -> input (src) pixel
    A=[];B=[]
    for (x,y),(u,v) in zip(dst,src):
        A+= [[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]; B+=[u,v]
    return np.linalg.solve(np.array(A,float),np.array(B,float)).tolist()
box=None; quads=[]
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
for i,fr in enumerate(frames):
    m=fr.min(2)>228
    # the screen is the white blob connected to its centre (seeded from the last frame's quad)
    seed=(int(W*.56),int(H*.45)) if box is None else (int((box[0]+box[2])/2),int((box[1]+box[3])/2))
    mi=Image.fromarray((m*255).astype(np.uint8)).copy(); ImageDraw.floodfill(mi,seed,128)
    sub=np.array(mi)==128
    ys,xs=np.nonzero(sub)
    Y0,Y1,X0,X1=ys.min(),ys.max(),xs.min(),xs.max()
    def fit(ts,vals):                 # robust line fit on the middle 70% of an edge
        k=len(ts); sl=slice(int(k*.15),int(k*.85)); t,v=np.array(ts)[sl],np.array(vals)[sl]
        for _ in range(3):
            a,b=np.polyfit(t,v,1); r=np.abs(v-(a*t+b)); keep=r<max(1.5,np.percentile(r,80)); t,v=t[keep],v[keep]
        return np.polyfit(t,v,1)
    rws=[y for y in range(Y0,Y1+1) if sub[y].any()]; L=[np.nonzero(sub[y])[0].min() for y in rws]; R=[np.nonzero(sub[y])[0].max() for y in rws]
    cls=[x for x in range(X0,X1+1) if sub[:,x].any()]; T=[np.nonzero(sub[:,x])[0].min() for x in cls]; B=[np.nonzero(sub[:,x])[0].max() for x in cls]
    lx,rx,ty,by=fit(rws,L),fit(rws,R),fit(cls,T),fit(cls,B)     # x=a*y+b (left/right), y=a*x+b (top/bottom)
    def meet(v,h):                    # x=v0*y+v1 and y=h0*x+h1
        y=(h[0]*v[1]+h[1])/(1-h[0]*v[0]); return (v[0]*y+v[1],y)
    q=np.array([meet(lx,ty),meet(rx,ty),meet(rx,by),meet(lx,by)],float)
    if quads: q=0.85*q+0.15*np.array(quads[-1])
    quads.append(q.tolist()); box=(X0,Y0,X1,Y1)
    # grow the quad 2 px so it covers the anti-aliased white edge
    c=q.mean(0); g=max(4,0.011*np.linalg.norm(q[2]-q[0])); qg=c+(q-c)*(1+g/np.linalg.norm(q-c,axis=1,keepdims=True))
    warped=still.transform((W,H),Image.PERSPECTIVE,coeffs([tuple(v) for v in qg],[(0,0),(sw,0),(sw,sh),(0,sh)]),Image.BICUBIC)
    mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).polygon([tuple(v) for v in qg],fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(0.8))
    out=Image.fromarray(fr.copy()); out.paste(warped,(0,0),mask)
    p.stdin.write(np.asarray(out).tobytes())
p.stdin.close(); p.wait()
json.dump(quads,open(QJ,'w')); print('ok',len(quads),quads[0],quads[-1])
