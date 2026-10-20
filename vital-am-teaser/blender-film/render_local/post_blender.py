# Post inside Blender (no external Python/ffmpeg): dissolve phone->drone (118-131 from 117),
# waterline split frames, sun flare, vignette, grain, then H.264 encode with Blender's own ffmpeg.
# blender -b --factory-startup -P post_blender.py -- SRC OUT MP4
import bpy, sys, os, math, json
import numpy as np
SRC,OUT,MP4=[os.path.abspath(p) for p in sys.argv[sys.argv.index('--')+1:][:3]]
os.makedirs(OUT,exist_ok=True)

def load(p):
    im=bpy.data.images.load(p); W,H=im.size; a=np.empty(W*H*4,np.float32); im.pixels.foreach_get(a)
    bpy.data.images.remove(im); return a.reshape(H,W,4)[::-1,:,:3]*255.0
_buf={}
def save(a,p):
    H,W=a.shape[:2]
    if (W,H) not in _buf: _buf[(W,H)]=bpy.data.images.new('post_%dx%d'%(W,H),W,H,alpha=False)
    im=_buf[(W,H)]; px=np.ones((H,W,4),np.float32); px[...,:3]=np.clip(a,0,255)[::-1]/255.0
    im.pixels.foreach_set(px.ravel()); im.filepath_raw=p; im.file_format='JPEG'; im.save()

a117=load(f'{SRC}/f0117.jpg'); H,W=a117.shape[:2]; sc=W/960
ZR=0.05
def split(F):
    m=json.load(open(f'{SRC}/f{F:04d}.json')); z=m['z']; zz=z*abs(z)/ZR if abs(z)<ZR else z
    s=max(-1.0,min(1.0,zz/ZR))
    air=load(f'{SRC}/f{F:04d}_a.jpg'); und=load(f'{SRC}/f{F:04d}_u.jpg')
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    wave=(3.0*np.sin(xx/(40*sc)+F*0.6)+1.5*np.sin(xx/(13*sc)-F*1.1))*sc
    yl=H*(0.5+0.5*s)+(xx-W/2)*math.tan(m['roll'])+wave
    dist=yy-yl                                   # >0 below the waterline
    off=np.clip(6*sc*np.exp(-np.clip(dist,0,None)/(18*sc)),0,None)
    sy=np.clip((yy+off).astype(int),0,H-1); und2=und[sy,xx.astype(int)]
    und2=und2*(1+0.18*np.exp(-np.clip(dist,0,None)/(22*sc))[...,None])
    a=np.clip(0.5-dist/(1.5*sc),0,1)[...,None]   # soft edge
    out=air*a+und2*(1-a)
    band=np.exp(-((dist-1.5*sc)/(2.2*sc))**2)[...,None]; out=out*(1-0.45*band)
    rim=np.exp(-((dist+1.2*sc)/(0.9*sc))**2)[...,None]; out=out+60*rim
    return out
n=len([f for f in os.listdir(SRC) if f.endswith('.jpg') and '_' not in f])
yy0,xx0=np.mgrid[0:H,0:W].astype(np.float32)
VIG=(1.0-0.28*np.clip(((xx0-W/2)/(W/2))**2*0.8+((yy0-H/2)/(H/2))**2*0.9-0.25,0,1))[...,None]
FL={'p':None,'amp':0.0}
def flare(a):
    # flare only from a real, clipped sun disc; position and strength are smoothed over frames so it never jumps or pops
    L=a.mean(2); m=L.max(); tgt=0.0; pos=None
    if m>=250:
        ys,xs=np.nonzero(L>m-6)
        if len(xs)>=12: pos=(xs.mean(),ys.mean()); tgt=min(1.0,(m-250)/5.0)
    if pos is not None:
        q=FL['p']; FL['p']=pos if q is None or math.hypot(pos[0]-q[0],pos[1]-q[1])>60*sc else (0.5*q[0]+0.5*pos[0],0.5*q[1]+0.5*pos[1])
    FL['amp']+=(tgt-FL['amp'])*0.35
    if FL['p'] is None or FL['amp']<0.02: return a
    k=FL['amp']; sx,sy=FL['p']; cx,cy=W/2,H/2; out=a.copy()
    # soft anamorphic streak through the sun
    st=np.exp(-((yy0-sy)/(3.5*sc))**2)*np.exp(-np.abs(xx0-sx)/(260*sc)); out+=k*st[...,None]*np.array([90,60,30],np.float32)
    # ghosts along the sun -> centre line
    for t,r,col in ((0.55,26,(40,30,18)),(0.95,14,(28,32,40)),(1.35,44,(20,26,30)),(1.7,9,(40,28,16))):
        gx=sx+(cx-sx)*t; gy=sy+(cy-sy)*t
        d2=((xx0-gx)**2+(yy0-gy)**2)/(r*sc)**2; out+=k*(np.clip(1-d2,0,1)**1.5)[...,None]*np.array(col,np.float32)
    return out
def finish(a,F):
    if F>=465: a=flare(a)
    a=a*VIG
    g=np.random.default_rng(F).normal(0,3.2,(H,W,1)).astype(np.float32)
    return a+g*(0.6+0.4*(1-a.mean(2,keepdims=True)/255))     # fine grain, a bit stronger in the shadows
for F in range(1,n+1):
    dst=f'{OUT}/f{F:04d}.jpg'
    if os.path.exists(dst): continue
    if 118<=F<=131:
        t=(F-117)/15; t=t*t*(3-2*t); a=a117*(1-t)+load(f'{SRC}/f{F:04d}.jpg')*t
    elif os.path.exists(f'{SRC}/f{F:04d}.json'): a=split(F)
    else: a=load(f'{SRC}/f{F:04d}.jpg')
    save(finish(a,F),dst)
    if F%50==0: print('POST',F,'/',n,flush=True)

# encode the finished frames with the sequencer
sc_=bpy.context.scene; sc_.sequence_editor_create()
files=[{'name':f'f{F:04d}.jpg'} for F in range(1,n+1)]
st=sc_.sequence_editor.sequences.new_image('frames',f'{OUT}/f0001.jpg',1,1)
for f in files[1:]: st.elements.append(f['name'])
sc_.frame_start=1; sc_.frame_end=n; sc_.render.fps=24; sc_.render.fps_base=1
sc_.render.resolution_x=W; sc_.render.resolution_y=H; sc_.render.resolution_percentage=100
sc_.view_settings.view_transform='Standard'; sc_.view_settings.look='None'
r=sc_.render; r.image_settings.file_format='FFMPEG'; r.ffmpeg.format='MPEG4'; r.ffmpeg.codec='H264'
r.ffmpeg.constant_rate_factor='HIGH'; r.ffmpeg.ffmpeg_preset='GOOD'; r.ffmpeg.audio_codec='NONE'
r.filepath=MP4; r.use_file_extension=False
bpy.ops.render.render(animation=True)
print('POST_OK',n,MP4)
