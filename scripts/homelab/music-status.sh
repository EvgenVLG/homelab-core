#!/usr/bin/env bash
set -euo pipefail

echo "========== MUSIC STATUS $(date) =========="
echo

echo "---- Containers ----"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '^(NAMES|navidrome|lidarr|qbittorrent|prowlarr|caddy)' || true
echo

echo "---- Storage usage ----"
du -sh /storage/downloads 2>/dev/null || true
du -sh /storage/downloads/complete 2>/dev/null || true
du -sh /storage/downloads/incomplete 2>/dev/null || true
du -sh /storage/media/music 2>/dev/null || true
echo

echo "---- Free space on /storage ----"
df -h /storage || true
echo

echo "---- Listening ports ----"
ss -tulpn | grep -E ':(4533|8686|8080|9696)\b' || true
echo

echo "---- Recently modified files in downloads (last 10) ----"
find /storage/downloads -type f -printf '%TY-%Tm-%Td %TH:%TM %p\n' 2>/dev/null | sort | tail -n 10 || true
echo

echo "---- qBittorrent complete/incomplete file counts ----"
find /storage/downloads/complete -type f 2>/dev/null | wc -l
find /storage/downloads/incomplete -type f 2>/dev/null | wc -l
echo

echo "---- Last 20 lines of YTMusic sync log ----"
tail -n 20 ~/scripts/ytmusic/logs/sync.log 2>/dev/null || echo "No sync log yet"
echo

echo "---- Lidarr logs (last 20 lines) ----"
docker logs lidarr --tail 20 2>/dev/null || true
echo

echo "---- qBittorrent logs (last 20 lines) ----"
docker logs qbittorrent --tail 20 2>/dev/null || true
echo

echo "========== END =========="
