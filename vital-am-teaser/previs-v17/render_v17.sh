set -e
cd "$(dirname "$0")"
node v16audit.mjs
rm -rf xf_under
find v17f -name 'p*.jpg' | awk -F'/p' '{n=substr($2,1,4)+0; if(n>=195) print}' | xargs rm -f
node v16.mjs 195 800 1280 v17f > v17_render.log 2>&1
node v16xf.mjs xf_under
python3 - <<'PY'
import json
from PIL import Image
m=json.load(open('xf_under/map.json')); X0,X1=m['XF0'],m['XF1']
def smo(a,b,x):
    t=min(1,max(0,(x-a)/(b-a))); return t*t*(3-2*t)
for F,f in m['out']:
    w=smo(X0,X1,f)          # weight of the above-water pass
    a=Image.open(f'xf_under/p{F:04d}.jpg'); b=Image.open(f'v17f/p{F:04d}.jpg')
    Image.blend(a,b,w).save(f'v17f/p{F:04d}.jpg',quality=92)
print('dissolve frames',len(m['out']))
PY
ffmpeg -y -loglevel error -framerate 24 -i v17f/p%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 19 VitalAM_previs_v17.mp4
ls -l VitalAM_previs_v17.mp4
