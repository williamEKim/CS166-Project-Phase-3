@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "DB_NAME=%USERNAME%_eBay_DB"

call "%SCRIPT_DIR%cs166_server\psql.bat"

echo.
choice /c YN /m "Would you like to execute the Python Script?"

if %ERRORLEVEL% == 1 (
    echo Executing the Python Script...
    python "%SCRIPT_DIR%backend\main.py" "%DB_NAME%" "%PGPORT%" "%USERNAME%"
) else (
    echo Skipping Python Script.
)

echo.
choice /c YN /m "Would you like to stop your PostgreSQL Server?"

if %ERRORLEVEL% == 1 (
    echo Stopping the PostgreSQL Server...
    call "%SCRIPT_DIR%cs166_server\stopPostgreDB.bat"
) else (
    echo Skipping Server Stop.
)