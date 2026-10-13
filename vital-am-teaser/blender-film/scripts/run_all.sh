#!/bin/bash
cd /tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad
for pass in 1 2 3; do
  ./bl/blender-4.2.23-linux-x64/blender -b --python film/render_film.py -- 1 541 960 20 /tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/film/frames >> /tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/film/render.log 2>&1
done
echo ALLDONE >> /tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/film/render.log
