set -e
cd "$(dirname "$0")"
node v20audit.mjs
rm -rf ou_under ou_above v24f; mkdir -p v24f
node v24_8840.mjs 1 135 1280 v24f > r1.log 2>&1 &
node v24_8841.mjs 136 270 1280 v24f > r2.log 2>&1 &
node v24_8842.mjs 271 405 1280 v24f > r3.log 2>&1 &
node v24_8843.mjs 406 541 1280 v24f > r4.log 2>&1 &
wait
node v24ou.mjs under ou_under 8832 &
node v24ou.mjs above ou_above 8833 &
wait
python3 ou_comp.py v24f
python3 - <<'PY'
# dissolve: hold the last phone frame (6:30 on screen) with a slow push-in and cross-fade into the drone frames
from PIL import Image
last=Image.open('v24f/p0117.jpg').convert('RGB'); W,H=last.size; N=14
for k in range(N):
    f=118+k; z=1.0+0.012*(k+1); cw,ch=int(W/z),int(H/z)
    ph=last.crop(((W-cw)//2,(H-ch)//2,(W-cw)//2+cw,(H-ch)//2+ch)).resize((W,H),Image.LANCZOS)
    a=(k+1)/(N+1); a=a*a*(3-2*a)
    Image.blend(ph,Image.open(f'v24f/p{f:04d}.jpg').convert('RGB'),a).save(f'v24f/p{f:04d}.jpg',quality=94)
PY
ffmpeg -y -loglevel error -framerate 24 -i v24f/p%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 17 VitalAM_previs_v24.mp4
ls -l VitalAM_previs_v24.mp4
