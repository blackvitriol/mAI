@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "DOCKER_DIR=%ROOT%docker"
set "COMPOSE_FILE=%DOCKER_DIR%\docker-compose.yml"
set "A7_SYSTEM=a7_server_1"
set "HEALTH_TIMEOUT=120"
set "HEALTH_INTERVAL=3"

for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set "STARTUP_DATE=%%c-%%b-%%a"
for /f "tokens=1-2 delims=:." %%a in ("%time%") do set "STARTUP_TIME=%%a:%%b"
set "STARTUP_STAMP=%STARTUP_DATE% %STARTUP_TIME%"

echo.
echo ============================================================
echo   A7 SERVER STARTUP
echo   System : %A7_SYSTEM%
echo   Started: %STARTUP_STAMP%
echo ============================================================
echo.

echo [1/6] Checking Docker CLI...
where docker >nul 2>&1
if errorlevel 1 (
    echo       [FAIL] Docker is not installed or not in PATH.
    exit /b 1
)
for /f "delims=" %%v in ('docker --version 2^>nul') do echo       [OK]   %%v
for /f "delims=" %%v in ('docker compose version 2^>nul') do echo       [OK]   %%v

echo.
echo [2/6] Checking Docker engine...
docker info >nul 2>&1
if errorlevel 1 (
    echo       [FAIL] Docker engine is not running. Start Docker Desktop.
    exit /b 1
)
for /f "delims=" %%v in ('docker info --format "{{.OperatingSystem}} / {{.ServerVersion}}" 2^>nul') do echo       [OK]   Engine: %%v
for /f "delims=" %%v in ('docker info --format "Containers: {{.ContainersRunning}} running, {{.Containers}} total" 2^>nul') do echo       [OK]   %%v

echo.
echo [3/6] Validating compose stack...
if not exist "%COMPOSE_FILE%" (
    echo       [FAIL] Missing %COMPOSE_FILE%
    exit /b 1
)
echo       [OK]   Compose file: %COMPOSE_FILE%

cd /d "%DOCKER_DIR%"

if not exist ".a7-initialized" (
    echo       [FAIL] Server not initialized. Run init.cmd first.
    exit /b 1
)

if not exist ".env" (
    echo       [FAIL] No .env file. Run init.cmd first.
    exit /b 1
)
echo       [OK]   Environment: %DOCKER_DIR%\.env

docker compose -f "%COMPOSE_FILE%" config --quiet >nul 2>&1
if errorlevel 1 (
    echo       [FAIL] docker-compose.yml validation failed.
    exit /b 1
)
echo       [OK]   Stack name: %A7_SYSTEM%
echo       [OK]   Network   : %A7_SYSTEM%

set "PORTAINER_PORT=9443"
set "N8N_PORT=5678"
set "WEB_HTTP_PORT=80"
set "LM_STUDIO_PORT=1234"
set "OPENCLAW_GATEWAY_PORT=18789"
set "OPENCLAW_GATEWAY_TOKEN="
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    if /i "%%a"=="PORTAINER_PORT" set "PORTAINER_PORT=%%b"
    if /i "%%a"=="N8N_PORT" set "N8N_PORT=%%b"
    if /i "%%a"=="WEB_HTTP_PORT" set "WEB_HTTP_PORT=%%b"
    if /i "%%a"=="LM_STUDIO_PORT" set "LM_STUDIO_PORT=%%b"
    if /i "%%a"=="OPENCLAW_GATEWAY_PORT" set "OPENCLAW_GATEWAY_PORT=%%b"
    if /i "%%a"=="OPENCLAW_GATEWAY_TOKEN" set "OPENCLAW_GATEWAY_TOKEN=%%b"
)

echo.
echo [4/6] Starting %A7_SYSTEM% containers...
echo       Services: portainer, postgres, n8n, website, lmstudio, openclaw-gateway
docker compose -f "%COMPOSE_FILE%" up -d --no-build --remove-orphans
if errorlevel 1 (
    echo       [WARN] docker compose up reported errors. Continuing startup...
    set "COMPOSE_OK=0"
) else (
    echo       [OK]   Compose up completed.
    set "COMPOSE_OK=1"
)

echo.
echo [5/6] Waiting for core container health (timeout %HEALTH_TIMEOUT%s)...
set /a ELAPSED=0
set "ALL_HEALTHY=0"

:health_loop
set "ALL_HEALTHY=1"

for %%c in (
    "a7_server_1-postgres:database"
    "a7_server_1-portainer:dashboard"
    "a7_server_1-n8n:automation"
    "a7_server_1-website:web-hosting"
    "a7_server_1-lmstudio:llm"
    "a7_server_1-openclaw-gateway:ai-agent"
) do (
    for /f "tokens=1,2 delims=:" %%a in (%%c) do (
        set "CNAME=%%a"
        set "CROLE=%%b"
        set "CSTATUS=missing"
        set "CHEALTH=n/a"

        for /f "delims=" %%s in ('docker inspect --format "{{if .State.Running}}running{{else}}{{.State.Status}}{{end}}" "!CNAME!" 2^>nul') do set "CSTATUS=%%s"
        for /f "delims=" %%h in ('docker inspect --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}" "!CNAME!" 2^>nul') do set "CHEALTH=%%h"

        if /i not "!CSTATUS!"=="running" set "ALL_HEALTHY=0"
        if /i "!CHEALTH!"=="unhealthy" set "ALL_HEALTHY=0"
        if /i "!CHEALTH!"=="starting" set "ALL_HEALTHY=0"
        if /i "!CSTATUS!"=="missing" set "ALL_HEALTHY=0"
        if /i "!CHEALTH!"=="-" if /i not "!CSTATUS!"=="running" set "ALL_HEALTHY=0"
        if /i "!CHEALTH!"=="no-healthcheck" if /i not "!CSTATUS!"=="running" set "ALL_HEALTHY=0"
    )
)

