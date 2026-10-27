# Mockup from the concave screen's video only: concave = real video; the other screens show crops of the same
# video (different regions, each with its screen's aspect) as a provisional stand-in until they are rendered.
# python3 mock_video.py CONCAVA.mp4 OUT.mp4
import sys, os, subprocess, cv2, numpy as np
src,outv=sys.argv[1],sys.argv[2]
sys.argv=[sys.argv[0],'/nonexistent',outv]; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import mock
from PIL import Image, ImageDraw
# crop windows on the 1008x840 concave frame (x0,y0,w,h) chosen where the schools usually swim
CROPS={'banner_frontal':(0,430,1008,252),'banner_lateral':(0,470,1008,126),
       'totem_N1':(60,180,220,660),'totem_N2':(300,180,220,660),'totem_N3':(540,180,220,660),'totem_N4':(780,180,220,660),
       'cocina':(0,300,1008,504),'totem_R1':(150,250,280,560),'totem_R2':(600,250,280,560)}
cur={}
def frame(name,i):
    f=cur['f']
    if name=='concava': return f
    H,W=f.shape[:2]; x,y,w,h=CROPS[name]; s=W/1008.0
    return f[int(y*s):int((y+h)*s),int(x*s):int((x+w)*s)]
mock.frame=frame
cap=cv2.VideoCapture(src); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s','1920x1080','-r','24','-i','-',
                    '-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p',outv],stdin=subprocess.PIPE)
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    cur['f']=f; img=mock.compose(i+1)
    im=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(im)
    d.multiline_text((1100,900),'Pantalla cóncava: render real.\nResto: provisorio, recortes del\nmismo video hasta renderizarlas.',font=mock.fnt,fill=(150,175,205),spacing=6)
    p.stdin.write(cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR).tobytes()); i+=1
    if i%300==0: print('frames',i,'/',n,flush=True)
p.stdin.close(); p.wait(); print('DONE',i)
