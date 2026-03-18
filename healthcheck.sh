#!/bin/bash

BOT_TOKEN="8772857427:AAFsva8OOqe1JqEZQXdwNOhuc0-81po0gv0"
CHAT_ID="653822434"
STATE_FILE="/tmp/homelab_alert_state"

ALERTS=""

# Critical containers
for c in caddy adguard homepage n8n homeassistant glances navidrome lidarr; do
  if ! docker ps --format '{{.Names}}' | grep -qx "$c"; then
    ALERTS="${ALERTS}Container down: $c\n"
  fi
done

# Disk usage checks
ROOT_USE=$(df / | awk 'NR==2 {gsub("%","",$5); print $5}')
STORAGE_USE=$(df /storage | awk 'NR==2 {gsub("%","",$5); print $5}')

if [ "$ROOT_USE" -ge 90 ]; then
  ALERTS="${ALERTS}Root disk critical: ${ROOT_USE}%\n"
fi

if [ "$STORAGE_USE" -ge 90 ]; then
  ALERTS="${ALERTS}Storage disk critical: ${STORAGE_USE}%\n"
fi

# Send alert only once until issue clears
if [ -n "$ALERTS" ]; then
  if [ ! -f "$STATE_FILE" ]; then
    MESSAGE=$(printf "🚨 Homelab alert\nHost: evgenserver\n\n%b" "$ALERTS")
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
      --data-urlencode "chat_id=${CHAT_ID}" \
      --data-urlencode "text=${MESSAGE}" >/dev/null
    touch "$STATE_FILE"
  fi
else
  rm -f "$STATE_FILE"
fi
