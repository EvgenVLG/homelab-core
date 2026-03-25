#!/usr/bin/env bash
set -euo pipefail

OUT="/srv/docker/docs/core-compose-review.md"

{
  echo "# Core Compose Review"
  echo
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo

  for f in \
    /srv/docker/reverse-proxy/docker-compose.yml \
    /srv/docker/adguard/docker-compose.yml \
    /srv/docker/homepage/docker-compose.yml \
    /srv/docker/portainer/docker-compose.yml \
    /srv/docker/n8n/docker-compose.yml \
    /srv/docker/ha/docker-compose.yml \
    /srv/docker/compose/core/docker-compose.yml
  do
    if [ -f "$f" ]; then
      echo "## FILE: $f"
      echo
      sed -n '1,240p' "$f"
      echo
      echo '---'
      echo
    else
      echo "## MISSING: $f"
      echo
    fi
  done
} > "$OUT"

echo "Wrote $OUT"
