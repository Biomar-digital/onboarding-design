# Recording -> same layout as the 4A laptop screen: page (rows 148-926, last clean row extended) + Windows taskbar.
import sys, subprocess, numpy as np
from PIL import Image
SRC,OUT,TB=sys.argv[1:4]
W,H=1920,1080
tb=np.asarray(Image.open(TB).convert('RGB'))
_r=subprocess.run(['ffmpeg','-v','error','-i',SRC,'-vf','fps=5,crop=1920:1:0:926','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
MED=np.median(np.frombuffer(_r,np.uint8).reshape(-1,1920,3),0).astype(np.uint8)
raw=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i',SRC,
   '-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p','-c:a','copy','-shortest',OUT],stdin=subprocess.PIPE)
n=0
while True:
    b=raw.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    a=np.frombuffer(b,np.uint8).reshape(H,W,3)
    row=a[926].copy(); dev=np.abs(row.astype(int)-MED.astype(int)).max(1)>30
    if dev.sum()<200: row[dev]=MED[dev]                 # drop the cursor; keep full-row changes (loading overlay)
    top=a[148:927]; fill=np.repeat(row[None],1032-len(top),0)
    enc.stdin.write(np.concatenate([top,fill,tb]).tobytes()); n+=1
enc.stdin.close(); enc.wait(); print('frames',n)
