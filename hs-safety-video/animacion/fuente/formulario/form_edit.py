# Edit of the Workday form recording: Windows-style layout, follow-zoom per field, orange highlight,
# click pulses, call-out cards, and site names replaced with [Location].
# python3 form_edit.py SRC.mp4 track.json taskbar.png OUT.mp4 [preview_times]
import sys, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC,TRK,TB,OUT=sys.argv[1:5]; ONLY=[float(x) for x in sys.argv[5].split(',')] if len(sys.argv)>5 else None
W,H,FPS=1920,1080,30
HERE=__file__.rsplit('/',1)[0]
T=json.load(open(TRK)); N=len(T)
tb=Image.open(TB).convert('RGB')
ROW_FILL=np.load(f'{HERE}/row926_med.npy')               # median of src row 926 over the clip
ORANGE=(221,105,40); BLUE=(31,62,119); HL=(246,214,120); ACC=(234,179,24)
ROB=f'{HERE}/fonts/roboto-latin-400-normal.woff'
F_T=ImageFont.truetype(f'{HERE}/fonts/AvenirNextLTPro-Bold.otf',30)
F_B=ImageFont.truetype(f'{HERE}/fonts/AvenirNextLTPro-Regular.otf',24)
ease=lambda x:(lambda x:x*x*(3-2*x))(min(1.0,max(0.0,x)))
HDR=243                                            # dialog content starts below the sticky title bar (src y)

# ---------- tracked anchors (src y), smoothed, with last-good fallback ----------
def series(key,thr):
    out=[];last=None
    for r in T:
        y,s=r[key]
        if s<thr: last=y
        out.append(last)
    return out
ANCH={k:series(k,13) for k in ['loc','date','type','incloc','summary']}
def smooth(v,k=0.35):
    o=[];c=None
    for x in v:
        if x is None: o.append(c); continue
        c=x if c is None or abs(x-c)>60 else c+(x-c)*k; o.append(c)
    return o
SANCH={k:smooth(v) for k,v in ANCH.items()}
def pill_pos(i):
    """(loc_y, inc_y) of the pill text tops in src coords, or None"""
    pl,sl=T[i]['p_loc']; pi,si=T[i]['p_inc']
    loc=pl if sl<12 else None; inc=pi if si<12 else None
    t=i/FPS
    if t>15.0:                                     # while scrolling, derive the hidden one from the other
        if loc is None and inc is not None: loc=inc-240
        if inc is None and loc is not None: inc=loc+240
    return loc,inc

