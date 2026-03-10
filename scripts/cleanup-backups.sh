#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/srv/docker/backups"

# Keep newest 14 backup directories, delete older ones
find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d | sort | head -n -14 | xargs -r rm -rf

# Keep newest 20 pre-* git tags, delete older local pre-change tags
OLD_TAGS=$(git -C /srv/docker tag --list 'pre-*' | sort | head -n -20 || true)
if [ -n "${OLD_TAGS:-}" ]; then
  echo "$OLD_TAGS" | xargs -r -n 1 git -C /srv/docker tag -d
fi
