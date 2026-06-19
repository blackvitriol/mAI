# A7 Server (Docker)

Docker-based home server stack. Services run in containers and are exposed on your local network and the internet.

## Services

| Service | Purpose | Default port |
|---------|---------|--------------|
| **Portainer** | Main dashboard — manage containers, images, volumes | 9443 |
| **n8n** | Workflow automation + AI agent | 5678 |
| **PostgreSQL** | n8n database (internal only) | — |
| **LM Studio** | Local LLM server (llmster, GPU) for OpenClaw | 1234 |
| **OpenClaw** | AI agent gateway (uses LM Studio) | 18789 |
| **Mail server** | Self-hosted mail (Mailcow or similar) | 25, 587, 993 |
| **Website hosting** | Static sites / web apps via Nginx | 80, 443 |

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows)
- NVIDIA GPU + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) in Docker Desktop (for LM Studio)
- CMD or PowerShell with admin rights when binding low ports

## Quick start

```cmd
cd d:\A7Dev\Server
```

1. Edit `docker\.env` — set **`LM_STUDIO_MODELS_PATH`** to your models folder (e.g. `D:/LLM/models`)
2. Run:

```cmd
init.cmd
boot.cmd
```

- **init.cmd** — folders, `.env`, pull images, build LM Studio GPU image
- **boot.cmd** — start stack, health checks, sync OpenClaw config
- **stop.cmd** — stop the full stack

Open **Portainer**: `https://localhost:9443`  
Open **OpenClaw**: `http://localhost:18789`  
LM Studio API: `http://localhost:1234`

## LM Studio (GPU container, host models)

Uses official [llmster](https://lmstudio.ai/docs/developer/core/headless) installed inside the container on first boot (picks the GPU bundle when NVIDIA is visible). OpenClaw connects per [LM Studio + OpenClaw](https://lmstudio.ai/docs/integrations/openclaw).

In `docker\.env`:

```env
# Your models on the host (required)
LM_STUDIO_MODELS_PATH=D:/LLM/models

# llmster binary + config (container cache, in repo)
LM_STUDIO_DATA_PATH=./lmstudio-data

LM_STUDIO_MODEL_ID=qwen/qwen3.5-9b
```

Mounts:

| Host | Container |
|------|-----------|
| `LM_STUDIO_MODELS_PATH` | `/root/.lmstudio/models` |
| `LM_STUDIO_DATA_PATH` | `/root/.lmstudio` (bin, config) |

Put GGUF / LM Studio model files in your host folder. First boot downloads llmster (~few min). Then load a model:

```cmd
docker exec -it a7_server_1-lmstudio lms ls
docker exec -it a7_server_1-lmstudio lms load qwen/qwen3.5-9b --gpu max
docker exec -it a7_server_1-lmstudio nvidia-smi
```

Requires `gpus: all` in compose and NVIDIA drivers on the host.

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
    ├── .env.example
    ├── lmstudio-image/             ← GPU llmster Docker build
    ├── lmstudio-data/              ← llmster install cache (gitignored)
    ├── portainer/
    ├── n8n/
    ├── postgres/
    ├── openclaw/
    ├── shared/
    ├── mail/
    └── www/
```

## Network: local LAN + internet

Published ports on your LAN:

- `http://<your-pc-ip>:5678` — n8n
- `http://<your-pc-ip>:18789` — OpenClaw
- `http://<your-pc-ip>:1234` — LM Studio API

```cmd
ipconfig
```

## n8n AI agent + browser (optional)

Stock `n8nio/n8n`. Install `n8n-nodes-puppeteer` later via **Settings → Community Nodes** if you need browser tools.

## Common commands

```cmd
cd d:\A7Dev\Server

init.cmd
boot.cmd
stop.cmd

docker compose -f docker\docker-compose.yml logs -f lmstudio
docker compose -f docker\docker-compose.yml restart openclaw-gateway
```

## OpenClaw gateway token

`init.cmd` generates `OPENCLAW_GATEWAY_TOKEN` in `docker\.env`. Paste it into OpenClaw Settings after first boot.

## Next steps

1. Set `LM_STUDIO_MODELS_PATH` and `LM_STUDIO_MODEL_ID` in `docker\.env`
2. Run `init.cmd` then `boot.cmd`
3. Load a model in LM Studio (see `lms load` above)
4. Open OpenClaw at `http://localhost:18789`
