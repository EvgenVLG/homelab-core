#!/usr/bin/env bash
set -Eeuo pipefail

cd /srv/docker/music-assistant

echo "[v0.2] rebuilding..."
docker compose -f compose.yml build

echo "[v0.2] running pipeline..."
docker compose -f compose.yml run --rm music-assistant

echo
echo "[v0.2] matched_tracks.csv (first 30)"
head -30 /srv/docker/music-assistant/data/output/matched_tracks.csv || true

echo
echo "[v0.2] suspicious artist sample"
grep -Ei 'Nickelback|Aerosmith|Taylor Swift|Eminem' /srv/docker/music-assistant/data/output/matched_tracks.csv || true

echo
echo "[v0.2] summary.json"
cat /srv/docker/music-assistant/data/output/summary.json || true
