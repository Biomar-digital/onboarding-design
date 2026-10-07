set -e
cd "$(dirname "$0")"
node v19audit.mjs
rm -rf v20f ou_under ou_above; mkdir -p v20f
for i in $(seq -f "%04g" 1 114); do cp v19f/p$i.jpg v20f/; done
node v19.mjs 115 900 1280 v20f > v20_render.log 2>&1
node v19ou.mjs under ou_under 8820
node v19ou.mjs above ou_above 8821
python3 ou_comp.py v20f
ffmpeg -y -loglevel error -framerate 24 -i v20f/p%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 19 VitalAM_previs_v20.mp4
ls -l VitalAM_previs_v20.mp4
python3 - <<'PY'
from PIL import Image
import numpy as np, glob
n=len(glob.glob('v20f/p*.jpg')); prev=None; d=[]
for f in range(1,n+1):
    im=np.asarray(Image.open(f'v20f/p{f:04d}.jpg').resize((160,90)).convert('L'),dtype=float)
    if prev is not None: d.append((f,round(np.abs(im-prev).mean(),1)))
    prev=im
print(n, sorted(d,key=lambda x:-x[1])[:10])
PY
