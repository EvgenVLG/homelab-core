# HomeLab Platform

This repository is a monorepo for a self-hosted homelab system.

## Structure

### /infra
Core infrastructure services:
- reverse-proxy
- adguard
- homepage
- portainer
- glances

### /services
Custom application layer:
- music-assistant
- house-bot
- ai-console
- ai-runner

### /media
Media ecosystem:
- navidrome
- lidarr
- prowlarr
- qbittorrent

### /automation
Automation and orchestration:
- n8n
- scripts

### /docs
Documentation and plans

### /compose
Top-level orchestration (future)

### /secrets
Local-only secrets (NOT tracked in git)

## Rules

- Never commit secrets
- Never commit runtime data
- Only code + configs go into git
- Services should be isolated and portable
