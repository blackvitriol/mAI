@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"

echo.
echo ============================================================
echo   A7 SERVER RESTART
echo ============================================================
echo.

call "%ROOT%stop.cmd"
if errorlevel 1 exit /b 1

echo.
call "%ROOT%boot.cmd"
exit /b %ERRORLEVEL%
