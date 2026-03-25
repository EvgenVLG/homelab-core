#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[build] ensuring directories exist..."
mkdir -p data/input data/output data/state

echo "[build] building docker image..."
docker compose -f compose.yml build

echo "[build] done."
