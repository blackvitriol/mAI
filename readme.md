# A7 Server (Docker)

Docker-based home server stack. Services run in containers and are exposed on your local network and the internet.

## Services

| Service | Purpose | Default port |
|---------|---------|--------------|
| **Portainer** | Main dashboard — manage containers, images, volumes | 9443 |
| **n8n** | Workflow automation (uses PostgreSQL) | 5678 |
| **PostgreSQL** | n8n database (internal only) | — |
| **Ollama** | Local LLM inference | 11434 |
| **OpenClaw** | AI agent gateway (uses Ollama) | 18789 |
| **Mail server** | Self-hosted mail (Mailcow or similar) | 25, 587, 993 |
| **Website hosting** | Static sites / web apps via Nginx | 80, 443 |

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows)
- NVIDIA GPU + drivers for Ollama (optional but recommended)
- CMD or PowerShell with admin rights when binding low ports

## Quick start

```cmd
cd d:\A7Dev\Server
init.cmd
boot.cmd
```

- **init.cmd** — first-time setup: folders, `.env`, pull images
- **boot.cmd** — start **a7_server_1**, wait for health, ensure Ollama model, sync OpenClaw
- **stop.cmd** — stop the full stack

All containers belong to the **a7_server_1** system (shared network, labels, and naming).

Open **Portainer**: `https://localhost:9443`  
Open **OpenClaw**: `http://localhost:18789`

## Project layout

```
Server/
├── readme.md
├── init.cmd
├── boot.cmd
├── stop.cmd
├── scripts/                      ← OpenClaw sync, health wait
└── docker/
    ├── docker-compose.yml
    ├── .env.example              ← copy to .env on first run (init.cmd does this)
    ├── portainer/
    ├── n8n/
    ├── postgres/
    ├── ollama/                   ← LLM models (~7 GB)
    ├── openclaw/                 ← config, workspace, secrets
    ├── shared/                   ← cross-container file share
    ├── mail/
    └── www/
```

## Network: local LAN + internet

### 1. Local network

Published ports are reachable from other devices on your LAN:

- `http://<your-pc-ip>:80` — website
- `https://<your-pc-ip>:9443` — Portainer
- `http://<your-pc-ip>:5678` — n8n
- `http://<your-pc-ip>:18789` — OpenClaw
- `http://<your-pc-ip>:11434` — Ollama API

Find your PC IP:

```cmd
ipconfig
```

### 2. Internet access

Forward external ports to this machine’s LAN IP as needed. Prefer VPN or a reverse proxy with TLS for admin and AI services.

### 3. GPU services

Ollama benefits from `gpus: all` in Docker Desktop (WSL2 backend with NVIDIA Container Toolkit).

## Common commands

```cmd
cd d:\A7Dev\Server

init.cmd
boot.cmd
stop.cmd

docker compose -f docker\docker-compose.yml logs -f
docker compose -f docker\docker-compose.yml restart openclaw-gateway
docker compose -f docker\docker-compose.yml --profile cli run openclaw-cli --help
```

## OpenClaw gateway token

`init.cmd` generates `OPENCLAW_GATEWAY_TOKEN` in `docker\.env`. Paste it into OpenClaw Settings after first boot.

## Mail server

The compose file includes a placeholder for mail. Replace `docker/mail/` with your chosen stack and wire it in `docker-compose.yml`.

## Next steps

1. Edit `docker\.env` — set `POSTGRES_PASSWORD` and review `OPENCLAW_GATEWAY_TOKEN`.
2. Run `init.cmd` then `boot.cmd`.
3. Complete Portainer setup at `https://localhost:9443`.
4. Open OpenClaw at `http://localhost:18789` and enter the gateway token.
5. Add site files under `docker\www\`.
