#!/usr/bin/env bash
set -euo pipefail

NAME="${1:-manual}"
STAMP="$(date +%Y%m%d-%H%M%S)"
TAG="pre-${STAMP}-${NAME}"
BACKUP_DIR="/srv/docker/backups/${TAG}"

mkdir -p "${BACKUP_DIR}"

cd /srv/docker

git add .
git commit -m "checkpoint before ${NAME}" || true
git tag -a "${TAG}" -m "Pre-change snapshot: ${NAME}"

tar -czf "${BACKUP_DIR}/compose-and-config.tar.gz" \
  --exclude='./backups' \
  --exclude='./*/data' \
  --exclude='./*/work' \
  --exclude='./*/conf' \
  .

for path in \
  /srv/docker/adguard/work \
  /srv/docker/adguard/conf \
  /srv/docker/reverse-proxy/caddy/data \
  /srv/docker/reverse-proxy/caddy/config \
  /srv/docker/portainer/data \
  /srv/docker/homepage/data \
  /srv/docker/n8n/data \
  /srv/docker/ha/config
do
  if [ -e "$path" ]; then
    base="$(echo "$path" | sed 's#^/srv/docker/##; s#/#_#g')"
    tar -czf "${BACKUP_DIR}/${base}.tar.gz" -C / "$(echo "$path" | sed 's#^/##')"
  fi
done

echo "Created tag: ${TAG}"
echo "Backups stored in: ${BACKUP_DIR}"
