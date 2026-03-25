#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/docker"
OLD_DIR="$ROOT/homepage"
NEW_DIR="$ROOT/compose/core"
ENV_FILE="$ROOT/env/.env"
TS="$(date '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$ROOT/backups/cutover-homepage-$TS"

mkdir -p "$BACKUP_DIR"

echo "[1/9] Saving current docker inspect..."
docker inspect homepage > "$BACKUP_DIR/homepage.inspect.json"

echo "[2/9] Saving current logs snapshot..."
docker logs --tail 200 homepage > "$BACKUP_DIR/homepage.logs.txt" 2>&1 || true

echo "[3/9] Backing up old compose..."
cp "$OLD_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose.homepage.old.yml"

echo "[4/9] Showing currently running homepage container..."
docker ps --filter "name=^homepage$"

echo "[5/9] Stopping old homepage from legacy compose..."
docker compose -f "$OLD_DIR/docker-compose.yml" down

echo "[6/9] Starting homepage from structured core compose..."
docker compose \
  -f "$NEW_DIR/docker-compose.yml" \
  --env-file "$ENV_FILE" \
  up -d --no-deps homepage

echo "[7/9] Waiting briefly..."
sleep 5

echo "[8/9] Showing new homepage status..."
docker ps --filter "name=^homepage$"
docker logs --tail 100 homepage || true

echo "[9/9] Done."
echo
echo "Verify manually:"
echo "  - http://SERVER_IP:3000"
echo "  - your Caddy route(s) for homepage"
echo
echo "Backup saved in: $BACKUP_DIR"
