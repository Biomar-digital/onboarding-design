set -e
cd "$(dirname "$0")"
sed -e 's/v16.html/v17.html/; s/8804/8806/' v16audit.mjs > v17audit.mjs; node v17audit.mjs
rm -rf ou_under ou_above
mkdir -p v18f; true
find v18f -name 'p*.jpg' | awk -F'/p' '{n=substr($2,1,4)+0; if(n>=400) print}' | xargs -r rm -f
sed -e 's/v16.html/v17.html/; s/8800/8807/' v16.mjs > v17.mjs
node v17.mjs 400 900 1280 v18f > v18_render.log 2>&1
node v17ou.mjs under ou_under 8808
node v17ou.mjs above ou_above 8809
python3 ou_comp.py v18f
ffmpeg -y -loglevel error -framerate 24 -i v18f/p%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 19 VitalAM_previs_v18.mp4
ls -l VitalAM_previs_v18.mp4
