@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0.."
set "ENV_FILE=%ROOT%\docker\.env"
set "OPENCLAW_GATEWAY_PORT=18789"
set "OPENCLAW_GATEWAY_TOKEN="

if not exist "%ENV_FILE%" (
    echo [FAIL] Missing %ENV_FILE%. Run init.cmd first.
    exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
    if /i "%%a"=="OPENCLAW_GATEWAY_PORT" set "OPENCLAW_GATEWAY_PORT=%%b"
    if /i "%%a"=="OPENCLAW_GATEWAY_TOKEN" set "OPENCLAW_GATEWAY_TOKEN=%%b"
)

if not defined OPENCLAW_GATEWAY_TOKEN (
    echo [FAIL] OPENCLAW_GATEWAY_TOKEN missing from docker\.env
    exit /b 1
)

start "" "http://localhost:%OPENCLAW_GATEWAY_PORT%#token=%OPENCLAW_GATEWAY_TOKEN%"
echo [OK] Opened OpenClaw dashboard.
exit /b 0
