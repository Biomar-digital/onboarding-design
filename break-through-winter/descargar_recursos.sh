#!/bin/sh
# Recursos de Poly Haven (CC0) para escena_hielo.py. Uso: sh descargar_recursos.sh CARPETA
D=${1:-recursos}; mkdir -p "$D/textures"; cd "$D" || exit 1
B=https://dl.polyhaven.org/file/ph-assets
curl -sSLO $B/HDRIs/hdr/4k/winter_lake_01_4k.hdr
for t in diff nor_gl rough disp; do curl -sSLO $B/Textures/jpg/2k/snow_02/snow_02_${t}_2k.jpg; done
curl -sSLO $B/Models/blend/1k/fir_tree_01/fir_tree_01_1k.blend
curl -sS https://api.polyhaven.com/files/fir_tree_01 | python3 -c "
import json,sys; d=json.load(sys.stdin)
for p,v in d['blend']['1k']['blend']['include'].items(): print(p, v['url'])" | while read p u; do curl -sSL -o "$p" "$u"; done
# hielo negro de lago (ambientCG, CC0)
curl -sSL -o Ice003.zip "https://ambientcg.com/get?file=Ice003_2K-JPG.zip" && unzip -oq Ice003.zip 'Ice003_2K-JPG_*.jpg' && rm Ice003.zip
