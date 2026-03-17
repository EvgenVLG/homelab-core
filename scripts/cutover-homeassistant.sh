#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/docker"
OLD_DIR="$ROOT/ha"
NEW_DIR="$ROOT/compose/core"
ENV_FILE="$ROOT/env/.env"
TS="$(date '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$ROOT/backups/cutover-homeassistant-$TS"

mkdir -p "$BACKUP_DIR"

echo "[1/10] Saving current docker inspect..."
docker inspect homeassistant > "$BACKUP_DIR/homeassistant.inspect.json"

echo "[2/10] Saving current logs snapshot..."
docker logs --tail 300 homeassistant > "$BACKUP_DIR/homeassistant.logs.txt" 2>&1 || true

echo "[3/10] Backing up old compose..."
cp "$OLD_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose.homeassistant.old.yml"

echo "[4/10] Showing current homeassistant container..."
docker ps --filter "name=^homeassistant$"

echo "[5/10] Stopping old homeassistant from legacy compose..."
docker compose -f "$OLD_DIR/docker-compose.yml" down

echo "[6/10] Starting homeassistant from structured core compose..."
docker compose \
  -f "$NEW_DIR/docker-compose.yml" \
  --env-file "$ENV_FILE" \
  up -d --no-deps homeassistant

echo "[7/10] Waiting briefly..."
sleep 12

echo "[8/10] Showing new homeassistant status..."
docker ps --filter "name=^homeassistant$"

echo "[9/10] Recent logs..."
docker logs --tail 120 homeassistant || true

echo "[10/10] Done."
echo
echo "Verify manually:"
echo "  - Home Assistant UI"
echo "  - https://ha.home.arpa"
echo
echo "Backup saved in: $BACKUP_DIR"
