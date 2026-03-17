# Homelab Current State Inventory

Generated: 2026-03-16 19:47:38

## 1. Running containers

NAMES                  IMAGE                                          STATUS                  PORTS
homepage               ghcr.io/gethomepage/homepage:latest            Up 17 hours (healthy)   0.0.0.0:3000->3000/tcp
house-bot              house-bot-house-bot                            Up 18 hours             
n8n                    n8nio/n8n:latest                               Up 20 hours             5678/tcp
cloudflared            cloudflare/cloudflared:latest                  Up 20 hours             
telegram-summary-bot   telegram-summary-bot-telegram-summary-bot      Up 20 hours             
lidarr                 linuxserver/lidarr:latest                      Up 19 hours             0.0.0.0:8686->8686/tcp
navidrome              deluan/navidrome:latest                        Up 19 hours             0.0.0.0:4533->4533/tcp
prowlarr               linuxserver/prowlarr:latest                    Up 19 hours             9696/tcp
qbittorrent            linuxserver/qbittorrent:latest                 Up 19 hours             6881/tcp, 8080/tcp, 6881/udp
caddy                  lucaslorentz/caddy-docker-proxy:2.9-alpine     Up 17 hours             0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp, 2019/tcp
adguard                adguard/adguardhome:v0.107.58                  Up 20 hours             80/tcp, 67-68/udp, 443/tcp, 443/udp, 853/udp, 853/tcp, 3000/udp, 5443/tcp, 0.0.0.0:53->53/tcp, 0.0.0.0:53->53/udp, 5443/udp, 6060/tcp, 0.0.0.0:3001->3000/tcp
portainer              portainer/portainer-ce:latest                  Up 20 hours             8000/tcp, 9000/tcp, 9443/tcp
homeassistant          ghcr.io/home-assistant/home-assistant:stable   Up 20 hours             

## 2. All containers

NAMES                  IMAGE                                          STATUS
homepage               ghcr.io/gethomepage/homepage:latest            Up 17 hours (healthy)
house-bot              house-bot-house-bot                            Up 18 hours
n8n                    n8nio/n8n:latest                               Up 20 hours
cloudflared            cloudflare/cloudflared:latest                  Up 20 hours
telegram-summary-bot   telegram-summary-bot-telegram-summary-bot      Up 20 hours
lidarr                 linuxserver/lidarr:latest                      Up 19 hours
navidrome              deluan/navidrome:latest                        Up 19 hours
prowlarr               linuxserver/prowlarr:latest                    Up 19 hours
qbittorrent            linuxserver/qbittorrent:latest                 Up 19 hours
caddy                  lucaslorentz/caddy-docker-proxy:2.9-alpine     Up 17 hours
adguard                adguard/adguardhome:v0.107.58                  Up 20 hours
portainer              portainer/portainer-ce:latest                  Up 20 hours
homeassistant          ghcr.io/home-assistant/home-assistant:stable   Up 20 hours

## 3. Docker networks

NETWORK ID     NAME                           DRIVER    SCOPE
e978cf23b802   bridge                         bridge    local
45135ac2a700   homelab                        bridge    local
195439e26a06   host                           host      local
b7283f342e4c   none                           null      local
28293bfc0e07   telegram-summary-bot_default   bridge    local

## 4. Candidate compose files

/srv/docker/adguard/docker-compose.yml
/srv/docker/ha/docker-compose.yml
/srv/docker/homepage/docker-compose.yml
/srv/docker/house-bot/docker-compose.yml
/srv/docker/lidarr/docker-compose.yml
/srv/docker/n8n/docker-compose.yml
/srv/docker/navidrome/docker-compose.yml
/srv/docker/portainer/docker-compose.yml
/srv/docker/prowlarr/docker-compose.yml
/srv/docker/qbittorrent/docker-compose.yml
/srv/docker/reverse-proxy/docker-compose.yml

## 5. Top-level directories

/srv/docker
/srv/docker/adguard
/srv/docker/adguard/conf
/srv/docker/adguard/work
/srv/docker/ai
/srv/docker/backups
/srv/docker/backups/pre-20260309-235925-before-network-cleanup
/srv/docker/backups/pre-20260310-000903-caddy-adguard-route
/srv/docker/backups/pre-20260310-001032-caddy-adguard-route
/srv/docker/backups/pre-20260310-002431-remove-proxy-network
/srv/docker/backups/pre-20260310-031501-nightly-auto
/srv/docker/backups/pre-20260311-012050-stable-checkpoint
/srv/docker/backups/pre-20260311-031501-nightly-auto
/srv/docker/backups/pre-20260312-031501-nightly-auto
/srv/docker/backups/pre-20260313-031501-nightly-auto
/srv/docker/backups/pre-20260314-031501-nightly-auto
/srv/docker/backups/pre-20260315-031501-nightly-auto
/srv/docker/backups/pre-20260316-031501-nightly-auto
/srv/docker/compose
/srv/docker/compose/automation
/srv/docker/compose/core
/srv/docker/compose/media
/srv/docker/compose/monitoring
/srv/docker/data
/srv/docker/docs
/srv/docker/env
/srv/docker/ha
/srv/docker/ha/config
/srv/docker/homeassistant
/srv/docker/homepage
/srv/docker/homepage/backup-2026-03-15-1939
/srv/docker/homepage/config
/srv/docker/homepage/data
/srv/docker/house-bot
/srv/docker/lidarr
/srv/docker/n8n
/srv/docker/n8n/data
/srv/docker/navidrome
/srv/docker/ops
/srv/docker/portainer
/srv/docker/portainer/data
/srv/docker/prowlarr
/srv/docker/qbittorrent
/srv/docker/reverse-proxy
/srv/docker/reverse-proxy/caddy
/srv/docker/scripts
/srv/docker/scripts/homelab
/srv/docker/scripts/ytmusic

