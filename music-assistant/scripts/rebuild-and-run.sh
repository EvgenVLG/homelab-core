#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[rebuild] ensuring directories exist..."
mkdir -p data/input data/output data/state

echo "[rebuild] docker compose build..."
docker compose build

echo "[rebuild] init db..."
docker compose run --rm music-assistant python scripts/init_db.py

echo "[rebuild] run pipeline..."
docker compose run --rm music-assistant run-all

echo "[rebuild] done."
echo
echo "Check outputs:"
echo "  head -30 data/output/matched_tracks.csv"
echo "  cat data/output/summary.json"
