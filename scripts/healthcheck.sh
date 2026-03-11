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
