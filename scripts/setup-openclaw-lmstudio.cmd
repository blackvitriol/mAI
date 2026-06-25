@echo off

setlocal EnableExtensions EnableDelayedExpansion



set "ROOT=%~dp0.."

set "DOCKER_DIR=%ROOT%\docker"

set "COMPOSE_FILE=%DOCKER_DIR%\docker-compose.yml"

set "MARKER=%DOCKER_DIR%\openclaw\config\.lmstudio-configured"

set "SETUP_FORCE=0"



if /i "%~1"=="--force" set "SETUP_FORCE=1"

if defined A7_OPENCLAW_SETUP_FORCE set "SETUP_FORCE=1"



set "LM_STUDIO_MODEL_ID=gemma-4-e2b-it"

set "LM_API_TOKEN=lmstudio"



if not exist "%DOCKER_DIR%\.env" (

    echo [FAIL] Missing docker\.env. Run init.cmd first.

    exit /b 1

)



for /f "usebackq tokens=1,* delims==" %%a in ("%DOCKER_DIR%\.env") do (

    if /i "%%a"=="LM_STUDIO_MODEL_ID" set "LM_STUDIO_MODEL_ID=%%b"

    if /i "%%a"=="LM_API_TOKEN" set "LM_API_TOKEN=%%b"

)



if "!LM_API_TOKEN!"=="" set "LM_API_TOKEN=lmstudio"



for /f "delims=" %%M in ('powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\scripts\resolve-lmstudio-model.ps1" -EnvFile "%DOCKER_DIR%\.env" -PreferredModel "gemma-4-e2b-it"') do set "LM_STUDIO_MODEL_ID=%%M"



if exist "%MARKER%" if "!SETUP_FORCE!"=="0" (

    echo [SKIP] OpenClaw already configured for LM Studio ^(!LM_STUDIO_MODEL_ID!^).

    exit /b 0

)



powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\scripts\sync-openclaw-token.ps1"

if errorlevel 1 (

    echo [FAIL] OpenClaw config sync failed.

    exit /b 1

)



docker ps --filter "name=a7_server_1-openclaw-gateway" --format "{{.Names}}" | findstr /i "a7_server_1-openclaw-gateway" >nul 2>&1

if errorlevel 1 (

    echo [FAIL] OpenClaw gateway is not running. Run startup.cmd first.

    exit /b 1

)



echo [OPENCLAW] Applying LM Studio provider ^(openai-completions, model: !LM_STUDIO_MODEL_ID!^)...

docker exec -u node a7_server_1-openclaw-gateway node dist/index.js config set agents.defaults.model.primary "lmstudio/!LM_STUDIO_MODEL_ID!"

if errorlevel 1 (

    echo [FAIL] Failed to set primary model.

    exit /b 1

)



docker exec -u node a7_server_1-openclaw-gateway node dist/index.js config set agents.defaults.memorySearch.provider lmstudio

if errorlevel 1 (

    echo [WARN] memorySearch provider update failed.

)



echo [OPENCLAW] Restarting gateway to apply config...

docker compose -f "%COMPOSE_FILE%" restart openclaw-gateway

if errorlevel 1 (

    echo [FAIL] Gateway restart failed.

    exit /b 1

)



if not exist "%DOCKER_DIR%\openclaw\config" mkdir "%DOCKER_DIR%\openclaw\config"

echo configured> "%MARKER%"

echo [OK]   OpenClaw uses LM Studio / gemma via openai-completions ^(!LM_STUDIO_MODEL_ID!^).

exit /b 0

