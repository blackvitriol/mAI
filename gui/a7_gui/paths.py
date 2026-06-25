from __future__ import annotations

import os
import sys
from pathlib import Path

MARKER = "startup.cmd"


def find_server_root() -> Path:
    env_root = os.environ.get("A7_SERVER_ROOT")
    if env_root:
        path = Path(env_root).resolve()
        if (path / MARKER).is_file():
            return path
        raise FileNotFoundError(
            f"A7_SERVER_ROOT is set but {MARKER} was not found at {path}"
        )

    candidates: list[Path] = []
    package_root = Path(__file__).resolve().parent.parent
    candidates.append(package_root.parent)
    candidates.append(Path.cwd())
    candidates.append(Path(sys.executable).resolve().parent)

    for start in candidates:
        found = _walk_up_for_marker(start)
        if found is not None:
            return found

    raise FileNotFoundError(
        f"Could not locate server root ({MARKER}). Set A7_SERVER_ROOT to the Server repo folder."
    )


def _walk_up_for_marker(start: Path) -> Path | None:
    current = start.resolve()
    for _ in range(10):
        if (current / MARKER).is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def startup_script(root: Path) -> Path:
    return root / "startup.cmd"


def stop_script(root: Path) -> Path:
    return root / "stop.cmd"


def init_script(root: Path) -> Path:
    return root / "init.cmd"


def is_initialized(root: Path) -> bool:
    return (root / "docker" / ".a7-initialized").is_file()


def asset_path(name: str) -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / name
