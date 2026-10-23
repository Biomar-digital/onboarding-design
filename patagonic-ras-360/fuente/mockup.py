# Patagonic RAS 360 mockup: the client's hall photos with each blue panel replaced by the real rendered
# screen (perspective warp + LED glow), plus the screens that are not in the photos, at 1920x1080.
# python3 mock.py FRAMES_DIR OUT.mp4 [first] [last]
import cv2, numpy as np, sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont
SRC='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/images/17.webp'
FONT='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/mg2d/AvenirNextLTPro-Bold.otf'
FR=sys.argv[1]; OUTV=sys.argv[2]
slide=cv2.imread(SRC)
# remove the presentation's orange arrows from the photos (inpaint)
_hsv=cv2.cvtColor(slide,cv2.COLOR_BGR2HSV); _m=cv2.inRange(_hsv,(5,120,150),(22,255,255)); _m[:240]=0; _m[820:]=0
_m=cv2.dilate(_m,np.ones((7,7),np.uint8)); slide=cv2.inpaint(slide,_m,7,cv2.INPAINT_TELEA)
PLAN=cv2.imread('/home/user/onboarding-design/patagonic-ras-360/plano_pantallas_y_recorrido.png')
# photo crops in the slide and the panel quads (TL,TR,BR,BL) in slide pixels
LEFT=(33,252,882,813); RIGHT=(933,252,1894,813)
def L(x,y): return (33+x/2,252+y/2)            # picked on the 2x crop of the left photo
QUADS={
 'left':{
  'banner_lateral':[L(355,352),L(695,550),L(685,600),L(352,410)],
  'banner_frontal':[L(695,552),L(1036,548),L(1036,598),L(690,601)],
  'totem_N1':[L(1057,548),L(1161,556),L(1181,948),L(1090,882)],
  'totem_N2':[L(1200,444),L(1356,454),L(1386,1090),L(1252,982)],
  'totem_N3':[L(1424,350),L(1657,362),L(1698,1122),L(1488,1062)]},
 'right':{
  'totem_N2':[(1008,406),(1101,321),(1097,742),(990,753)],
  'totem_N3':[(1221,444),(1297,372),(1295,718),(1206,728)],
  'totem_N4':[(1401,472),(1460,421),(1457,690),(1389,697)],
  'concava':[(1568,442),(1720,447),(1713,682),(1560,678)]}}
NAMES={'banner_lateral':'Banner lateral','banner_frontal':'Banner frontal','concava':'Pantalla cóncava','cocina':'Pantalla cocina',
       'totem_R1':'Tótem R1','totem_R2':'Tótem R2'}
def frame(name,i):
    p=os.path.join(FR,name,f'{name}_{i:04d}.jpg')
    return cv2.imread(p) if os.path.exists(p) else None
def fit_aspect(img,quad):
    # crop the source to the panel's apparent aspect so nothing is squashed
    q=np.array(quad,float); w=(np.linalg.norm(q[1]-q[0])+np.linalg.norm(q[2]-q[3]))/2; h=(np.linalg.norm(q[3]-q[0])+np.linalg.norm(q[2]-q[1]))/2
    a=w/h; H,W=img.shape[:2]
    if W/H>a: nw=int(H*a); x0=(W-nw)//2; return img[:,x0:x0+nw]
    nh=int(W/a); y0=(H-nh)//2; return img[y0:y0+nh]
def place(base,img,quad,off):
    img=fit_aspect(img,quad); H,W=img.shape[:2]
    q=(np.array(quad,np.float32)-np.array(off,np.float32))
    M=cv2.getPerspectiveTransform(np.float32([[0,0],[W,0],[W,H],[0,H]]),q)
    sz=(base.shape[1],base.shape[0])
    warp=cv2.warpPerspective(img,M,sz,flags=cv2.INTER_AREA,borderMode=cv2.BORDER_CONSTANT)
    mask=cv2.warpPerspective(np.full((H,W),255,np.uint8),M,sz)
    mask=cv2.dilate(mask,np.ones((3,3),np.uint8))                     # cover the anti-aliased blue edge of the old panel
    m=(mask/255.0)[...,None]
    out=base*(1-m)+warp*m
    glow=cv2.GaussianBlur(warp.astype(np.float32)*m,(0,0),9)          # LED light spilling on the surroundings
    return np.clip(out+0.22*glow*(1-m),0,255)
