from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .paths import (
    find_server_root,
    init_script,
    is_initialized,
    startup_script,
    stop_script,
)
from .services import MANAGED_SERVICES, is_managed_service, parse_env_ports, service_url

CREATE_NEW_CONSOLE = 0x00000010


@dataclass
class ContainerStatus:
    service: str
    name: str
    label: str
    role: str
    state: str
    health: str | None
    url: str | None


@dataclass
class ServerStatus:
    server_root: str
    running: bool
    initialized: bool
    containers: list[ContainerStatus]
    operation: str | None
    docker_available: bool


class ServerController:
    def __init__(self) -> None:
        self._operation: str | None = None

    @property
    def operation(self) -> str | None:
        return self._operation

    def get_status(self) -> ServerStatus:
        root = find_server_root()
        containers = _query_container_statuses(root)
        return ServerStatus(
            server_root=str(root),
            running=any(c.state.lower() == "running" for c in containers),
            initialized=is_initialized(root),
            containers=containers,
            operation=self._operation,
            docker_available=_docker_available(),
        )

    def run_init(self) -> str:
        root = find_server_root()
        script = init_script(root)
        if not script.is_file():
            raise FileNotFoundError(f"Missing {script}")
        self._operation = "initializing"
        try:
            _run_cmd(script, root, wait=False)
        finally:
            self._operation = None
        return "Init launched — watch the console for progress."

    def start_server(self) -> str:
        root = find_server_root()
        if not is_initialized(root):
            raise RuntimeError("Server not initialized. Run init first.")
        script = startup_script(root)
        if not script.is_file():
            raise FileNotFoundError(f"Missing {script}")
        self._operation = "starting"
        try:
            _run_cmd(script, root, wait=False)
        finally:
            self._operation = None
        return "Startup launched — watch the console for progress."

    def stop_server(self) -> str:
        root = find_server_root()
        script = stop_script(root)
        if not script.is_file():
            raise FileNotFoundError(f"Missing {script}")
        self._operation = "stopping"
        try:
            _run_cmd(script, root, wait=True)
        finally:
            self._operation = None
        return "All containers stopped."

    def restart_server(self) -> str:
        root = find_server_root()
        if not is_initialized(root):
            raise RuntimeError("Server not initialized. Run init first.")
        stop = stop_script(root)
        start = startup_script(root)
        if not stop.is_file() or not start.is_file():
            raise FileNotFoundError("Missing startup.cmd or stop.cmd")
        self._operation = "restarting"
        try:
            _run_cmd(stop, root, wait=True)
            _run_cmd(start, root, wait=False)
        finally:
            self._operation = None
        return "Restart launched — watch the console for progress."

    def control_container(self, service: str, action: str) -> str:
        if not is_managed_service(service):
            raise ValueError(f"Unknown service: {service}")
        action = action.lower()
        if action not in {"start", "stop", "restart"}:
            raise ValueError(f"Unknown action: {action}")
        root = find_server_root()
        if not is_initialized(root):
            raise RuntimeError("Server not initialized. Run init first.")
        _run_compose_service(root, service, action)
        return f"{service} {action} complete"


def _run_cmd(script: Path, root: Path, wait: bool) -> None:
    env = os.environ.copy()
    env["A7_NO_PAUSE"] = "1"
    kwargs: dict = {
        "args": ["cmd", "/C", str(script)],
        "cwd": root,
        "env": env,
    }
    if sys.platform == "win32" and not wait:
        kwargs["creationflags"] = CREATE_NEW_CONSOLE
    if wait:
        result = subprocess.run(**kwargs, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"{script} exited with {result.returncode}.\n{result.stdout}{result.stderr}"
            )
    else:
        subprocess.Popen(**kwargs)


def _run_compose_service(root: Path, service: str, action: str) -> None:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            "docker/docker-compose.yml",
            action,
            service,
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"docker compose {action} {service} failed.\n{result.stdout}{result.stderr}"
        )


def _docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except OSError:
        return False


def _inspect_container(name: str) -> tuple[str, str | None]:
    try:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}",
                name,
            ],
            capture_output=True,
            text=True,
        )
    except OSError:
        return "missing", None

    if result.returncode != 0:
        return "missing", None

    text = result.stdout.strip()
    if "|" not in text:
        return "unknown", None
    state, health = text.split("|", 1)
    health = health or None
    return state, health


def _query_container_statuses(root: Path) -> list[ContainerStatus]:
    ports = parse_env_ports(root)
    items: list[ContainerStatus] = []
    for defn in MANAGED_SERVICES:
        state, health = _inspect_container(defn.container_name)
        items.append(
            ContainerStatus(
                service=defn.compose_service,
                name=defn.container_name,
                label=defn.label,
                role=defn.role,
                state=state,
                health=health,
                url=service_url(defn, ports),
            )
        )
    return items
