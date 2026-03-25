#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/docker"
OLD_DIR="$ROOT/n8n"
NEW_DIR="$ROOT/compose/core"
ENV_FILE="$ROOT/env/.env"
TS="$(date '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$ROOT/backups/cutover-n8n-$TS"

mkdir -p "$BACKUP_DIR"

echo "[1/10] Saving current docker inspect..."
docker inspect n8n > "$BACKUP_DIR/n8n.inspect.json"

echo "[2/10] Saving current logs snapshot..."
docker logs --tail 300 n8n > "$BACKUP_DIR/n8n.logs.txt" 2>&1 || true

echo "[3/10] Backing up old compose..."
cp "$OLD_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose.n8n.old.yml"

echo "[4/10] Capturing current env snapshot..."
docker inspect n8n --format '{{range .Config.Env}}{{println .}}{{end}}' \
  > "$BACKUP_DIR/n8n.env.txt"

echo "[5/10] Showing currently running n8n container..."
docker ps --filter "name=^n8n$"

echo "[6/10] Stopping old n8n from legacy compose..."
docker compose -f "$OLD_DIR/docker-compose.yml" down

echo "[7/10] Starting n8n from structured core compose..."
docker compose \
  -f "$NEW_DIR/docker-compose.yml" \
  --env-file "$ENV_FILE" \
  up -d --no-deps n8n

echo "[8/10] Waiting briefly..."
sleep 8

echo "[9/10] Showing new n8n status..."
docker ps --filter "name=^n8n$"
docker logs --tail 120 n8n || true

echo "[10/10] Done."
echo
echo "Verify manually:"
echo "  - n8n UI through Caddy"
echo "  - any webhook-dependent workflow you care about"
echo
echo "Backup saved in: $BACKUP_DIR"
