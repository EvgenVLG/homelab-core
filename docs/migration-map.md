# Homelab Migration Map

## Goal
Move from legacy per-service compose folders to structured stack layout under `/srv/docker/compose/*`
without moving live data yet.

## Legacy -> Structured mapping

### Core stack
- /srv/docker/reverse-proxy      -> /srv/docker/compose/core (service: caddy)
- /srv/docker/adguard            -> /srv/docker/compose/core (service: adguard)
- /srv/docker/homepage           -> /srv/docker/compose/core (service: homepage)
- /srv/docker/portainer          -> /srv/docker/compose/core (service: portainer)
- /srv/docker/n8n                -> /srv/docker/compose/core (service: n8n)
- /srv/docker/ha                 -> /srv/docker/compose/core (service: homeassistant)

### Media stack
- /srv/docker/navidrome          -> /srv/docker/compose/media (service: navidrome)
- /srv/docker/qbittorrent        -> /srv/docker/compose/media (service: qbittorrent)
- /srv/docker/lidarr             -> /srv/docker/compose/media (service: lidarr)
- /srv/docker/prowlarr           -> /srv/docker/compose/media (service: prowlarr)

### Automation / bots
- /srv/docker/house-bot          -> /srv/docker/compose/automation
- telegram-summary-bot           -> probably separate automation compose later
- /srv/docker/ai                 -> future AI stack / services

## Rules
1. Existing bind-mount folders remain where they are for now.
2. New compose files become the control plane.
3. Data migration happens only after stable structured compose is verified.
4. One stack at a time, starting with core.
