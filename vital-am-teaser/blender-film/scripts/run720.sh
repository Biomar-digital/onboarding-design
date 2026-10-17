#!/bin/sh
# 720p final: resumable render loop (skips frames already on disk), then post + copy to the repo
cd /tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/film
OUT=$PWD/hd720v7
for i in 1 2 3 4 5 6; do
  n=$(ls $OUT/f????.jpg 2>/dev/null | wc -l)
  [ "$n" -ge 589 ] && break
  ../bl/blender-4.2.23-linux-x64/blender -b film.blend -P render_film.py -- 1 589 1280 16 $OUT >> hd720v7.log 2>&1
done
rm -rf hd720v7_out; python3 post.py hd720v7 hd720v7_out film_720p_v7.mp4 >> hd720v7.log 2>&1
cp film_720p_v7.mp4 /home/user/onboarding-design/vital-am-teaser/blender-film/ && echo DONE720 >> hd720v7.log
