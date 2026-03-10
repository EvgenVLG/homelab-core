#!/usr/bin/env bash
set -euo pipefail

for f in /srv/docker/*/docker-compose.yml; do
  echo "Checking $f"
  docker compose -f "$f" config >/dev/null
done

echo "All compose files are valid."
