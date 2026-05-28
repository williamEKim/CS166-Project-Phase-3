@echo off

set PGDATA=%USERPROFILE%\myDB\data

:: Check if server is running
pg_ctl -D "%PGDATA%" status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo No PostgreSQL server is running at %PGDATA%.
    exit /b 0
)

:: Stop the server
echo Stopping PostgreSQL server...
pg_ctl -D "%PGDATA%" stop

echo.
echo Your PostgreSQL server stopped.