if !ALL_HEALTHY! equ 1 goto health_done

if !ELAPSED! geq %HEALTH_TIMEOUT% goto health_timeout

echo       ... %ELAPSED%s elapsed
ping -n 4 127.0.0.1 >nul
set /a ELAPSED+=%HEALTH_INTERVAL%
goto health_loop

:health_timeout
echo       [WARN] Core health wait timed out. Some services may still be starting.
goto health_report

:health_done
echo       [OK]   Core containers report healthy or running.

call "%ROOT%scripts\setup-openclaw-lmstudio.cmd"
if errorlevel 1 (
    echo       [WARN] OpenClaw LM Studio setup skipped or failed.
)

:health_report
echo.
echo [6/6] Container health report:
for %%c in (
    "a7_server_1-postgres:database"
    "a7_server_1-portainer:dashboard"
    "a7_server_1-n8n:automation"
    "a7_server_1-website:web-hosting"
    "a7_server_1-lmstudio:llm"
    "a7_server_1-openclaw-gateway:ai-agent"
) do (
    for /f "tokens=1,2 delims=:" %%a in (%%c) do (
        set "CNAME=%%a"
        set "CROLE=%%b"
        for /f "delims=" %%s in ('docker inspect --format "{{.State.Status}}" "!CNAME!" 2^>nul') do set "CSTATUS=%%s"
        for /f "delims=" %%h in ('docker inspect --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}-{{end}}" "!CNAME!" 2^>nul') do set "CHEALTH=%%h"
        if /i "!CSTATUS!"=="running" (
            if /i "!CHEALTH!"=="healthy" (
                echo       [OK]   !CNAME! ^(!CROLE!^) ^| !CSTATUS! ^| health: !CHEALTH!
            ) else if /i "!CHEALTH!"=="unhealthy" (
                echo       [FAIL] !CNAME! ^(!CROLE!^) ^| !CSTATUS! ^| health: !CHEALTH!
            ) else if /i "!CHEALTH!"=="starting" (
                echo       [WAIT] !CNAME! ^(!CROLE!^) ^| !CSTATUS! ^| health: !CHEALTH!
            ) else (
                echo       [OK]   !CNAME! ^(!CROLE!^) ^| !CSTATUS!
            )
        ) else (
            echo       [FAIL] !CNAME! ^(!CROLE!^) ^| !CSTATUS!
        )
    )
)

echo.
docker compose -f "%COMPOSE_FILE%" ps

call :print_and_open_urls
call :open_service_logs
goto :startup_done

:print_and_open_urls
echo.
echo ============================================================
echo   SERVICE URLS
echo ============================================================
echo.
echo   Local:
echo     Portainer    https://localhost:%PORTAINER_PORT%
echo     n8n          http://localhost:%N8N_PORT%
echo     Website      http://localhost:%WEB_HTTP_PORT%
echo     OpenClaw     http://localhost:%OPENCLAW_GATEWAY_PORT%
echo     LM Studio    http://localhost:%LM_STUDIO_PORT%
echo.

set "LAN_FOUND=0"
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "LAN_IP=%%i"
    set "LAN_IP=!LAN_IP: =!"
    if not "!LAN_IP!"=="127.0.0.1" (
        if !LAN_FOUND! equ 0 (
            echo   LAN:
            set "LAN_FOUND=1"
        )
        echo     Portainer    https://!LAN_IP!:%PORTAINER_PORT%
        echo     n8n          http://!LAN_IP!:%N8N_PORT%
        echo     Website      http://!LAN_IP!:%WEB_HTTP_PORT%
        echo     OpenClaw     http://!LAN_IP!:%OPENCLAW_GATEWAY_PORT%
        echo     LM Studio    http://!LAN_IP!:%LM_STUDIO_PORT%
        echo.
    )
)
if !LAN_FOUND! equ 0 echo   LAN: [WARN] No LAN IPv4 address detected.

echo.
echo   Opening in default browser...
start "" "https://localhost:%PORTAINER_PORT%"
start "" "http://localhost:%N8N_PORT%"
start "" "http://localhost:%WEB_HTTP_PORT%"
if defined OPENCLAW_GATEWAY_TOKEN (
    start "" "http://localhost:%OPENCLAW_GATEWAY_PORT%#token=%OPENCLAW_GATEWAY_TOKEN%"
) else (
    start "" "http://localhost:%OPENCLAW_GATEWAY_PORT%"
)
echo   [OK]   Browser tabs launched.
exit /b 0

:open_service_logs
echo.
echo   Opening service log windows...
for %%c in (
    "portainer:a7_server_1-portainer"
    "postgres:a7_server_1-postgres"
    "n8n:a7_server_1-n8n"
    "website:a7_server_1-website"
    "lmstudio:a7_server_1-lmstudio"
    "openclaw:a7_server_1-openclaw-gateway"
) do (
    for /f "tokens=1,2 delims=:" %%a in (%%c) do (
        start "A7 Logs - %%a" cmd /k docker logs -f %%b
    )
)
echo   [OK]   Log windows launched.
exit /b 0

:startup_done
echo ------------------------------------------------------------
echo   %A7_SYSTEM% startup finished at %STARTUP_STAMP%
echo.
echo   Logs (all):      docker compose -f docker\docker-compose.yml logs -f
echo   Stop stack:      stop.cmd
echo ------------------------------------------------------------
echo.

if not defined A7_NO_PAUSE (
    echo Press any key to close...
    pause >nul
)

exit /b 0
