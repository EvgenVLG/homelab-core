# Homelab Core

## Host
- Ubuntu 24.04
- Docker Engine
- LAN IP: 192.168.50.59
- Root path: /srv/docker

## Core Services
- Caddy
- AdGuard
- Homepage
- Portainer

## Secondary Services
- n8n
- Home Assistant

## Docker Network
- homelab

## Stable Tag
- stable-core-2026-03-09

## Operational Scripts
- scripts/prechange.sh
- scripts/rollback-config.sh
- scripts/check-compose.sh
- scripts/cleanup-backups.sh
- scripts/healthcheck.sh
