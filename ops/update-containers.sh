#!/usr/bin/env bash
set -e

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
