#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="/srv/docker/secrets/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: secrets file not found: $ENV_FILE"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

HOSTNAME="${HOSTNAME:-server}"
HAS_ERRORS=0

send_telegram() {
  local text="$1"

  if [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]]; then
    return 0
  fi

  curl -fsS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    --data-urlencode text="$text" \
    >/dev/null || true
}

check_http() {
  local url="$1"
  local expected="$2"

  local code
  code="$(curl -k -s -o /dev/null -w "%{http_code}" "$url" || echo "000")"

  if [[ "$code" == "$expected" ]]; then
    echo "$url -> OK ($code)"
  else
    echo "$url -> FAIL ($code expected $expected)"
    HAS_ERRORS=1
  fi
}

echo "=== $(date '+%F %T %Z') ==="
echo

echo "[containers]"
docker ps --format '{{.Names}} {{.Status}}'

echo
echo "[http]"
check_http "https://home.home.arpa" "200"
check_http "https://portainer.home.arpa" "200"
check_http "https://n8n.home.arpa" "200"
check_http "https://adguard.home.arpa" "302"

echo
echo "[dns]"
getent hosts home.home.arpa || HAS_ERRORS=1
getent hosts adguard.home.arpa || HAS_ERRORS=1

echo
echo "[disk]"
df -h /

echo
echo "[docker errors]"
FAILED_CONTAINERS="$(docker ps -a --filter 'status=exited' --format '{{.Names}}' || true)"
if [[ -n "$FAILED_CONTAINERS" ]]; then
  echo "$FAILED_CONTAINERS"
  HAS_ERRORS=1
else
  echo "none"
fi

DISK_USAGE="$(df -h / | awk 'NR==2 {print $5 " used (" $3 "/" $2 ")"}')"
MEM_USAGE="$(free -h | awk '/Mem:/ {print $3 "/" $2 " used"}')"

if [[ "$HAS_ERRORS" -ne 0 ]]; then
  MSG="❌ ${HOSTNAME}: healthcheck failed
Disk: ${DISK_USAGE}
Memory: ${MEM_USAGE}"
  echo
  echo "$MSG"
  send_telegram "$MSG"
  exit 1
fi

MSG="✅ ${HOSTNAME}: healthcheck OK
Disk: ${DISK_USAGE}
Memory: ${MEM_USAGE}"

echo
echo "$MSG"
