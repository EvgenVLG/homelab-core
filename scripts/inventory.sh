#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/docker"
OUT="$ROOT/docs/current-state-inventory.md"
TS="$(date '+%Y-%m-%d %H:%M:%S')"

{
  echo "# Homelab Current State Inventory"
  echo
  echo "Generated: $TS"
  echo

  echo "## 1. Running containers"
  echo
  if command -v docker >/dev/null 2>&1; then
    docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
  else
    echo "Docker not found"
  fi
  echo

  echo "## 2. All containers"
  echo
  if command -v docker >/dev/null 2>&1; then
    docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
  else
    echo "Docker not found"
  fi
  echo

  echo "## 3. Docker networks"
  echo
  if command -v docker >/dev/null 2>&1; then
    docker network ls
  else
    echo "Docker not found"
  fi
  echo

  echo "## 4. Candidate compose files"
  echo
  find "$ROOT" \
    \( -name 'docker-compose.yml' -o -name 'docker-compose.yaml' -o -name 'compose.yml' -o -name 'compose.yaml' \) \
    -not -path '*/.git/*' \
    | sort
  echo

  echo "## 5. Top-level directories"
  echo
  find "$ROOT" -maxdepth 2 -type d \
    -not -path '*/.git*' \
    | sort
  echo

  echo "## 6. Important service paths"
  echo
  for p in \
    "$ROOT/reverse-proxy" \
    "$ROOT/adguard" \
    "$ROOT/homepage" \
    "$ROOT/portainer" \
    "$ROOT/n8n" \
    "$ROOT/ha" \
    "$ROOT/homeassistant" \
    "$ROOT/navidrome" \
    "$ROOT/qbittorrent" \
    "$ROOT/lidarr" \
    "$ROOT/prowlarr"
  do
    if [ -e "$p" ]; then
      echo "### $p"
      find "$p" -maxdepth 2 -type f | sort | head -100
      echo
    fi
  done

  echo "## 7. Docker compose version"
  echo
  if command -v docker >/dev/null 2>&1; then
    docker compose version || true
  fi
  echo

  echo "## 8. Git status"
  echo
  if [ -d "$ROOT/.git" ]; then
    git -C "$ROOT" status --short
  else
    echo "No git repo"
  fi
  echo
} > "$OUT"

echo "Inventory written to: $OUT"
