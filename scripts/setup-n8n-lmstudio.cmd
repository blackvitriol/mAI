@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0.."
set "DOCKER_DIR=%ROOT%\docker"
set "N8N_SCRIPTS=%ROOT%\scripts\n8n"
set "WORKFLOW_ID=zfnm0J8fcPqZ6zWu"
set "USER_ID=9725c070-50b5-4b7b-a01e-9a13f68de88c"

echo.
echo ============================================================
echo   n8n Browser Agent - LM Studio setup
echo ============================================================
echo.

docker ps --filter "name=a7_server_1-n8n" --format "{{.Names}}" | findstr /i "a7_server_1-n8n" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] n8n container is not running. Run startup.cmd first.
    exit /b 1
)

docker ps --filter "name=a7_server_1-lmstudio" --format "{{.Status}}" | findstr /i "healthy" >nul 2>&1
if errorlevel 1 (
    echo [WARN] LM Studio is not healthy yet. Load a model before testing the workflow.
)

echo [1/3] Importing LM Studio OpenAI credential...
docker cp "%N8N_SCRIPTS%\lmstudio-credential.json" a7_server_1-n8n:/tmp/lmstudio-credential.json
docker exec a7_server_1-n8n n8n import:credentials --input=/tmp/lmstudio-credential.json --userId=%USER_ID%
if errorlevel 1 (
    echo [ERROR] Credential import failed.
    exit /b 1
)
echo       [OK]   http://lmstudio:1234/v1

echo [2/3] Updating Browser Agent workflow nodes...
docker cp "%N8N_SCRIPTS%\browser-agent-nodes.json" a7_server_1-postgres:/tmp/browser-agent-nodes.json
docker cp "%N8N_SCRIPTS%\browser-agent-connections.json" a7_server_1-postgres:/tmp/browser-agent-connections.json
docker cp "%N8N_SCRIPTS%\update-browser-agent.sql" a7_server_1-postgres:/tmp/update-browser-agent.sql
docker exec a7_server_1-postgres psql -U n8n -d n8n -f /tmp/update-browser-agent.sql
if errorlevel 1 (
    echo [ERROR] Workflow update failed.
    exit /b 1
)
echo       [OK]   LM Studio Chat Model connected (responses API off)

echo [3/3] Verifying LM Studio from n8n network...
docker exec a7_server_1-n8n wget -qO- http://lmstudio:1234/v1/models
echo.
echo ------------------------------------------------------------
echo   Done. Open n8n ^> Browser Agent workflow and test.
echo   Model: gemma-4-e2b-it (loaded in LM Studio)
echo   Guide: https://community.n8n.io/t/running-a-local-llm-with-lm-studio-n8n-fixed-workflow-real-case-step-by-step/272190
echo ------------------------------------------------------------
echo.

exit /b 0
