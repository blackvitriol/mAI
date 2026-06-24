@echo off
setlocal EnableExtensions EnableDelayedExpansion

if not defined COMPOSE_FILE (
    echo [FAIL] COMPOSE_FILE is not set.
    exit /b 1
)

set "PORTAINER_VERSION=2.39.3"
set "POSTGRES_VERSION=16.8-alpine"
set "NGINX_VERSION=1.27.5-alpine"
set "N8N_VERSION=2.26.6"
set "NODE_VERSION=22-bookworm-slim"
set "UBUNTU_VERSION=22.04"
set "OPENCLAW_VERSION=2026.5.4"

if exist "%DOCKER_DIR%\.env" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%DOCKER_DIR%\.env") do (
        if /i "%%a"=="PORTAINER_VERSION" set "PORTAINER_VERSION=%%b"
        if /i "%%a"=="POSTGRES_VERSION" set "POSTGRES_VERSION=%%b"
        if /i "%%a"=="NGINX_VERSION" set "NGINX_VERSION=%%b"
        if /i "%%a"=="N8N_VERSION" set "N8N_VERSION=%%b"
        if /i "%%a"=="NODE_VERSION" set "NODE_VERSION=%%b"
        if /i "%%a"=="UBUNTU_VERSION" set "UBUNTU_VERSION=%%b"
        if /i "%%a"=="OPENCLAW_VERSION" set "OPENCLAW_VERSION=%%b"
    )
)

set "MISSING=0"

call :ensure_external "portainer/portainer-ce" "%PORTAINER_VERSION%"
call :ensure_external "postgres" "%POSTGRES_VERSION%"
call :ensure_external "nginx" "%NGINX_VERSION%"
call :ensure_local "a7_server_1-n8n" "%N8N_VERSION%" "n8n"
call :ensure_local "a7_server_1-lmstudio" "%UBUNTU_VERSION%" "lmstudio"
call :ensure_local "a7_server_1-openclaw" "%OPENCLAW_VERSION%" "openclaw-gateway"

if !MISSING! equ 0 (
    echo       [OK]   All pinned images are already local.
    exit /b 0
)

echo       [OK]   Missing images were pulled or built.
exit /b 0

:ensure_external
set "IMAGE_REPO=%~1"
set "IMAGE_TAG=%~2"
docker image inspect "%IMAGE_REPO%:%IMAGE_TAG%" >nul 2>&1
if not errorlevel 1 (
    echo       [SKIP] %IMAGE_REPO%:%IMAGE_TAG%
    exit /b 0
)

echo       [PULL] %IMAGE_REPO%:%IMAGE_TAG%
docker pull "%IMAGE_REPO%:%IMAGE_TAG%"
if errorlevel 1 exit /b 1
set "MISSING=1"
exit /b 0

:ensure_local
set "IMAGE_REPO=%~1"
set "IMAGE_TAG=%~2"
set "SERVICE=%~3"
docker image inspect "%IMAGE_REPO%:%IMAGE_TAG%" >nul 2>&1
if not errorlevel 1 (
    echo       [SKIP] %IMAGE_REPO%:%IMAGE_TAG%
    exit /b 0
)

echo       [BUILD] %IMAGE_REPO%:%IMAGE_TAG% ^(%SERVICE%^)
docker compose -f "%COMPOSE_FILE%" build "%SERVICE%"
if errorlevel 1 exit /b 1
set "MISSING=1"
exit /b 0
