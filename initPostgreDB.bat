@echo off

:: Check if PostgreSQL is installed
where pg_ctl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL not found. Installing via winget...
    winget install -e --id PostgreSQL.PostgreSQL
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install PostgreSQL. Please install manually.
        exit /b 1
    )
) else (
    echo PostgreSQL is already installed.
)

:: Set data directory
set PGDATA=%USERPROFILE%\myDB\data

:: Only init if data dir doesn't exist
if not exist "%PGDATA%" (
    echo Initializing database at %PGDATA%...
    initdb -D "%PGDATA%"
) else (
    echo Database already initialized, skipping initdb.
)

:: Find a free port starting from 5432
set PGPORT=5432
:find_port
    netstat -ano | findstr ":%PGPORT% " >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Port %PGPORT% is in use, trying next...
        set /a PGPORT=%PGPORT%+1
        goto find_port
    )

echo Using port %PGPORT%

:: Start the server
echo Starting PostgreSQL server at %PGDATA% on port %PGPORT%...
pg_ctl -D "%PGDATA%" -o "-p %PGPORT%" start

pg_ctl -D "%PGDATA%" status

echo.
echo To connect, run:
echo   psql -p %PGPORT% -U %USERNAME% postgres
echo.
echo To stop the server later, run:
echo   pg_ctl -D "%PGDATA%" stop