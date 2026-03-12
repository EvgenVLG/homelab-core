#!/bin/bash

cd /srv/docker || exit

git add .

if ! git diff --cached --quiet; then
    git commit -m "auto: homelab config update $(date '+%Y-%m-%d %H:%M')"
    git push
fi
