#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[init-db] ensuring state directory exists..."
mkdir -p data/state

echo "[init-db] creating database schema..."
docker compose run --rm music-assistant python scripts/init_db.py

echo "[init-db] done."
