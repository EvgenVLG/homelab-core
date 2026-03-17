#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/docker"
OLD_DIR="$ROOT/portainer"
NEW_DIR="$ROOT/compose/core"
ENV_FILE="$ROOT/env/.env"
TS="$(date '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$ROOT/backups/cutover-portainer-$TS"

mkdir -p "$BACKUP_DIR"

echo "[1/9] Saving current docker inspect..."
docker inspect portainer > "$BACKUP_DIR/portainer.inspect.json"

echo "[2/9] Saving current logs snapshot..."
docker logs --tail 200 portainer > "$BACKUP_DIR/portainer.logs.txt" 2>&1 || true

echo "[3/9] Backing up old compose..."
cp "$OLD_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose.portainer.old.yml"

echo "[4/9] Showing currently running portainer container..."
docker ps --filter "name=^portainer$"

echo "[5/9] Stopping old portainer from legacy compose..."
docker compose -f "$OLD_DIR/docker-compose.yml" down

echo "[6/9] Starting portainer from structured core compose..."
docker compose \
  -f "$NEW_DIR/docker-compose.yml" \
  --env-file "$ENV_FILE" \
  up -d --no-deps portainer

echo "[7/9] Waiting briefly..."
sleep 5

echo "[8/9] Showing new portainer status..."
docker ps --filter "name=^portainer$"
docker logs --tail 100 portainer || true

echo "[9/9] Done."
echo
echo "Verify manually:"
echo "  - Portainer UI via your Caddy route"
echo
echo "Backup saved in: $BACKUP_DIR"
