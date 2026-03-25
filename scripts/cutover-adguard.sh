#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/docker"
OLD_DIR="$ROOT/adguard"
NEW_DIR="$ROOT/compose/core"
ENV_FILE="$ROOT/env/.env"
TS="$(date '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$ROOT/backups/cutover-adguard-$TS"

mkdir -p "$BACKUP_DIR"

echo "[1/10] Saving current docker inspect..."
docker inspect adguard > "$BACKUP_DIR/adguard.inspect.json"

echo "[2/10] Saving current logs snapshot..."
docker logs --tail 300 adguard > "$BACKUP_DIR/adguard.logs.txt" 2>&1 || true

echo "[3/10] Backing up old compose..."
cp "$OLD_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose.adguard.old.yml"

echo "[4/10] Showing current adguard container..."
docker ps --filter "name=^adguard$"

echo "[5/10] Stopping old adguard from legacy compose..."
docker compose -f "$OLD_DIR/docker-compose.yml" down

echo "[6/10] Starting adguard from structured core compose..."
docker compose \
  -f "$NEW_DIR/docker-compose.yml" \
  --env-file "$ENV_FILE" \
  up -d --no-deps adguard

echo "[7/10] Waiting briefly..."
sleep 8

echo "[8/10] Showing new adguard status..."
docker ps --filter "name=^adguard$"

echo "[9/10] Recent logs..."
docker logs --tail 120 adguard || true

echo "[10/10] Done."
echo
echo "Verify manually:"
echo "  - DNS on port 53"
echo "  - AdGuard UI on :3001"
echo "  - https://adguard.home.arpa via Caddy"
echo
echo "Backup saved in: $BACKUP_DIR"
