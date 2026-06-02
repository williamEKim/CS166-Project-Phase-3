@echo off
setlocal

set "DB_NAME=%USERNAME%_eBay_DB"
set "SCRIPT_DIR=%~dp0"

choice /c YN /m "Would you like to execute the Python Script? (Y/N)"

if %ERRORLEVEL% == 1 (
    echo Executing the Python Script...
    python "%SCRIPT_DIR%backend\main.py" "%DB_NAME%" "%PGPORT%" "%USERNAME%"
) else (
    echo Skipping Python Script.
)