#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[rebuild] ensuring directories exist..."
mkdir -p data/input data/output data/state

echo "[rebuild] docker compose -f compose.yml build..."
docker compose -f compose.yml build

echo "[rebuild] init db..."
docker compose -f compose.yml run --rm --entrypoint "" music-assistant python -m app.db.init_db

echo "[rebuild] run pipeline..."
docker compose -f compose.yml run --rm music-assistant run-all

echo "[rebuild] done."
