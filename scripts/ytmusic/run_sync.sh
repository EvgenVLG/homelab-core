#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$HOME/scripts/ytmusic"
VENV_PY="$BASE_DIR/venv/bin/python"
SCRIPT="$BASE_DIR/sync_ytmusic_to_lidarr.py"
LOG_DIR="$BASE_DIR/logs"
LOCK_FILE="/tmp/ytmusic_sync.lock"

mkdir -p "$LOG_DIR"

exec 200>"$LOCK_FILE"
flock -n 200 || {
  echo "[$(date)] Sync already running, exiting."
  exit 1
}

echo "========== $(date) =========="
cd "$BASE_DIR"

"$VENV_PY" "$SCRIPT"
