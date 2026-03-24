#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[init-db] ensuring state directory exists..."
mkdir -p data/state

echo "[init-db] creating database schema..."
docker compose -f compose.yml run --rm --entrypoint "" music-assistant python -m app.db.init_db

echo "[init-db] done."
