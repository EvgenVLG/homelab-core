#!/usr/bin/env bash
docker compose -f /srv/docker/compose/core/docker-compose.yml --env-file /srv/docker/env/.env logs --tail=100 "${@}"