## 6. Important service paths

### /srv/docker/reverse-proxy
/srv/docker/reverse-proxy/Caddyfile
/srv/docker/reverse-proxy/docker-compose.yml

### /srv/docker/adguard
/srv/docker/adguard/conf/AdGuardHome.yaml
/srv/docker/adguard/docker-compose.yml

### /srv/docker/homepage
/srv/docker/homepage/backup-2026-03-15-1939/bookmarks.yaml
/srv/docker/homepage/backup-2026-03-15-1939/docker.yaml
/srv/docker/homepage/backup-2026-03-15-1939/kubernetes.yaml
/srv/docker/homepage/backup-2026-03-15-1939/proxmox.yaml
/srv/docker/homepage/backup-2026-03-15-1939/services.yaml
/srv/docker/homepage/backup-2026-03-15-1939/settings.yaml
/srv/docker/homepage/backup-2026-03-15-1939/widgets.yaml
/srv/docker/homepage/config/bookmarks.yaml
/srv/docker/homepage/config/custom.css
/srv/docker/homepage/config/custom.js
/srv/docker/homepage/config/docker.yaml
/srv/docker/homepage/config/kubernetes.yaml
/srv/docker/homepage/config/proxmox.yaml
/srv/docker/homepage/config/services.yaml
/srv/docker/homepage/config/settings.yaml
/srv/docker/homepage/config/widgets.yaml
/srv/docker/homepage/data/bookmarks.yaml
/srv/docker/homepage/data/custom.css
/srv/docker/homepage/data/custom.js
/srv/docker/homepage/data/docker.yaml
/srv/docker/homepage/data/kubernetes.yaml
/srv/docker/homepage/data/proxmox.yaml
/srv/docker/homepage/data/services.yaml
/srv/docker/homepage/data/settings.yaml
/srv/docker/homepage/data/widgets.yaml
/srv/docker/homepage/docker-compose.yml

### /srv/docker/portainer
/srv/docker/portainer/data/portainer.db
/srv/docker/portainer/data/portainer.key
/srv/docker/portainer/data/portainer.pub
/srv/docker/portainer/docker-compose.yml

### /srv/docker/n8n
/srv/docker/n8n/data/config
/srv/docker/n8n/data/crash.journal
/srv/docker/n8n/data/database.sqlite
/srv/docker/n8n/data/database.sqlite-shm
/srv/docker/n8n/data/database.sqlite-wal
/srv/docker/n8n/data/n8nEventLog-1.log
/srv/docker/n8n/data/n8nEventLog-2.log
/srv/docker/n8n/data/n8nEventLog-3.log
/srv/docker/n8n/data/n8nEventLog.log
/srv/docker/n8n/docker-compose.yml

### /srv/docker/ha
/srv/docker/ha/config/automations.yaml
/srv/docker/ha/config/configuration.yaml
/srv/docker/ha/config/.ha_run.lock
/srv/docker/ha/config/.HA_VERSION
/srv/docker/ha/config/home-assistant.log
/srv/docker/ha/config/home-assistant.log.1
/srv/docker/ha/config/home-assistant.log.fault
/srv/docker/ha/config/home-assistant_v2.db
/srv/docker/ha/config/home-assistant_v2.db-shm
/srv/docker/ha/config/home-assistant_v2.db-wal
/srv/docker/ha/config/scenes.yaml
/srv/docker/ha/config/scripts.yaml
/srv/docker/ha/config/secrets.yaml
/srv/docker/ha/docker-compose.yml

### /srv/docker/homeassistant

### /srv/docker/navidrome
/srv/docker/navidrome/docker-compose.yml

### /srv/docker/qbittorrent
/srv/docker/qbittorrent/docker-compose.yml

### /srv/docker/lidarr
/srv/docker/lidarr/docker-compose.yml

### /srv/docker/prowlarr
/srv/docker/prowlarr/docker-compose.yml

## 7. Docker compose version

Docker Compose version v5.1.0

## 8. Git status

 M ha/config/home-assistant.log
?? docs/current-state-inventory.md
?? scripts/inventory.sh

