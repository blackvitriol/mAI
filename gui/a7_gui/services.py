from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ServiceDef:
    compose_service: str
    container_name: str
    label: str
    role: str
    port_env: str | None = None
    url_scheme: str | None = None


MANAGED_SERVICES: tuple[ServiceDef, ...] = (
    ServiceDef("portainer", "a7_server_1-portainer", "Portainer", "dashboard", "PORTAINER_PORT", "https"),
    ServiceDef("postgres", "a7_server_1-postgres", "PostgreSQL", "database"),
    ServiceDef("n8n", "a7_server_1-n8n", "n8n", "automation", "N8N_PORT", "http"),
    ServiceDef("website", "a7_server_1-website", "Website", "web-hosting", "WEB_HTTP_PORT", "http"),
    ServiceDef("lmstudio", "a7_server_1-lmstudio", "LM Studio", "llm", "LM_STUDIO_PORT", "http"),
    ServiceDef(
        "openclaw-gateway",
        "a7_server_1-openclaw-gateway",
        "OpenClaw",
        "ai-agent",
        "OPENCLAW_GATEWAY_PORT",
        "http",
    ),
)

DEFAULT_PORTS: dict[str, str] = {
    "PORTAINER_PORT": "9443",
    "N8N_PORT": "5678",
    "WEB_HTTP_PORT": "80",
    "LM_STUDIO_PORT": "1234",
    "OPENCLAW_GATEWAY_PORT": "18789",
}


def parse_env_ports(root: Path) -> dict[str, str]:
    ports = dict(DEFAULT_PORTS)
    env_path = root / "docker" / ".env"
    if not env_path.is_file():
        return ports

    for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value:
            ports[key] = value
    return ports


def service_url(defn: ServiceDef, ports: dict[str, str]) -> str | None:
    if not defn.port_env or not defn.url_scheme:
        return None
    port = ports.get(defn.port_env)
    if not port:
        return None
    return f"{defn.url_scheme}://localhost:{port}"


def is_managed_service(service: str) -> bool:
    return any(defn.compose_service == service for defn in MANAGED_SERVICES)