# ---------- [Location] patches ----------
def text_img(s,size,color):
    S=8; f=ImageFont.truetype(ROB,size*S); bb=f.getbbox(s)
    im=Image.new('L',(bb[2]+4*S,int(size*S*1.6)),0); ImageDraw.Draw(im).text((2*S,0),s,font=f,fill=255)
    im=im.resize((im.width//S,im.height//S),Image.BOX); return im,(bb[1]//S)
def patch(img,x0,y0,x1,y1,s,cap_top,tx):
    a=np.asarray(img); reg=a[max(y0,HDR):y1,x0:x1]
    if reg.size==0: return
    lum=reg.mean(2); bg=np.median(reg[lum>lum.max()-25],0) if (lum>lum.max()-25).any() else np.array([243,243,243])
    lay=Image.new('RGB',(x1-x0,y1-y0),tuple(int(v) for v in bg))
    m,off=text_img(s,7.45,0); col=Image.new('RGB',m.size,(40,40,40))
    lay.paste(col,(tx-x0, cap_top-y0-off-1),m)
    if y0<HDR: lay=lay.crop((0,HDR-y0,lay.width,lay.height)); y0=HDR
    if lay.height>0: img.paste(lay,(x0,y0))
def anonymise(img,i):
    loc,inc=pill_pos(i)
    if loc is not None and loc+20>HDR: patch(img,118,loc+2,215,loc+20,'[Location]',loc+8,122)
    if inc is not None and inc+14>HDR: patch(img,143,inc+1,241,inc+14,'[Location] - Production',inc+4,146)

# ---------- sections ----------
CARDS={'loc':('Location','In which business unit and site did the incident happen?'),
 'date':('Incident date and time','When did the incident happen?'),
 'type':('Incident type','What type of incident?'),
 'incloc':('Incident location','In what area did the incident happen?'),
 'summary':('Summary','Describe what happened and leave out names and other personal information.'),
 'attach':('Attachments','Add photos if it is safe and relevant.'),
 'submit':('Submit','Send your report.')}
SECT=[('loc',0.45,2.9),('date',2.9,4.7),('type',4.7,9.4),('incloc',9.4,13.0),('summary',13.0,15.1),('attach',16.8,21.0),('submit',21.0,25.7)]
CLICKS=[(1.55,'loc',(185,6)),(5.25,'type',(205,6)),(10.25,'incloc',(205,4)),(13.05,'summary',(310,40))]
def geom(name,i):
    """highlight box (src coords) and zoom target (z,cx,cy in src coords)"""
    if name in ANCH:
        L=SANCH[name][i]
        if L is None: return None
        if name=='loc':     return (8,L-12,266,L+(27 if T[i]['p_loc'][1]<12 else 18)),(2.2,300,L+90)
        if name=='date':    return (8,L-11,266,L+50),(2.2,300,L+40)
        if name=='type':    return (8,L-12,290,(ANCH['incloc'][i]-16) if ANCH['incloc'][i] else L+35),(2.0,320,L+110)
        if name=='incloc':  return (8,L-12,290,L+20),(2.0,320,L+70)
        if name=='summary': return (8,L-12,503,L+86),(1.9,420,L+40)
    if name=='attach': return (820,662,1092,756),(1.6,960,720)
    if name=='submit': return (14,891,90,926),(2.0,330,820)
def active(t):
    for n,a,b in SECT:
        if a<=t<b: return n,a,b
    return None,0,0
ease3=lambda x:(lambda x:4*x*x*x if x<.5 else 1-(-2*x+2)**3/2)(min(1.0,max(0.0,x)))
FULL=(1.0,W/2,H/2+148)
def sect_target(name):
    n=[k for k in SECT if k[0]==name][0]; mid=int((n[1]+n[2])/2*FPS)
    if name in ANCH:                                 # framing fixed for the whole section (no per-frame follow)
        ys=[ANCH[name][j] for j in range(int(n[1]*FPS),min(N,int(n[2]*FPS))) if ANCH[name][j] is not None]
        L=int(np.median(ys)); SANCH[name][mid]=L
    return geom(name,mid)[1]
KEYS=[]                                              # (start,end,target)
prev_end=0.0
for n,a0,b0 in SECT:
    if a0>prev_end+1e-6: KEYS.append((prev_end,a0,FULL))
    KEYS.append((a0,b0,sect_target(n))); prev_end=b0
KEYS.append((prev_end,1e9,FULL))
TR=0.8
def clampc(z,cx,cy):
    cw,ch=W/z,H/z; cy-=148
    return z,min(max(cx,cw/2),W-cw/2),min(max(cy,ch/2),H-ch/2)+148
def zoom_at(t,i):
    for k,(a0,b0,tg) in enumerate(KEYS):
        if t<b0: break
    A=clampc(*tg)
    if k+1<len(KEYS) and t>b0-TR/2:
        B=clampc(*KEYS[k+1][2]); u=ease3((t-(b0-TR/2))/TR)
    elif k>0 and t<a0+TR/2:
        B=A; A=clampc(*KEYS[k-1][2]); u=ease3((t-(a0-TR/2))/TR)
    else: return A
    z=np.exp(np.log(A[0])*(1-u)+np.log(B[0])*u)
    # move the window so the framing glides without overshoot
    return z,A[1]*(1-u)+B[1]*u,A[2]*(1-u)+B[2]*u
def card(name,alpha):
    title,body=CARDS[name]; wmax=520
    words=body.split(); lines=[];cur=''
    for w_ in words:
        s=(cur+' '+w_).strip()
        if F_B.getlength(s)>wmax-48 and cur: lines.append(cur); cur=w_
        else: cur=s
    lines.append(cur)
    tw=max(F_T.getlength(title),*(F_B.getlength(l) for l in lines))+56; th=24+38+len(lines)*32+18
    im=Image.new('RGBA',(int(tw)+40,int(th)+40),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((20,20,20+tw,20+th),16,fill=(255,255,255,255),outline=(214,222,232,255),width=2)
    d.rounded_rectangle((20,20,28,20+th),4,fill=ACC+(255,))
    d.text((46,40),title,font=F_T,fill=BLUE); y=40+40
    for l in lines: d.text((46,y),l,font=F_B,fill=(51,51,51)); y+=32
    if alpha<1: im.putalpha(im.getchannel('A').point(lambda v:int(v*alpha)))
    return im
CARD_CACHE={k:card(k,1) for k in CARDS}
def render(i,src):
    t=i/FPS
    img=Image.fromarray(src.copy()); anonymise(img,i)
    a=np.asarray(img); top=a[148:927]; fill=np.repeat(ROW_FILL[None],1032-len(top),0)   # cursor-free row, no streaks
    fr=Image.new('RGB',(W,H)); fr.paste(Image.fromarray(np.concatenate([top,fill])),(0,0)); fr.paste(tb,(0,1032))
    z,cx,cy=zoom_at(t,i); cy-=148                 # to formatted coords
    cw,ch=W/z,H/z; x0=min(max(cx-cw/2,0),W-cw); y0=min(max(cy-ch/2,0),H-ch)
    if z>1.001: fr=fr.resize((W,H),Image.LANCZOS,box=(x0,y0,x0+cw,y0+ch))
    S=lambda x,y:((x-x0)*z,(y-148-y0)*z)
    base=fr.convert('RGBA'); lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    n,a0,b0=active(t)
    if n:
        g=geom(n,i)
        al=ease((t-a0-0.25)/0.3)*(1-ease((t-(b0-0.3))/0.25))
        if g and al>0:
            bx=g[0]; p0=S(bx[0],bx[1]); p1=S(bx[2],bx[3]); pad=6
            r=[p0[0]-pad,p0[1]-pad,p1[0]+pad,p1[1]+pad]
            wipe=ease3((t-a0-0.25)/0.35); rx=r[0]+(r[2]-r[0])*wipe
            if rx>r[0]+2:
                xa,ya,xb,yb=[int(round(v)) for v in (max(0,r[0]),max(0,r[1]),min(W,rx),min(H,r[3]))]
                if xb>xa and yb>ya:
                    reg=np.asarray(base)[ya:yb,xa:xb,:3].astype(np.float32)
                    out=reg*(1-al+al*np.array(HL,np.float32)/255)          # multiply blend
                    m=Image.new('L',(xb-xa,yb-ya),0); ImageDraw.Draw(m).rounded_rectangle((0,0,xb-xa-1,yb-ya-1),6,fill=255)
                    patchimg=Image.fromarray(out.clip(0,255).astype(np.uint8)).convert('RGBA')
                    base.paste(patchimg,(xa,ya),m)
            c=CARD_CACHE[n]
            if al<1: c=c.copy(); c.putalpha(c.getchannel('A').point(lambda v:int(v*al)))
            cxp=int(r[2]+22); cyp=int((r[1]+r[3])/2-c.height/2)
            if cxp+c.width>W-20: cxp=int(max(20,r[0])); cyp=int(r[1]-c.height-6) if n=='submit' else int(r[3]+6)
            cyp=max(10,min(H-60-c.height,cyp)); base.alpha_composite(c,(cxp+int((1-al)*16),cyp))
    for tc,fld,(dx,dy) in CLICKS:
        p=(t-tc)/0.9
        if 0<p<1:
            L=SANCH[fld][i]
            if L is None: continue
            c=S(dx,L+dy)
            for k in (0,0.33):
                q=p-k
                if 0<q<1:
                    rr=10+42*ease(q); d.ellipse((c[0]-rr,c[1]-rr,c[0]+rr,c[1]+rr),outline=ACC+(int(240*(1-q)),),width=5)
    base.alpha_composite(lay); return base.convert('RGB')

raw=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
if ONLY:
    want={int(round(x*FPS)):x for x in ONLY}; i=0
    while want:
        b=raw.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        if i in want: render(i,np.frombuffer(b,np.uint8).reshape(H,W,3)).save(f'{OUT}_{want.pop(i)}.jpg',quality=90)
        i+=1
    sys.exit()
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',SRC,
   '-map','0:v','-map','1:a?','-c:v','libx264','-crf','12','-preset','slow','-tune','stillimage','-pix_fmt','yuv420p','-c:a','copy','-shortest',OUT],stdin=subprocess.PIPE)
i=0
while True:
    b=raw.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    enc.stdin.write(render(i,np.frombuffer(b,np.uint8).reshape(H,W,3)).tobytes()); i+=1
    if i%100==0: print(i,flush=True)
enc.stdin.close(); enc.wait(); print('ok',i)
