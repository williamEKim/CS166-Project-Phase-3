@echo off

set DB_NAME=%USERNAME%_eBay_DB
echo Creating database: %DB_NAME%

:: Use PGPORT if set, fallback to 5432
if "%PGPORT%"=="" set PGPORT=5432

:: Create the database
createdb -h localhost -p %PGPORT% %DB_NAME%

pg_ctl -D "%PGDATA%" status

:: Copy .dat files if any exist
if exist *.dat (
    echo Copying .dat files to %PGDATA%...
    copy *.dat "%PGDATA%\"
) else (
    echo No .dat files found, skipping copy.
)

:: Run SQL if file exists
if exist create_tables.sql (
    echo Running create_tables.sql on %DB_NAME%...
    psql -h localhost -p %PGPORT% -U %USERNAME% -d %DB_NAME% -f create_tables.sql
) else (
    echo create_tables.sql not found, skipping.
)

echo.
echo Done! To connect to your database:
echo   psql -h localhost -p %PGPORT% -U %USERNAME% -d %DB_NAME%