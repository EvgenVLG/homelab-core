#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== summary.json ==="
cat data/output/summary.json || true
echo

echo "=== matched_tracks.csv (first 30) ==="
head -30 data/output/matched_tracks.csv || true
echo

echo "=== unmatched_history.csv (first 30) ==="
head -30 data/output/unmatched_history.csv || true
echo

echo "=== playlists ==="
find data/output/playlists -maxdepth 1 -type f | sort || true
