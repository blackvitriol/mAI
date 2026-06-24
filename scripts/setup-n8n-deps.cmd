@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0.."
set "DOCKER_DIR=%ROOT%\docker"
set "COMPOSE_FILE=%DOCKER_DIR%\docker-compose.yml"
set "SETUP_FORCE=0"

if /i "%~1"=="--force" set "SETUP_FORCE=1"
if defined A7_SETUP_FORCE set "SETUP_FORCE=1"

cd /d "%DOCKER_DIR%"

docker images --format "{{.Repository}}" | findstr /i /x "a7_server_1-n8n" >nul 2>&1
if errorlevel 1 (
    echo [FAIL] n8n image missing. Run init.cmd first.
    exit /b 1
)

if "!SETUP_FORCE!"=="1" (
    docker compose -f "%COMPOSE_FILE%" run --rm --no-deps -e A7_SETUP_FORCE=1 --entrypoint /setup-deps.sh n8n
) else (
    docker compose -f "%COMPOSE_FILE%" run --rm --no-deps --entrypoint /setup-deps.sh n8n
)

exit /b %ERRORLEVEL%
