#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/docker"
OLD_DIR="$ROOT/reverse-proxy"
NEW_DIR="$ROOT/compose/core"
ENV_FILE="$ROOT/env/.env"
TS="$(date '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$ROOT/backups/cutover-caddy-$TS"

mkdir -p "$BACKUP_DIR"

echo "[1/10] Saving current docker inspect..."
docker inspect caddy > "$BACKUP_DIR/caddy.inspect.json"

echo "[2/10] Saving current logs snapshot..."
docker logs --tail 400 caddy > "$BACKUP_DIR/caddy.logs.txt" 2>&1 || true

echo "[3/10] Backing up old compose and Caddyfile..."
cp "$OLD_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose.caddy.old.yml"
cp "$OLD_DIR/Caddyfile" "$BACKUP_DIR/Caddyfile"

echo "[4/10] Showing current caddy container..."
docker ps --filter "name=^caddy$"

echo "[5/10] Stopping old caddy from legacy compose..."
docker compose -f "$OLD_DIR/docker-compose.yml" down

echo "[6/10] Starting caddy from structured core compose..."
docker compose \
  -f "$NEW_DIR/docker-compose.yml" \
  --env-file "$ENV_FILE" \
  up -d --no-deps caddy

echo "[7/10] Waiting briefly..."
sleep 6

echo "[8/10] Showing new caddy status..."
docker ps --filter "name=^caddy$"

echo "[9/10] Recent logs..."
docker logs --tail 120 caddy || true

echo "[10/10] Done."
echo
echo "Now verify routes manually and with curl."
echo "Backup saved in: $BACKUP_DIR"
