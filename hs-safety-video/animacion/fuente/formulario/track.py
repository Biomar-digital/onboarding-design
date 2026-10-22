# Track field labels per frame (template match in the label column) -> track.json
import sys, json, subprocess, numpy as np
from PIL import Image
SRC,REF,OUT=sys.argv[1:4]
W,H=1920,1080
ref=np.asarray(Image.open(REF).convert('L')).astype(np.float32)
TPL={'loc':(19,326,53,336),'date':(19,475,104,485),'type':(19,532,38,542),'incloc':(19,565,83,575),'summary':(19,592,56,602),'p_loc':(119,322,209,346),'p_inc':(143,562,243,577)}
tpl={k:ref[y0:y1,x0:x1] for k,(x0,y0,x1,y1) in TPL.items()}
raw=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
res=[]
while True:
    b=raw.stdout.read(W*H)
    if len(b)<W*H: break
    a=np.frombuffer(b,np.uint8).reshape(H,W).astype(np.float32)
    r={}
    for k,t in tpl.items():
        x0=TPL[k][0]; h,w=t.shape
        col=a[150:930,x0:x0+w] if not k.startswith('p_') else a[150:930,x0:x0+w]
        win=np.lib.stride_tricks.sliding_window_view(col,(h,w))[:,0]
        sad=np.abs(win-t).mean((1,2)); i=int(sad.argmin())
        r[k]=(150+i, round(float(sad[i]),1))
    res.append(r)
json.dump(res,open(OUT,'w')); print(len(res))
