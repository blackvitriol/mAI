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

set "INIT_FORCE=0"
if /i "%~1"=="--force" set "INIT_FORCE=1"
if defined A7_INIT_FORCE set "INIT_FORCE=1"

if exist ".a7-initialized" if "!INIT_FORCE!"=="0" (
    echo [INFO] Already initialized.
    echo        Run startup.cmd to start the server, or stop.cmd to shut it down.
    echo        To pull/build images again, run: init.cmd --force
    exit /b 0
)

echo [1/7] Creating data folders...
for %%D in (
    portainer n8n postgres mail www
    shared
    openclaw\config openclaw\workspace openclaw\secrets
) do (
    if not exist "%%D" mkdir "%%D"
)

echo [2/7] Checking environment file...
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

findstr /r /c:"^LM_STUDIO_MODEL_ID=" ".env" >nul 2>&1
if errorlevel 1 (
    echo LM_STUDIO_MODEL_ID=gemma-4-e2b-it>> ".env"
    echo       [OK]   Added default LM_STUDIO_MODEL_ID=gemma-4-e2b-it
)

findstr /r /c:"^LM_STUDIO_MODELS_PATH=" ".env" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Set LM_STUDIO_MODELS_PATH in docker\.env to your local models folder.
    echo         Example: LM_STUDIO_MODELS_PATH=D:/LLM/models
    exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    if /i "%%a"=="LM_STUDIO_MODELS_PATH" set "LM_MODELS_PATH=%%b"
)
if not exist "!LM_MODELS_PATH!" (
    echo [WARN] LM_STUDIO_MODELS_PATH does not exist: !LM_MODELS_PATH!
    echo        Create the folder or update docker\.env before startup.
)

echo [3/7] Ensuring pinned images are local...
set "COMPOSE_FILE=%COMPOSE_FILE%"
set "DOCKER_DIR=%DOCKER_DIR%"
call "%ROOT%scripts\ensure-images.cmd"
if errorlevel 1 (
    echo [ERROR] Failed to ensure images.
    exit /b 1
)

if "!INIT_FORCE!"=="1" (
    echo       [FORCE] Rebuilding service images...
    docker compose -f "%COMPOSE_FILE%" build n8n lmstudio openclaw-gateway
)

echo [4/7] Setting up n8n dependencies (one-time)...
if "!INIT_FORCE!"=="1" (
    call "%ROOT%scripts\setup-n8n-deps.cmd" --force
) else (
    call "%ROOT%scripts\setup-n8n-deps.cmd"
)
if errorlevel 1 (
    echo [WARN] n8n dependency setup skipped or failed.
)

echo [5/7] Syncing OpenClaw config...
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\sync-openclaw-token.ps1"
if errorlevel 1 (
    echo [WARN] OpenClaw config sync skipped or failed. Run startup.cmd after fixing .env.
)

echo [6/7] Validating compose file...
docker compose -f "%COMPOSE_FILE%" config --quiet
if errorlevel 1 (
    echo [ERROR] docker-compose.yml validation failed.
    exit /b 1
)

echo initialized> ".a7-initialized"

echo.
echo Init complete for %A7_SYSTEM%.
echo   Network  : %A7_SYSTEM%
echo   Containers will be named: a7_server_1-^<service^>
echo.
echo Run startup.cmd to start the server.
echo.
exit /b 0
