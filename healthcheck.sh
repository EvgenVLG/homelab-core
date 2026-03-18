#!/bin/bash

BOT_TOKEN="8772857427:AAFsva8OOqe1JqEZQXdwNOhuc0-81po0gv0"
CHAT_ID="653822434"

STATE_FILE="/tmp/homelab_alert_state"
STATUS_FILE="/tmp/homelab_last_alert_text"

ALERTS=""

HOSTNAME="$(hostname)"

CPU_WARN=90
RAM_WARN=90
ROOT_WARN=90
STORAGE_WARN=90
LOAD_WARN=4.0
TEMP_WARN=85

if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
  echo "ERROR: BOT_TOKEN or CHAT_ID is empty"
  exit 1
fi

send_telegram() {
  local MESSAGE="$1"
  curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT_ID}" \
    --data-urlencode "text=${MESSAGE}" >/dev/null
}

# Critical containers
for c in caddy adguard homepage n8n homeassistant glances navidrome lidarr; do
  if ! docker ps --format '{{.Names}}' | grep -qx "$c"; then
    ALERTS="${ALERTS}Container down: $c\n"
  fi
done

# Disk usage
ROOT_USE=$(df / | awk 'NR==2 {gsub("%","",$5); print $5}')
STORAGE_USE=$(df /storage | awk 'NR==2 {gsub("%","",$5); print $5}')

if [ "$ROOT_USE" -ge "$ROOT_WARN" ]; then
  ALERTS="${ALERTS}Root disk critical: ${ROOT_USE}%\n"
fi

if [ "$STORAGE_USE" -ge "$STORAGE_WARN" ]; then
  ALERTS="${ALERTS}Storage disk critical: ${STORAGE_USE}%\n"
fi

# RAM usage
RAM_USE=$(free | awk '/Mem:/ {printf("%.0f", $3/$2 * 100)}')
if [ "$RAM_USE" -ge "$RAM_WARN" ]; then
  ALERTS="${ALERTS}RAM usage high: ${RAM_USE}%\n"
fi

# CPU usage
CPU_IDLE=$(top -bn1 | awk '/Cpu\(s\)/ {for(i=1;i<=NF;i++) if ($i ~ /id,/) {gsub(",", "", $(i-1)); print $(i-1)}}')
CPU_USE=$(awk -v idle="$CPU_IDLE" 'BEGIN {printf("%.0f", 100 - idle)}')
if [ "$CPU_USE" -ge "$CPU_WARN" ]; then
  ALERTS="${ALERTS}CPU usage high: ${CPU_USE}%\n"
fi

# Load average (1 min)
LOAD_1=$(awk '{print $1}' /proc/loadavg)

if awk -v val="$LOAD_1" -v warn="$LOAD_WARN" 'BEGIN {exit !(val >= warn)}'; then
  ALERTS="${ALERTS}Load average high: ${LOAD_1}\n"
fi
# Temperature (optional, if sensors exists and returns something useful)
# Temperature (trusted sensors only)
if command -v sensors >/dev/null 2>&1; then
  MAX_TEMP=$(
    sensors 2>/dev/null | awk '
      /Package id [0-9]+:/ || /Core [0-9]+:/ || /^CPU:/ || /^Composite:/ {
        for (i=1; i<=NF; i++) {
          if ($i ~ /^\+[0-9]+(\.[0-9]+)?°C$/) {
            val=$i
            gsub(/^\+/, "", val)
            gsub(/°C$/, "", val)
            if (val+0 > 0 && val+0 < 120) {
              if (val+0 > max) max=val+0
            }
          }
        }
      }
      END {
        if (max > 0) printf("%.0f\n", max)
      }'
  )

  if [ -n "$MAX_TEMP" ] && [ "$MAX_TEMP" -ge "$TEMP_WARN" ]; then
    ALERTS="${ALERTS}Temperature high: ${MAX_TEMP}C\n"
  fi
fi
# Alert / recovery logic
if [ -n "$ALERTS" ]; then
  printf "%b" "$ALERTS" > "$STATUS_FILE"

  if [ ! -f "$STATE_FILE" ]; then
    MESSAGE=$(printf "🚨 Homelab alert\nHost: %s\n\n%b" "$HOSTNAME" "$ALERTS")
    send_telegram "$MESSAGE"
    touch "$STATE_FILE"
  else
    if ! cmp -s "$STATUS_FILE" "$STATE_FILE.details" 2>/dev/null; then
      MESSAGE=$(printf "🚨 Homelab alert updated\nHost: %s\n\n%b" "$HOSTNAME" "$ALERTS")
      send_telegram "$MESSAGE"
    fi
  fi

  cp "$STATUS_FILE" "$STATE_FILE.details"
else
  if [ -f "$STATE_FILE" ]; then
    MESSAGE=$(printf "✅ Homelab recovered\nHost: %s\n\nAll monitored checks are back to normal." "$HOSTNAME")
    send_telegram "$MESSAGE"
    rm -f "$STATE_FILE" "$STATE_FILE.details" "$STATUS_FILE"
  fi
fi
