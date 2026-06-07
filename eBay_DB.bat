@echo off
setlocal

set SCRIPT_DIR=%~dp0

:: Load PostgreSQL environment
call "%SCRIPT_DIR%cs166_server\psql.bat"

set DB_NAME=%USERNAME%_eBay_DB

echo Initializing and activating the python virtual environment...
python3 -m venv venv --system-site-packages
call venv\Scripts\activate.bat

echo Installing Required Dependencies...
pip3 install -r requirements.txt

:: Python prompt
set /p RUN_PYTHON="Would you like to execute the Python Script? [Y/N]: "
if /i "%RUN_PYTHON%"=="Y" (
    echo Executing the Python Script...
    python3 "%SCRIPT_DIR%backend\GUI.py" "%DB_NAME%" "%PGPORT%" "%USERNAME%"
) else (
    echo Skipping Python Script.
)

:: Stop prompt
set /p STOP_PG="Would you like to stop your PostgreSQL Server? [Y/N]: "
if /i "%STOP_PG%"=="Y" (
    echo Stopping the PostgreSQL Server...
    call "%SCRIPT_DIR%cs166_server\stopPostgreDB.bat"
) else (
    echo Skipping Server Stop.
)

endlocal
pause