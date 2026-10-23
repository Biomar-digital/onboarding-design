from PIL import Image, ImageDraw, ImageFont
import sys
d=sys.argv[1]; out=sys.argv[2]
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
rows=[(['banner_frontal','totem_N1','totem_N2','totem_N3','totem_N4','concava','cocina'],420),(['totem_R2','totem_R1','banner_lateral'],300)]
tiles=[]
for ns,h in rows:
    t=[]
    for n in ns:
        im=Image.open(f'{d}/{n}.png').convert('RGB'); t.append((n,im.resize((int(im.width*h/im.height),h))))
    tiles.append((t,h))
W=max(sum(i.width+20 for _,i in t) for t,_ in tiles)+20
sheet=Image.new('RGB',(W,sum(h+50 for _,h in tiles)+20),(20,24,28)); dr=ImageDraw.Draw(sheet); y=40
for t,h in tiles:
    x=20
    for n,i in t: sheet.paste(i,(x,y)); dr.text((x,y-26),n,fill=(230,230,230),font=f); x+=i.width+20
    y+=h+50
sheet.save(out,quality=90)
