# Core Compose Review

Generated: 2026-03-16 19:54:21

## FILE: /srv/docker/reverse-proxy/docker-compose.yml

services:
  caddy:
    image: lucaslorentz/caddy-docker-proxy:2.9-alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    environment:
      - CADDY_INGRESS_NETWORKS=homelab
      - CADDY_DOCKER_CADDYFILE_PATH=/etc/caddy/Caddyfile
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./caddy/data:/data
      - ./caddy/config:/config
    networks:
      - homelab
    extra_hosts:
      - "host.docker.internal:host-gateway"

networks:
  homelab:
    external: true

---

## FILE: /srv/docker/adguard/docker-compose.yml

services:
  adguard:
    image: adguard/adguardhome:v0.107.58
    container_name: adguard
    restart: unless-stopped
    networks:
      - homelab
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "3001:3000/tcp"
    volumes:
      - ./work:/opt/adguardhome/work
      - ./conf:/opt/adguardhome/conf
    labels:
      caddy: adguard.home.arpa
      caddy.tls: internal
      caddy.reverse_proxy: "{{upstreams 3000}}"

networks:
  homelab:
    external: true

---

## FILE: /srv/docker/homepage/docker-compose.yml

services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    restart: unless-stopped
    environment:
      - HOMEPAGE_ALLOWED_HOSTS=home.home.arpa,100.79.248.118:3000,100.79.248.118,evgenserver.llama-alphard.ts.net
    volumes:
      - ./data:/app/config
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /storage:/storage:ro
      - /fast:/fast:ro
    ports:
      - "3000:3000"
    networks:
      - homelab

    labels:
      caddy_0: home.home.arpa
      caddy_0.tls: internal
      caddy_0.reverse_proxy: "{{upstreams 3000}}"

      caddy_1: evgenserver.llama-alphard.ts.net
      caddy_1.tls: internal
      caddy_1.reverse_proxy: "{{upstreams 3000}}"

networks:
  homelab:
    external: true

---

## FILE: /srv/docker/portainer/docker-compose.yml

services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/data
    networks:
      - homelab
    labels:
      caddy: portainer.home.arpa
      caddy.tls: internal
      caddy.reverse_proxy: "{{upstreams 9000}}"

networks:
  homelab:
    external: true

---

## FILE: /srv/docker/n8n/docker-compose.yml

services:
  n8n:
    image: n8nio/n8n:latest
    environment:
      - TZ=America/New_York
      - N8N_HOST=n8n.home.arpa
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://end-screensaver-notes-may.trycloudflare.com/
    container_name: n8n
    restart: unless-stopped
    volumes:
      - ./data:/home/node/.n8n
    networks:
      - homelab
    labels:
      caddy: n8n.home.arpa
      caddy.tls: internal
      caddy.reverse_proxy: "{{upstreams 5678}}"

networks:
  homelab:
    external: true

---

## FILE: /srv/docker/ha/docker-compose.yml

name: ha

services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    restart: unless-stopped
    network_mode: host
    privileged: true

    environment:
      - TZ=America/New_York

    volumes:
      - ./config:/config

---

## FILE: /srv/docker/compose/core/docker-compose.yml

name: homelab-core

services:
  caddy:
    image: lucaslorentz/caddy-docker-proxy:2.9-alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    environment:
      - CADDY_INGRESS_NETWORKS=homelab
    networks:
      - homelab
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /srv/docker/reverse-proxy/caddy/data:/data
      - /srv/docker/reverse-proxy/caddy/config:/config

  adguard:
    image: adguard/adguardhome:v0.107.58
    container_name: adguard
    restart: unless-stopped
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "3001:3000"
    networks:
      - homelab
    volumes:
      - /srv/docker/adguard/work:/opt/adguardhome/work
      - /srv/docker/adguard/conf:/opt/adguardhome/conf
    labels:
      caddy: adguard.local
      caddy.reverse_proxy: "{{upstreams 3000}}"

  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    restart: unless-stopped
    ports:
      - "3000:3000"
    networks:
      - homelab
    environment:
      - TZ=${TZ}
    volumes:
      - /srv/docker/homepage/config:/app/config
      - /var/run/docker.sock:/var/run/docker.sock:ro
    labels:
      caddy: home.local
      caddy.reverse_proxy: "{{upstreams 3000}}"

  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    networks:
      - homelab
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /srv/docker/portainer/data:/data
    command: -H unix:///var/run/docker.sock
    labels:
      caddy: portainer.local
      caddy.reverse_proxy: "{{upstreams 9000}}"

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    networks:
      - homelab
    environment:
      - TZ=${TZ}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
    volumes:
      - /srv/docker/n8n/data:/home/node/.n8n
    labels:
      caddy: ${N8N_HOST}
      caddy.reverse_proxy: "{{upstreams 5678}}"

  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    restart: unless-stopped
    network_mode: host
    privileged: true
    environment:
      - TZ=${TZ}
    volumes:
      - /srv/docker/ha/config:/config
      - /etc/localtime:/etc/localtime:ro

networks:
  homelab:
    external: true

---

