#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="/srv/docker/secrets/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: secrets file not found: $ENV_FILE"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

BACKUP_DEST="${BACKUP_DEST:-/storage/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

if [[ ! -d "$BACKUP_DEST" ]]; then
  echo "ERROR: backup destination does not exist: $BACKUP_DEST"
  exit 1
fi

find "$BACKUP_DEST" -type f -name "*.tar.gz" -mtime +"$RETENTION_DAYS" -print -delete

echo "Prune complete"

