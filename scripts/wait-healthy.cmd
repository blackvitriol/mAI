@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."

set "SERVICE=%~1"
set "TIMEOUT_SEC=%~2"
if "%TIMEOUT_SEC%"=="" set "TIMEOUT_SEC=180"

if "%SERVICE%"=="" (
    echo Usage: wait-healthy.cmd ^<service^> [timeout_seconds]
    exit /b 1
)

echo Waiting for %SERVICE% to become healthy (max %TIMEOUT_SEC%s)...
set /a ELAPSED=0

:loop
for /f "delims=" %%S in ('docker inspect --format^="{{.State.Health.Status}}" %SERVICE% 2^>nul') do set "STATUS=%%S"

if /i "!STATUS!"=="healthy" (
    echo %SERVICE% is healthy.
    exit /b 0
)

for /f "delims=" %%S in ('docker inspect --format^="{{.State.Status}}" %SERVICE% 2^>nul') do set "RUNNING=%%S"
if /i not "!RUNNING!"=="running" (
    echo %SERVICE% is not running. Check: docker compose ps
    exit /b 1
)

if !ELAPSED! geq %TIMEOUT_SEC% (
    echo Timed out waiting for %SERVICE% health. Last status: !STATUS!
    exit /b 1
)

ping -n 4 127.0.0.1 >nul
set /a ELAPSED+=3
goto loop
