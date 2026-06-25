@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
cd /d "%ROOT%"

for %%I in ("%ROOT%..") do set "A7_SERVER_ROOT=%%~fI"

call "%~dp0..\scripts\ensure-gui-venv.cmd"
if errorlevel 1 exit /b 1

set "PY=%ROOT%\.venv\Scripts\python.exe"

echo [INFO] A7_SERVER_ROOT=%A7_SERVER_ROOT%
echo [INFO] Python=%PY%
"%PY%" -m a7_gui
exit /b %ERRORLEVEL%
