#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/srv/docker"

echo "[1/7] Checking required commands..."
for cmd in docker git; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd"
    exit 1
  fi
done

echo "[2/7] Ensuring directory structure exists..."
mkdir -p \
  "$ROOT_DIR/compose/core" \
  "$ROOT_DIR/compose/media" \
  "$ROOT_DIR/compose/automation" \
  "$ROOT_DIR/compose/monitoring" \
  "$ROOT_DIR/env" \
  "$ROOT_DIR/scripts" \
  "$ROOT_DIR/docs" \
  "$ROOT_DIR/data" \
  "$ROOT_DIR/backups"

echo "[3/7] Ensuring env file exists..."
if [ ! -f "$ROOT_DIR/env/.env" ]; then
  if [ -f "$ROOT_DIR/env/.env.example" ]; then
    cp "$ROOT_DIR/env/.env.example" "$ROOT_DIR/env/.env"
    echo "Created $ROOT_DIR/env/.env from template. Edit it before production use."
  else
    touch "$ROOT_DIR/env/.env"
  fi
fi

echo "[4/7] Creating shared docker network if missing..."
if ! docker network inspect homelab >/dev/null 2>&1; then
  docker network create homelab
fi

echo "[5/7] Checking git repo..."
if [ ! -d "$ROOT_DIR/.git" ]; then
  echo "No git repo detected in $ROOT_DIR"
  echo "Run: git init"
else
  echo "Git repo found."
fi

echo "[6/7] Summary..."
find "$ROOT_DIR" -maxdepth 2 -type d | sort

echo "[7/7] Done."
echo "Next:"
echo "  1. Edit /srv/docker/env/.env"
echo "  2. Add compose files under compose/core"
echo "  3. Run docker compose from the appropriate directory"
