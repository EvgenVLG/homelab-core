#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[run-all] starting pipeline..."
docker compose -f compose.yml run --rm music-assistant run-all

echo "[run-all] pipeline finished."
