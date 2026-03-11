#!/usr/bin/env bash
set -euo pipefail

echo "Creating pre-update snapshot..."
/srv/docker/scripts/prechange.sh container-update

echo "Pulling latest images..."
docker compose -f /srv/docker/adguard/docker-compose.yml pull
docker compose -f /srv/docker/reverse-proxy/docker-compose.yml pull
docker compose -f /srv/docker/homepage/docker-compose.yml pull
docker compose -f /srv/docker/portainer/docker-compose.yml pull
docker compose -f /srv/docker/n8n/docker-compose.yml pull

echo "Restarting containers..."
docker compose -f /srv/docker/adguard/docker-compose.yml up -d
docker compose -f /srv/docker/reverse-proxy/docker-compose.yml up -d
docker compose -f /srv/docker/homepage/docker-compose.yml up -d
docker compose -f /srv/docker/portainer/docker-compose.yml up -d
docker compose -f /srv/docker/n8n/docker-compose.yml up -d

echo "Running healthcheck..."
/srv/docker/scripts/healthcheck.sh

echo "Update complete."
