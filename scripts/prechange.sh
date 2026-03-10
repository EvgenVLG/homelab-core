#!/usr/bin/env bash
set -euo pipefail

NAME="${1:-manual}"
STAMP="$(date +%Y%m%d-%H%M%S)"
TAG="pre-${STAMP}-${NAME}"
BACKUP_DIR="/srv/docker/backups/${TAG}"

mkdir -p "${BACKUP_DIR}"

cd /srv/docker

# Commit only already-tracked changes if there are any
if ! git diff --quiet || ! git diff --cached --quiet; then
  git commit -am "checkpoint before ${NAME}" || true
fi

# Create tag only if repository has at least one commit
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git tag -a "${TAG}" -m "Pre-change snapshot: ${NAME}"
fi

# Backup repo files, excluding runtime data and git metadata
tar -czf "${BACKUP_DIR}/repo-files.tar.gz" \
  --exclude='./.git' \
  --exclude='./backups' \
  --exclude='./adguard/work' \
  --exclude='./adguard/conf' \
  --exclude='./ha/config' \
  --exclude='./homepage/data' \
  --exclude='./homepage/config' \
  --exclude='./n8n/data' \
  --exclude='./portainer/data' \
  --exclude='./reverse-proxy/caddy/data' \
  --exclude='./reverse-proxy/caddy/config' \
  .

backup_path() {
  local path="$1"
  local rel="${path#/srv/docker/}"
  local name="${rel//\//_}"

  if [ -e "$path" ]; then
    tar -czf "${BACKUP_DIR}/${name}.tar.gz" -C "/srv/docker" "$rel"
  fi
}

backup_path "/srv/docker/adguard/work"
backup_path "/srv/docker/adguard/conf"
backup_path "/srv/docker/reverse-proxy/caddy/data"
backup_path "/srv/docker/reverse-proxy/caddy/config"
backup_path "/srv/docker/portainer/data"
backup_path "/srv/docker/homepage/data"
backup_path "/srv/docker/n8n/data"
backup_path "/srv/docker/ha/config"

echo "Created snapshot: ${TAG}"
echo "Backups stored in: ${BACKUP_DIR}"
