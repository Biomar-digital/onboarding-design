set -e
cd "$(dirname "$0")"
node v18audit.mjs
rm -rf v19f ou_under ou_above
node v18.mjs 1 900 1280 v19f > v19_render.log 2>&1
node v18ou.mjs under ou_under 8814
node v18ou.mjs above ou_above 8815
python3 ou_comp.py v19f
ffmpeg -y -loglevel error -framerate 24 -i v19f/p%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 19 VitalAM_previs_v19.mp4
ls -l VitalAM_previs_v19.mp4
