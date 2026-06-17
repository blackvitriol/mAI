@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "DOCKER_DIR=%ROOT%docker"
set "COMPOSE_FILE=%DOCKER_DIR%\docker-compose.yml"
set "A7_SYSTEM=a7_server_1"

echo.
echo ============================================================
echo   A7 SERVER INIT
echo   System : %A7_SYSTEM%
echo ============================================================
echo.

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH.
    echo Install Docker Desktop: https://www.docker.com/products/docker-desktop/
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Start Docker Desktop and try again.
    exit /b 1
)

if not exist "%COMPOSE_FILE%" (
    echo [ERROR] Missing %COMPOSE_FILE%
    exit /b 1
)

cd /d "%DOCKER_DIR%"

echo [1/5] Creating data folders...
for %%D in (
    portainer n8n postgres mail www
    ollama shared
    openclaw\config openclaw\workspace openclaw\secrets
) do (
    if not exist "%%D" mkdir "%%D"
)

echo [2/5] Checking environment file...
if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo       [OK]   Created docker\.env from .env.example
    ) else (
        echo [ERROR] Missing docker\.env and docker\.env.example
        exit /b 1
    )
)
echo       [OK]   docker\.env found

set "NEED_TOKEN=0"
findstr /r /c:"^OPENCLAW_GATEWAY_TOKEN=change-me-to-a-random-token" ".env" >nul 2>&1
if not errorlevel 1 set "NEED_TOKEN=1"

if "!NEED_TOKEN!"=="1" (
    for /f "delims=" %%T in ('powershell -NoProfile -Command "[guid]::NewGuid().ToString('N')"') do set "NEW_TOKEN=%%T"
    powershell -NoProfile -Command "(Get-Content '.env') -replace '^OPENCLAW_GATEWAY_TOKEN=.*', 'OPENCLAW_GATEWAY_TOKEN=!NEW_TOKEN!' | Set-Content '.env'"
    echo       [OK]   Generated OPENCLAW_GATEWAY_TOKEN
)

findstr /r /c:"^OLLAMA_MODEL=" ".env" >nul 2>&1
if errorlevel 1 (
    echo OLLAMA_MODEL=qwen3.5:9b>> ".env"
    echo       [OK]   Added default OLLAMA_MODEL=qwen3.5:9b
)

echo [3/5] Pulling images for %A7_SYSTEM%...
docker compose -f "%COMPOSE_FILE%" pull portainer postgres n8n website browserless ollama openclaw-gateway
if errorlevel 1 (
    echo [ERROR] Failed to pull images.
    exit /b 1
)

echo [4/5] Syncing OpenClaw config...
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\sync-openclaw-token.ps1"
if errorlevel 1 (
    echo [WARN] OpenClaw config sync skipped or failed. Run boot.cmd after fixing .env.
)

echo [5/5] Validating compose file...
docker compose -f "%COMPOSE_FILE%" config --quiet
if errorlevel 1 (
    echo [ERROR] docker-compose.yml validation failed.
    exit /b 1
)

echo.
echo Init complete for %A7_SYSTEM%.
echo   Network  : %A7_SYSTEM%
echo   Containers will be named: a7_server_1-^<service^>
echo.
echo Run boot.cmd to start the server.
echo.
exit /b 0
