@echo off
setlocal EnableExtensions

set "GUI_DIR=%~dp0..\gui"
set "PY=%GUI_DIR%\.venv\Scripts\python.exe"
set "PIP=%GUI_DIR%\.venv\Scripts\pip.exe"

cd /d "%GUI_DIR%"

where python >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python is not installed or not in PATH.
    exit /b 1
)

if not exist "%PY%" (
    echo [gui] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

"%PIP%" show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo [gui] Installing dependencies...
    "%PIP%" install -r requirements.txt
    if errorlevel 1 exit /b 1
)

echo [gui] venv ready: %PY%
exit /b 0
