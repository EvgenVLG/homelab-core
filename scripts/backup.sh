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

BACKUP_SOURCE="${BACKUP_SOURCE:-/srv/docker}"
BACKUP_DEST="${BACKUP_DEST:-/storage/backups}"

TIMESTAMP="$(date +%F_%H-%M-%S)"
ARCHIVE_NAME="docker-config-backup_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_DEST}/${ARCHIVE_NAME}"

mkdir -p "$BACKUP_DEST"

if [[ ! -w "$BACKUP_DEST" ]]; then
  echo "ERROR: backup destination is not writable: $BACKUP_DEST"
  ls -ld "$BACKUP_DEST" || true
  exit 1
fi

tar \
  --exclude="${BACKUP_SOURCE}/secrets" \
  --exclude="${BACKUP_SOURCE}/.git" \
  --exclude="${BACKUP_SOURCE}/*.log" \
  --exclude="${BACKUP_SOURCE}/tmp" \
  -czf "$ARCHIVE_PATH" \
  -C "$BACKUP_SOURCE" .

echo "Backup created: $ARCHIVE_PATH"
ls -lh "$ARCHIVE_PATH"
