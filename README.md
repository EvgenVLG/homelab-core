# Homelab Core

This repository contains reproducible infrastructure for the homelab.

## Goals
- Docker-based platform
- Configs stored in git
- Host can be rebuilt from repo
- Secrets kept out of git

## Layout
- compose/core         core services
- compose/media        media stack
- compose/automation   n8n, bots, workflows
- compose/monitoring   grafana/loki/prometheus later
- env                  environment templates
- scripts              bootstrap, backup, restore, helper scripts
- docs                 architecture and notes
- data                 runtime bind mounts (not tracked)
- backups              local backups (not tracked)
