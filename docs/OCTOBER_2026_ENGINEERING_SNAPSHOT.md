# October 2026 engineering snapshot

This repository is a sanitized public view of a larger self-hosted lab. Credentials, runtime databases, private topology, household data, and machine-specific state are intentionally excluded.

## Current private deployment

The active lab is centered on Ubuntu Server 24.04 and containerized services, including:

- Docker / Compose service isolation;
- reverse proxy and TLS termination;
- AdGuard-backed DNS filtering;
- Tailscale remote access;
- Home Assistant environment integration;
- n8n workflow automation;
- Portainer and Glances for operations and observability;
- separate media/storage services;
- a separate desktop compute node used when heavier local AI or test workloads need it.

## Engineering work this environment drives

The useful part of the lab is the integration and operational work around it:

- diagnosing DNS, reverse-proxy, TCP/IP, service-discovery, and certificate failures;
- separating persistent data, configuration, secrets, and disposable runtime state;
- building remote administration paths without directly exposing internal services;
- monitoring health and resource use;
- recovering from interrupted processes without corrupting state;
- composing automation, AI, media, and device-facing services without unnecessary authority;
- maintaining Git-backed configuration and documentation that can be reviewed independently of the live host.

This is hands-on Linux/integration work, not a claim of enterprise production infrastructure.

Related public projects: [Production Zoo](https://github.com/EvgenVLG/production-zoo), [The Nest](https://github.com/EvgenVLG/the-nest-runtime), [Marinka](https://github.com/EvgenVLG/Marinka-assistant).