def photo(side,i,scale):
    x0,y0,x1,y1=LEFT if side=='left' else RIGHT
    base=slide[y0:y1,x0:x1].astype(np.float32)
    for name,quad in QUADS[side].items():
        f=frame(name,i)
        if f is not None: base=place(base,f,quad,(x0,y0))
    base=cv2.resize(base.astype(np.uint8),None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    return base
fnt=ImageFont.truetype(FONT,22); fntT=ImageFont.truetype(FONT,30)
NAVY=(119,62,31)   # BGR of BioMar navy #1F3E77
def compose(i):
    can=np.full((1080,1920,3),NAVY,np.uint8)
    a=photo('left',i,1.03); b=photo('right',i,1.03)
    y=60; can[y:y+a.shape[0],22:22+a.shape[1]]=a; xb=22+a.shape[1]+12; can[y:y+b.shape[0],xb:xb+b.shape[1]]=b
    y2=y+a.shape[0]+78; hh=1080-y2-24
    xs=22; tiles=[]
    for name in ('cocina','totem_R2','totem_R1'):
        f=frame(name,i)
        if f is None: continue
        s=hh/f.shape[0]; f=cv2.resize(f,(int(f.shape[1]*s),hh),interpolation=cv2.INTER_AREA)
        can[y2:y2+hh,xs:xs+f.shape[1]]=f; tiles.append((name,xs)); xs+=f.shape[1]+18
    pw=1920-22-(xs+10); ph=int(PLAN.shape[0]*pw/PLAN.shape[1])
    if ph>hh: ph=hh; pw=int(PLAN.shape[1]*ph/PLAN.shape[0])
    pl=cv2.resize(PLAN,(pw,ph),interpolation=cv2.INTER_AREA); px=1920-22-pw; can[y2:y2+ph,px:px+pw]=pl
    im=Image.fromarray(cv2.cvtColor(can,cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(im)
    d.text((22,14),'Patagonic RAS 360 · mockup con el video real',font=fntT,fill=(255,255,255))
    d.text((22,y+a.shape[0]+8),'Hall principal: banner lateral, banner frontal y tótems',font=fnt,fill=(190,215,240))
    d.text((xb,y+a.shape[0]+8),'Tótems y pantalla cóncava (cuarto de cilindro)',font=fnt,fill=(190,215,240))
    for name,x in tiles: d.text((x,y2-30),NAMES[name],font=fnt,fill=(190,215,240))
    d.text((px,y2-30),'Recorrido del cardumen',font=fnt,fill=(190,215,240))
    d.text((1920-22-int(d.textlength('mismo instante en todas las pantallas',font=fnt)),22),'mismo instante en todas las pantallas',font=fnt,fill=(150,175,205))
    return cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
if __name__=='__main__':
    a=int(sys.argv[3]) if len(sys.argv)>3 else 1; b=int(sys.argv[4]) if len(sys.argv)>4 else 1440
    idx=[i for i in range(a,b+1) if os.path.exists(os.path.join(FR,'concava',f'concava_{i:04d}.jpg'))]
    if OUTV.endswith('.jpg'): cv2.imwrite(OUTV,compose(idx[0])); sys.exit()
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s','1920x1080','-r','24','-i','-',
                        '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',OUTV],stdin=subprocess.PIPE)
    for i in idx: p.stdin.write(compose(i).tobytes())
    p.stdin.close(); p.wait(); print('frames',len(idx))
