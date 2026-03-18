#!/bin/bash

ALERTS=""

for c in caddy adguard homepage n8n homeassistant glances navidrome lidarr; do
  if ! docker ps --format '{{.Names}}' | grep -qx "$c"; then
    ALERTS="${ALERTS}Container down: $c\n"
  fi
done

ROOT_USE=$(df / | awk 'NR==2 {gsub("%","",$5); print $5}')
STORAGE_USE=$(df /storage | awk 'NR==2 {gsub("%","",$5); print $5}')

if [ "$ROOT_USE" -ge 90 ]; then
  ALERTS="${ALERTS}Root disk critical: ${ROOT_USE}%\n"
fi

if [ "$STORAGE_USE" -ge 90 ]; then
  ALERTS="${ALERTS}Storage disk critical: ${STORAGE_USE}%\n"
fi

if [ -n "$ALERTS" ]; then
  PAYLOAD=$(printf '{"status":"fail","service":"healthcheck","details":"%s"}' "$(echo -e "$ALERTS" | sed ':a;N;$!ba;s/\n/\\n/g')")
  curl -k -X POST https://n8n.home.arpa/webhook/healthcheck \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD"
fi
