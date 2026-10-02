# HomeLab Platform

> [Engineering portfolio map](https://github.com/EvgenVLG/test-rep) - quick recruiter-facing index of the public projects and what each one demonstrates.

> **October 2026:** active engineering continues in the private lab. See the [current engineering snapshot](docs/OCTOBER_2026_ENGINEERING_SNAPSHOT.md) for Linux operations, networking, automation, observability, and recovery work that is intentionally separated from private runtime state.


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
