#!/usr/bin/env bash
set -euo pipefail

echo "=== $(date) ==="
echo

echo "[docker ps]"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo

echo "[http checks]"
for url in \
  https://home.home.arpa \
  https://portainer.home.arpa \
  https://n8n.home.arpa \
  https://adguard.home.arpa
do
  code=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" || true)
  echo "$url -> $code"
done
echo

echo "[dns checks]"
getent hosts home.home.arpa || true
getent hosts adguard.home.arpa || true
echo

echo "[disk]"
df -h /
echo

echo "[recent caddy log]"
docker logs --tail 5 caddy 2>/dev/null || true
echo

echo "[recent adguard log]"
docker logs --tail 5 adguard 2>/dev/null || true
