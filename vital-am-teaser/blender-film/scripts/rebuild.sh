#!/bin/bash
# full look rebuild: film_base.blend -> film.blend
cd "$(dirname "$0")"; B=../bl/blender-4.2.23-linux-x64/blender
$B -b -P look.py 2>&1 | grep -E "LOOK_SAVED|Traceback"
$B -b -P water_fx.py 2>&1 | grep -E "FX_OK|Traceback"
$B -b -P hf_assets.py 2>&1 | grep -E "HF_OK|Traceback"
$B -b -P hand_add.py -- 0.55 0.44 2>&1 | grep -E "HAND_OK|Traceback"
$B -b -P grip_add.py 2>&1 | grep -E "GRIP_OK|Traceback"
