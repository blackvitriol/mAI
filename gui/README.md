# A7 Server GUI

PyQt6 desktop app for managing the A7 Docker stack.

## Features

- Frameless window with GIF (or gradient) background
- **Init** — runs `init.cmd` in a new console
- **Start** / **Stop** / **Restart** — `startup.cmd` / `stop.cmd`
- Per-service start / stop / restart and **Open** links
- Live Docker container status polling

## Prerequisites

- Python 3.11+ on Windows
- Docker Desktop (for stack control)
- [PyQt6](https://pypi.org/project/PyQt6/) (installed automatically by `run.cmd`)

## Run

```cmd
cd D:\A7Dev\Server
gui\run.cmd
```

Or **Run and Debug** → **A7 GUI**.

## Development

Edit Python under `gui/a7_gui/`. Restart the app to pick up changes.

```cmd
cd gui
.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m a7_gui
```

## Assets

Place `background.gif` in `gui/assets/`. A gradient is used if the file is missing.

## Server root

The app finds `startup.cmd` via:

1. `A7_SERVER_ROOT` environment variable
2. Parent of `gui/` (repo layout)
3. Current working directory

`run.cmd` sets `A7_SERVER_ROOT` to the repo root automatically.

## Layout

```text
a7_gui/
  main_window.py      Application shell
  server_control.py   init / startup / docker compose
  services.py         Managed service definitions
  paths.py            Server root resolution
  widgets/            UI components
assets/
  background.gif
```
