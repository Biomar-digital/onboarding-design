#!/bin/bash
# Supervisor: renders 1 minute (frames 1-1440) of all 10 screens; re-launches Blender until every frame exists.
S=/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/salmon
OUT=$S/render1min
cd $S
while true; do
  n=$(find $OUT -name '*.jpg' 2>/dev/null | wc -l)
  echo "$(date '+%F %T') jpgs=$n" >> $S/render_min_progress.log
  [ "$n" -ge 14400 ] && { echo "$(date '+%F %T') COMPLETE" >> $S/render_min_progress.log; break; }
  RAS_FRAMEMAJOR=1 RAS_SAMPLES=10 RAS_JPG=1 RAS_STATIC_FROM=7 RAS_FRAMES=1-1440 \
    ../bl/blender-4.2.23-linux-x64/blender -b --factory-startup -P hall.py -- $OUT 0 1440 0.36 > $S/render_min_blender.log 2>&1
  sleep 5
done
