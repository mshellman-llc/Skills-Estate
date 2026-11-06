#!/bin/sh
set -eu
map_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -f "$map_dir/skills-estate-map.html" ]; then
  map_file="$map_dir/skills-estate-map.html"
else
  map_file="$map_dir/index.html"
fi
exec python3 "$map_dir/viewer.py" --output "$map_file" --open
