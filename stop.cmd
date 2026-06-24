@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "DOCKER_DIR=%ROOT%docker"
set "COMPOSE_FILE=%DOCKER_DIR%\docker-compose.yml"
set "A7_SYSTEM=a7_server_1"

for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set "STOP_DATE=%%c-%%b-%%a"
for /f "tokens=1-2 delims=:." %%a in ("%time%") do set "STOP_TIME=%%a:%%b"
set "STOP_STAMP=%STOP_DATE% %STOP_TIME%"

echo.
echo ============================================================
echo   A7 SERVER STOP
echo   System : %A7_SYSTEM%
echo   Started: %STOP_STAMP%
echo ============================================================
echo.

echo [1/4] Checking Docker CLI...
where docker >nul 2>&1
if errorlevel 1 (
    echo       [FAIL] Docker is not installed or not in PATH.
    exit /b 1
)
for /f "delims=" %%v in ('docker --version 2^>nul') do echo       [OK]   %%v

echo.
echo [2/4] Checking Docker engine...
docker info >nul 2>&1
if errorlevel 1 (
    echo       [FAIL] Docker engine is not running. Start Docker Desktop.
    exit /b 1
)
echo       [OK]   Docker engine is running.

if not exist "%COMPOSE_FILE%" (
    echo       [FAIL] Missing %COMPOSE_FILE%
    exit /b 1
)

cd /d "%DOCKER_DIR%"

echo.
echo [3/4] Stopping %A7_SYSTEM% containers...
docker compose -f "%COMPOSE_FILE%" ps 2>nul
echo.
docker compose -f "%COMPOSE_FILE%" down --remove-orphans
if errorlevel 1 (
    echo       [FAIL] docker compose down failed.
    exit /b 1
)
echo       [OK]   Compose down completed.

echo.
echo [4/4] Verifying stack is stopped...
set "STILL_RUNNING=0"
for %%c in (
    "a7_server_1-postgres"
    "a7_server_1-portainer"
    "a7_server_1-n8n"
    "a7_server_1-website"
    "a7_server_1-lmstudio"
    "a7_server_1-openclaw-gateway"
) do (
    set "CNAME=%%~c"
    set "CSTATUS=stopped"
    for /f "delims=" %%s in ('docker inspect --format "{{.State.Status}}" "!CNAME!" 2^>nul') do set "CSTATUS=%%s"
    if /i not "!CSTATUS!"=="stopped" if /i not "!CSTATUS!"=="exited" if /i not "!CSTATUS!"=="" (
        set "STILL_RUNNING=1"
        echo       [WARN] !CNAME! status=!CSTATUS!
    ) else (
        echo       [OK]   !CNAME! stopped
    )
)

echo.
echo ------------------------------------------------------------
echo   %A7_SYSTEM% stop finished at %STOP_STAMP%
echo.
echo   Start again: startup.cmd
echo ------------------------------------------------------------
echo.
exit /b 0
