set -e
cd "$(dirname "$0")"
rm -rf ou_under ou_above
node v20_8840.mjs 276 342 1280 v21f > r1.log 2>&1 &
node v20_8841.mjs 343 408 1280 v21f > r2.log 2>&1 &
node v20_8842.mjs 409 474 1280 v21f > r3.log 2>&1 &
node v20_8843.mjs 475 539 1280 v21f > r4.log 2>&1 &
wait
node v20ou.mjs under ou_under 8832 &
node v20ou.mjs above ou_above 8833 &
wait
python3 ou_comp.py v21f
ffmpeg -y -loglevel error -framerate 24 -i v21f/p%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 19 VitalAM_previs_v21.mp4
ls -l VitalAM_previs_v21.mp4
python3 - <<'PY'
from PIL import Image
import numpy as np, glob
n=len(glob.glob('v21f/p*.jpg')); prev=None; d=[]
for f in range(1,n+1):
    im=np.asarray(Image.open(f'v21f/p{f:04d}.jpg').resize((160,90)).convert('L'),dtype=float)
    if prev is not None: d.append((f,round(np.abs(im-prev).mean(),1)))
    prev=im
print(n, sorted(d,key=lambda x:-x[1])[:10])
PY
