#!/usr/bin/env bash
set -euo pipefail

echo "=== $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z') ==="

echo

echo "[containers]"
docker ps --format '{{.Names}} {{.Status}}'
echo

check_http() {
  url=$1
  expected=$2
  code=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" || echo "000")

  if [[ "$code" == "$expected" ]]; then
    echo "$url -> OK ($code)"
  else
    echo "$url -> FAIL ($code expected $expected)"
  fi
}

echo "[http]"

check_http https://home.home.arpa 401
check_http https://portainer.home.arpa 200
check_http https://n8n.home.arpa 200
check_http https://adguard.home.arpa 302

echo

echo "[dns]"
getent hosts home.home.arpa
getent hosts adguard.home.arpa
echo

echo "[disk]"
df -h /
echo

echo "[docker errors]"
docker ps --filter "status=exited"
echo

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

send_telegram() {
  local text="$1"

  if [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]]; then
    echo "WARN: Telegram variables are not set, skipping notification"
    return 0
  fi

  curl -fsS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    --data-urlencode text="$text" \
    >/dev/null
}

fail() {
  local msg="❌ ${HOSTNAME}: healthcheck failed
Disk: ${DISK_USAGE}
Memory: ${MEM_USAGE}
Docker failed containers:
${FAILED_CONTAINERS}"
  send_telegram "$msg"
  echo "$msg"
  exit 1
}

DISK_USAGE="$(df -h / | awk 'NR==2 {print $5 " used (" $3 "/" $2 ")"}')"
MEM_USAGE="$(free -h | awk '/Mem:/ {print $3 "/" $2 " used"}')"
FAILED_CONTAINERS="$(docker ps -a --filter 'status=exited' --format '{{.Names}}' || true)"

ROOT_USE_PCT="$(df / | awk 'NR==2 {gsub("%","",$5); print $5}')"

if [[ "${ROOT_USE_PCT}" -ge 90 ]]; then
  FAILED_CONTAINERS="${FAILED_CONTAINERS:-none}"
  fail
fi

if [[ -n "${FAILED_CONTAINERS}" ]]; then
  fail
fi

MSG="✅ ${HOSTNAME}: healthcheck OK
Disk: ${DISK_USAGE}
Memory: ${MEM_USAGE}"

echo "$MSG"
